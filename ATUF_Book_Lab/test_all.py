"""Run a fresh lab and preserve truthful, per-stage acceptance evidence."""
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def stages():
    return [('unit', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']),
            ('install', ['bash', 'run_lab.sh', 'install']),
            ('direct', ['bash', 'run_lab.sh', 'direct']),
            ('pipeline', ['bash', 'run_lab.sh', 'pipeline']),
            ('kafka-lag', [sys.executable, 'check_runtime.py', 'lag']),
            ('telemetry', ['bash', 'run_lab.sh', 'telemetry']),
            ('redaction', [sys.executable, 'check_runtime.py', 'redaction']),
            ('retrieval', ['bash', 'run_lab.sh', 'retrieval']),
            ('recovery', ['bash', 'run_lab.sh', 'recovery']),
            ('recovery-lag', [sys.executable, 'check_runtime.py', 'lag']),
            ('final-verify', ['bash', 'run_lab.sh', 'verify', '40'])]


def write_report(folder, report):
    folder.mkdir(exist_ok=True)
    pending = folder / 'report.json.tmp'
    pending.write_text(json.dumps(report, indent=2) + '\n')
    pending.replace(folder / 'report.json')


def fresh_check(root, project):
    if any((root / n).exists() for n in ('events.ndjson', 'batch-b.ndjson')):
        raise RuntimeError('Existing batch files found. Use a fresh extraction; nothing was deleted.')
    result = subprocess.run(['docker', 'volume', 'ls', '-q', '--filter',
        'label=com.docker.compose.project=' + project], capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise RuntimeError('Docker is unavailable. Start Docker Desktop.\n' + result.stderr)
    if result.stdout.strip():
        raise RuntimeError('Project volumes already exist. Use a fresh extraction with its own project; nothing was deleted.')
    for port in (9200, 8080, 4318):
        with socket.socket() as sock:
            try:
                sock.bind(('127.0.0.1', port))
            except OSError as exc:
                raise RuntimeError(f'Port {port} is occupied. Stop the previous lab in Docker Desktop before starting a fresh run.') from exc


def execute_steps(folder, report, steps_to_run):
    for name, cmd in steps_to_run:
        print(f'RUN {name} — output: test-results/{name}.log', flush=True)
        item = {'name': name, 'status': 'RUNNING'}
        report['steps'].append(item)
        write_report(folder, report)
        try:
            with (folder / f'{name}.log').open('w') as log:
                p = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=1800)
            item.update(exit_code=p.returncode, status='PASS' if p.returncode == 0 else 'FAIL')
            if p.returncode:
                raise RuntimeError(f'{name} failed; inspect test-results/{name}.log')
        except BaseException as exc:
            item['status'] = 'FAIL'
            item['error'] = str(exc) or type(exc).__name__
            write_report(folder, report)
            raise
        write_report(folder, report)


def diagnostics(folder):
    commands = {
        'docker-version.log': ['docker', 'version'],
        'compose-version.log': ['docker', 'compose', 'version'],
        'images.log': ['docker', 'compose', 'images'],
        'services.log': ['docker', 'compose', 'logs', '--no-color', '--tail=200'],
    }
    for name, command in commands.items():
        try:
            info = subprocess.run(command, capture_output=True, text=True, timeout=30)
            (folder / name).write_text(info.stdout + info.stderr)
        except (OSError, subprocess.TimeoutExpired) as exc:
            (folder / name).write_text(str(exc))
    # Inspect only this project's configured images, not unrelated host images.
    try:
        names = subprocess.check_output(['docker', 'compose', 'config', '--images'], text=True, timeout=30).splitlines()
        if names:
            info = subprocess.run(['docker', 'image', 'inspect', *sorted(set(names)),
                '--format', '{{json .RepoTags}} {{json .RepoDigests}} {{.Id}} {{.Architecture}}'],
                capture_output=True, text=True, timeout=30)
            (folder / 'image-digests.log').write_text(info.stdout + info.stderr)
    except (OSError, subprocess.SubprocessError) as exc:
        (folder / 'image-digests.log').write_text(str(exc))


def main():
    os.chdir(ROOT)
    marker = ROOT / '.lab-project'
    os.environ.setdefault('COMPOSE_PROJECT_NAME', marker.read_text().strip() if marker.exists() else 'atuf-book-lab')
    folder = ROOT / 'test-results'
    if (folder / 'report.json').exists():
        print('An earlier report already exists. Preserve this run; use a fresh extraction for another complete test.')
        return 1
    report = {'status': 'RUNNING', 'release': (ROOT / 'RELEASE.txt').read_text().splitlines()[0],
              'python': sys.version, 'host': platform.platform(), 'architecture': platform.machine(),
              'project': os.environ['COMPOSE_PROJECT_NAME'], 'steps': []}
    try:
        if sys.flags.optimize:
            raise RuntimeError('Run without Python -O / PYTHONOPTIMIZE; verification assertions must be enabled.')
        if sys.version_info < (3, 11) or sys.prefix == sys.base_prefix:
            raise RuntimeError('Use Start_Lab.command on Mac, or activate a Python 3.11+ virtual environment.')
        fresh_check(ROOT, report['project'])
        execute_steps(folder, report, stages())
        report['status'] = 'PASS'
    except (Exception, KeyboardInterrupt) as exc:
        report['status'] = 'FAIL'
        report['error'] = str(exc) or type(exc).__name__
    finally:
        write_report(folder, report)
        diagnostics(folder)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
