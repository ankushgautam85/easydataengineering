"""Acceptance checks for the book lab. No third-party Python packages."""
import argparse
import json
import math
import time
from urllib.request import Request, urlopen
from urllib.error import URLError


def api(path, body=None):
    req = Request('http://127.0.0.1:9200' + path,
                  data=None if body is None else json.dumps(body).encode(),
                  headers={'Content-Type': 'application/json'})
    with urlopen(req, timeout=10) as response:
        return json.load(response)


def check(result, expected, pipeline):
    assert result.get('_shards', {}).get('failed', 0) == 0, result
    assert not result.get('timed_out', False), result
    hits = result['hits']['hits']
    assert result['hits']['total']['value'] == expected, result['hits']['total']
    assert len(hits) == expected, len(hits)
    rows = [h['_source'] for h in hits]
    assert len({r['event_id'] for r in rows}) == expected, 'Duplicate IDs'
    assert len({r['order_id'] for r in rows}) == expected, 'Duplicate orders'
    assert all(r['currency'] == 'USD' for r in rows), 'Unexpected currency'
    expected_ids = {f'{batch}-{i:03d}' for batch in
                    (['batch-a'] if expected == 20 else ['batch-a', 'batch-b'])
                    for i in range(20)}
    assert {r['event_id'] for r in rows} == expected_ids, 'Unexpected batch IDs'
    assert all(r['order_id'] == r['event_id'].rsplit('-', 1)[0] + '-order-' + r['event_id'].rsplit('-', 1)[1]
               for r in rows), 'Order/event identity mismatch'
    assert all(math.isclose(r['amount'], 20 + int(r['event_id'][-3:]))
               for r in rows), 'Unexpected event amount'
    assert all(r['pipeline_version'] == pipeline for r in rows), 'Route not complete'
    total = sum(r['amount'] for r in rows)
    assert math.isclose(total, expected / 20 * 590), total
    return total


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--count', type=int, choices=[20, 40], required=True)
    p.add_argument('--pipeline', choices=['direct-v1', 'lab-v1'], required=True)
    p.add_argument('--timeout', type=int, default=180)
    args = p.parse_args()
    deadline = time.monotonic() + args.timeout
    last = None
    while True:
        try:
            result = api('/atuf-orders-*/_search',
                         {'size': 100, 'track_total_hits': True,
                          'query': {'match_all': {}}})
            total = check(result, args.count, args.pipeline)
            print(f'PASS: {args.count} unique orders; USD {total:.2f}; {args.pipeline}')
            return
        except (AssertionError, URLError, ConnectionError, TimeoutError, KeyError, ValueError) as exc:
            last = exc
        if time.monotonic() >= deadline:
            raise SystemExit(f'FAIL: acceptance target not met: {last}')
        time.sleep(2)


if __name__ == '__main__':
    main()
