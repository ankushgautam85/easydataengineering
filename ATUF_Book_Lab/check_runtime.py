"""Runtime checks used by the integration suite."""
import os
from pathlib import Path
_root = Path(__file__).resolve().parent
os.chdir(_root)
_marker = _root / ".lab-project"
os.environ.setdefault("COMPOSE_PROJECT_NAME", _marker.read_text().strip() if _marker.exists() else "atuf-book-lab")
import re
import subprocess
import time


def parse_lag(text):
    rows = []
    for line in text.splitlines():
        cols = line.split()
        if len(cols) >= 6 and cols[0] == 'orders-lab' and cols[1] == 'atuf.orders.v3':
            rows.append((cols[2], cols[3], cols[4], cols[5]))
    if len(rows) != 3 or {r[0] for r in rows} != {'0', '1', '2'}:
        return False
    return all(all(v.isdigit() for v in r) and int(r[3]) == 0 and
               int(r[1]) == int(r[2]) for r in rows)


def lag():
    deadline = time.monotonic() + 180
    while True:
        p = subprocess.run(['docker','compose','exec','-T','kafka',
                            '/opt/kafka/bin/kafka-consumer-groups.sh',
                            '--bootstrap-server','kafka:9092','--describe',
                            '--group','orders-lab'],capture_output=True,text=True,timeout=30)
        if p.returncode == 0 and parse_lag(p.stdout):
            print('PASS: all three Kafka partitions have committed through their end offsets')
            return
        if time.monotonic() >= deadline:
            raise RuntimeError('Kafka lag check failed: '+p.stdout+p.stderr)
        time.sleep(2)


def redaction():
    deadline = time.monotonic() + 60
    while True:
        p = subprocess.run(['docker','compose','logs','--no-color','--tail=300','otel'],
                           capture_output=True,text=True,check=True,timeout=20)
        out = p.stdout+p.stderr
        if 'test@example.invalid' in out or 'enduser.email' in out:
            raise RuntimeError('Sensitive telemetry attribute found in Collector output')
        if 'Synthetic pipeline check' in out:
            print('PASS: synthetic log exported without the sensitive email attribute')
            return
        if time.monotonic() >= deadline:
            raise RuntimeError('Expected synthetic telemetry record not found')
        time.sleep(2)


if __name__ == '__main__':
    import sys
    {'lag':lag,'redaction':redaction}[sys.argv[1]]()
