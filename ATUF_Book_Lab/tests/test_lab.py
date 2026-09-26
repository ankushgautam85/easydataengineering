import copy
import importlib.util
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError, HTTPError
from http.client import RemoteDisconnected

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import verify
import check_runtime


class LabTests(unittest.TestCase):
    def fixture(self, count=20):
        batches=['batch-a'] if count == 20 else ['batch-a','batch-b']
        rows=[{'_source':{'event_id':f'{b}-{i:03d}', 'order_id':f'{b}-order-{i:03d}',
                         'amount':20+i,'currency':'USD','pipeline_version':'lab-v1'}}
              for b in batches for i in range(20)]
        return {'hits':{'total':{'value':count},'hits':rows},'_shards':{'failed':0}}

    def test_control_totals(self):
        for n in [20,40]:
            self.assertEqual(verify.check(self.fixture(n),n,'lab-v1'),590*n/20)

    def test_invalid_outputs_fail(self):
        for field,value in [('amount',0),('currency','EUR'),('event_id','bad'),
                            ('pipeline_version','direct-v1'),('order_id','batch-a-order-001')]:
            with self.subTest(field=field):
                f=self.fixture();f['hits']['hits'][0]['_source'][field]=value
                with self.assertRaises(AssertionError):verify.check(f,20,'lab-v1')
        f=self.fixture();f['_shards']['failed']=1
        with self.assertRaises(AssertionError):verify.check(f,20,'lab-v1')
        f=self.fixture();f['timed_out']=True
        with self.assertRaises(AssertionError):verify.check(f,20,'lab-v1')

    def test_swapped_order_identities_fail(self):
        f = self.fixture()
        rows = f['hits']['hits']
        a, b = rows[0]['_source'], rows[1]['_source']
        a['order_id'], b['order_id'] = b['order_id'], a['order_id']
        with self.assertRaises(AssertionError): verify.check(f, 20, 'lab-v1')

    def test_generator_preserves_batch(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'events.ndjson'
            command=[sys.executable,str(ROOT/'events.py'),'batch-a',str(target)]
            subprocess.run(command,check=True)
            before=target.read_bytes()
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
            self.assertEqual(before,target.read_bytes())
            rows=[json.loads(s) for s in before.splitlines()]
            self.assertEqual(len(rows),20)
            self.assertEqual(sum(r['amount'] for r in rows),590)
            self.assertEqual(len({r['event_id'] for r in rows}),20)

    def telemetry(self, replies):
        class Response(io.BytesIO):status=200
        def reply(*a,**k):
            value=replies.pop(0)
            if isinstance(value,Exception):raise value
            return Response(json.dumps(value).encode())
        with patch('urllib.request.urlopen',side_effect=reply), patch('time.sleep'), patch('sys.stdout',new=io.StringIO()):
            runpy.run_path(str(ROOT/'telemetry.py'),run_name='__main__')

    def test_telemetry_success(self):self.telemetry([{}])
    def test_telemetry_rejection(self):
        with self.assertRaises(RuntimeError):
            self.telemetry([{'partialSuccess':{'rejectedLogRecords':'1'}}])
    def test_telemetry_retry(self):self.telemetry([URLError('fixture'),{}])
    def test_telemetry_disconnect_retry(self):
        self.telemetry([RemoteDisconnected('starting'), {}])
    def test_telemetry_timeout_retry(self):
        self.telemetry([TimeoutError('starting'), {}])
    def test_telemetry_retry_exhaustion(self):
        with self.assertRaises(RemoteDisconnected):
            self.telemetry([RemoteDisconnected('not ready') for _ in range(30)])
    def test_telemetry_http_error_fails(self):
        with self.assertRaises(HTTPError):
            self.telemetry([HTTPError('http://localhost', 400, 'bad request', {}, None)])
    def test_lag_parser(self):
        text='\n'.join(f'orders-lab atuf.orders.v3 {p} 7 7 0 consumer host client' for p in range(3))
        self.assertTrue(check_runtime.parse_lag(text))
        self.assertFalse(check_runtime.parse_lag(text.replace('7 7 0','6 7 1')))
        self.assertFalse(check_runtime.parse_lag('No active group'))
        self.assertFalse(check_runtime.parse_lag(text.splitlines()[0]))
        self.assertFalse(check_runtime.parse_lag(text.replace('atuf.orders.v3 2 ', 'atuf.orders.v3 9 ')))


if __name__ == '__main__':unittest.main()
