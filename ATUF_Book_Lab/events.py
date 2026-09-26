import json
import sys
from datetime import datetime, timezone
from decimal import Decimal

batch = sys.argv[1] if len(sys.argv) > 1 else "batch-a"
now = datetime.now(timezone.utc).isoformat()
# Exclusive creation preserves the original batch on a repeated command.
out = open(sys.argv[2], "x", encoding="utf-8") if len(sys.argv) > 2 else sys.stdout
for i in range(20):
    print(json.dumps({
        "event_id": f"{batch}-{i:03d}",
        "event_type": "order.created",
        "event_time": now,
        "producer": "lab-checkout",
        "schema_version": 3,
        "order_id": f"{batch}-order-{i:03d}",
        "amount": float(Decimal("20.00") + Decimal(i)),
        "currency": "USD",
    }), file=out)
if out is not sys.stdout:
    out.close()
