import json
import time
from http.client import RemoteDisconnected
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

record = {
    "timeUnixNano": str(time.time_ns()),
    "severityText": "INFO",
    "body": {"stringValue": "Synthetic pipeline check"},
    "attributes": [{"key": "enduser.email",
                    "value": {"stringValue": "test@example.invalid"}}],
}
payload = {"resourceLogs": [{
    "resource": {"attributes": [{"key": "service.name",
                  "value": {"stringValue": "lab-producer"}}]},
    "scopeLogs": [{"scope": {"name": "book-lab"},
                   "logRecords": [record]}],
}]}
request = Request("http://127.0.0.1:4318/v1/logs",
                  data=json.dumps(payload).encode(),
                  headers={"Content-Type": "application/json"})
for attempt in range(30):
    try:
        with urlopen(request, timeout=5) as response:
            result = json.load(response)
            partial = result.get("partialSuccess", {})
            rejected = int(partial.get("rejectedLogRecords", 0))
            if rejected:
                raise RuntimeError(f"Collector rejected {rejected} log records")
            print(response.status, result)
        break
    except HTTPError:
        raise
    except (URLError, RemoteDisconnected, ConnectionError, TimeoutError):
        if attempt == 29:
            raise
        time.sleep(2)
