import json
from urllib.request import Request, urlopen

properties = {
    "@timestamp": {"type": "date"},
    "event_time": {"type": "date"},
    "event_id": {"type": "keyword"},
    "event_type": {"type": "keyword"},
    "producer": {"type": "keyword"},
    "schema_version": {"type": "integer"},
    "order_id": {"type": "keyword"},
    "amount": {"type": "scaled_float", "scaling_factor": 100},
    "currency": {"type": "keyword"},
    "pipeline_version": {"type": "keyword"},
}
body = {
    "index_patterns": ["atuf-orders-*"],
    "priority": 500,
    "template": {
        "settings": {"number_of_shards": 1,
                     "number_of_replicas": 0},
        "mappings": {"dynamic": "strict",
                     "properties": properties},
    },
}
request = Request(
    "http://127.0.0.1:9200/_index_template/atuf-orders",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json"},
    method="PUT",
)
with urlopen(request, timeout=20) as response:
    print(response.read().decode())
