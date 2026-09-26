"""Behavioral regression tests; simulated tools do not certify Docker integration."""
import contextlib
import http.server
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import shlex
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import launch_lab
import test_all


class ReleaseTests(unittest.TestCase):
    def shell_step(self, step, fail_validation=False):
        with tempfile.TemporaryDirectory(prefix='atuf test ') as temp:
            root = Path(temp)
            (root / step).write_text((ROOT / step).read_text())
            (root / 'events.ndjson').write_text(json.dumps({'order_id': 'order-1'}) + '\n')
            fake = root / 'docker'
            fake_code = root / '_fake_docker.py'
            fake_code.write_text('''
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with Path(os.environ['TOOL_LOG']).open('a') as f:
    f.write(json.dumps(args)+'\\n')
if 'exec' in args and '-T' not in args:
    raise SystemExit('TTY requested in captured execution')
if '--config.test_and_exit' in args:
    options=args[args.index('logstash')+1:]
    allowed={'--config.test_and_exit','--path.data'}
    if any(x.startswith('--') and x not in allowed for x in options):
        raise SystemExit('Unsupported Logstash option')
    if options[options.index('--path.data')+1] != '/tmp/logstash-validation':
        raise SystemExit('Validation uses live data')
    if os.environ.get('FAIL_VALIDATION') == '1': raise SystemExit(9)
''')
            fake.write_text('#!/bin/sh\nexec ' + shlex.quote(sys.executable) + ' ' + shlex.quote(str(fake_code)) + ' "$@"\n')
            fake.chmod(0o755)
            env = dict(os.environ, PATH=str(root) + os.pathsep + os.environ['PATH'],
                       TOOL_LOG=str(root / 'calls.jsonl'), FAIL_VALIDATION=str(int(fail_validation)))
            result = subprocess.run(['bash', str(root / step)], env=env, capture_output=True, text=True)
            calls = [json.loads(x) for x in (root / 'calls.jsonl').read_text().splitlines()]
            return result, calls

    def test_logstash_validation_isolated_and_supported(self):
        result, calls = self.shell_step('step_09.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[-1], ['compose', 'up', '-d', 'logstash'])

    def test_validation_failure_prevents_service_start(self):
        result, calls = self.shell_step('step_09.sh', True)
        self.assertEqual(result.returncode, 9)
        self.assertEqual(len(calls), 2)

    def test_kafka_delivery_works_without_terminal(self):
        result, calls = self.shell_step('step_12.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(all('-T' in c for c in calls))

    def test_project_is_stable_per_extraction(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = launch_lab.project_name(root)
            self.assertEqual(first, launch_lab.project_name(root))
            self.assertRegex(first, r'^atuf-reader-[a-f0-9]{12}$')

    def test_corrupt_project_marker_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / '.lab-project').write_text('unrelated-production-project')
            with self.assertRaises(RuntimeError): launch_lab.project_name(root)

    def test_existing_data_never_deleted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'events.ndjson').write_text('retained')
            with self.assertRaises(RuntimeError): test_all.fresh_check(root, 'example')
            self.assertEqual((root / 'events.ndjson').read_text(), 'retained')

    def test_existing_volumes_refused(self):
        with tempfile.TemporaryDirectory() as temp, patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'volume\n', '')):
            with self.assertRaisesRegex(RuntimeError, 'volumes'): test_all.fresh_check(Path(temp), 'example')

    def test_port_collision_is_actionable(self):
        with tempfile.TemporaryDirectory() as temp, patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, '', '')), patch('socket.socket') as sock:
            sock.return_value.__enter__.return_value.bind.side_effect = OSError('occupied')
            with self.assertRaisesRegex(RuntimeError, 'Port 9200'): test_all.fresh_check(Path(temp), 'example')

    def test_runner_stops_and_records_failed_stage(self):
        with tempfile.TemporaryDirectory() as temp, patch('subprocess.run', side_effect=[subprocess.CompletedProcess([], 0), subprocess.CompletedProcess([], 7)]) as run:
            report = {'status': 'RUNNING', 'steps': []}
            with self.assertRaisesRegex(RuntimeError, 'second failed'):
                test_all.execute_steps(Path(temp), report, [('first', ['first']), ('second', ['second']), ('third', ['third'])])
            self.assertEqual(run.call_count, 2)
            saved = json.loads((Path(temp) / 'report.json').read_text())
            self.assertEqual([s['status'] for s in saved['steps']], ['PASS', 'FAIL'])

    def test_runner_records_timeout_as_failure(self):
        with tempfile.TemporaryDirectory() as temp, patch('subprocess.run', side_effect=subprocess.TimeoutExpired('test', 1)):
            report = {'status': 'RUNNING', 'steps': []}
            with self.assertRaises(subprocess.TimeoutExpired):
                test_all.execute_steps(Path(temp), report, [('timeout', ['test'])])
            self.assertEqual(report['steps'][0]['status'], 'FAIL')

    def test_real_http_disconnect_is_retried(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            attempts = 0
            def do_POST(self):
                type(self).attempts += 1
                self.rfile.read(int(self.headers['Content-Length']))
                if type(self).attempts == 1:
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.connection.close()
                    return
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"partialSuccess": {}}')
            def log_message(self, *args): pass
        with http.server.HTTPServer(('127.0.0.1', 0), Handler) as server:
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            def local_request(url, **kwargs):
                return Request(f'http://127.0.0.1:{server.server_port}/v1/logs', **kwargs)
            try:
                with patch('urllib.request.Request', side_effect=local_request), patch('time.sleep'), contextlib.redirect_stdout(io.StringIO()):
                    runpy.run_path(str(ROOT / 'telemetry.py'), run_name='__main__')
                self.assertEqual(Handler.attempts, 2)
            finally:
                server.shutdown()
                worker.join(timeout=5)


if __name__ == '__main__': unittest.main()
