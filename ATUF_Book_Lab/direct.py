import json
from datetime import datetime, timezone
from urllib.parse import quote
from urllib.request import Request, urlopen

for line in open("events.ndjson", encoding="utf-8"):
    event = json.loads(line)
    instant = datetime.fromisoformat(
        event["event_time"].replace("Z", "+00:00"))
    day = instant.astimezone(timezone.utc).strftime("%Y.%m.%d")
    event["@timestamp"] = event["event_time"]
    event["pipeline_version"] = "direct-v1"
    identity = quote(event["event_id"], safe="")
    url = (f"http://127.0.0.1:9200/atuf-orders-{day}"
           f"/_doc/{identity}?refresh=wait_for")
    request = Request(url, data=json.dumps(event).encode(),
                      headers={"Content-Type": "application/json"},
                      method="PUT")
    with urlopen(request, timeout=20) as response:
        print(json.load(response)["result"])
