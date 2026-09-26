import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:9200"

def api(method, path, body=None):
    raw = None if body is None else json.dumps(body).encode()
    req = Request(BASE + path, data=raw, method=method,
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=20) as response:
        return json.load(response)

mapping = {"settings": {"number_of_replicas": 0}, "mappings": {
    "properties": {
        "document_id": {"type": "keyword"},
        "source_version": {"type": "keyword"},
        "acl_groups": {"type": "keyword"},
        "content": {"type": "text"},
        "vector": {"type": "dense_vector", "dims": 3,
                   "index": True, "similarity": "cosine"},
    }}}
try:
    api("PUT", "/atuf-knowledge-lab", mapping)
except HTTPError as exc:
    error = json.load(exc).get("error", {})
    if error.get("type") != "resource_already_exists_exception":
        raise

for key, text, acl, vector in [
    ("leave", "Request annual leave from your manager.",
     ["employees"], [1.0, 0.0, 0.0]),
    ("incident", "Page the incident commander.",
     ["engineering"], [0.0, 1.0, 0.0]),
]:
    api("PUT", f"/atuf-knowledge-lab/_doc/{key}#0".replace(
        "#", "%23") + "?refresh=wait_for", {
            "document_id": key, "source_version": "v1",
            "acl_groups": acl, "content": text, "vector": vector})

acl_filter = {"term": {"acl_groups": "employees"}}
lexical = {"query": {"bool": {
    "must": [{"match": {"content": "annual leave"}}],
    "filter": [acl_filter]}}}
vector_query = {"knn": {
    "field": "vector", "query_vector": [0.9, 0.1, 0.0],
    "k": 2, "num_candidates": 10, "filter": acl_filter}}
for query in [lexical, vector_query]:
    result = api("POST", "/atuf-knowledge-lab/_search", query)
    ids = [h["_id"] for h in result["hits"]["hits"]]
    assert ids == ["leave#0"], ids
    print(ids)

deleted = api("POST",
    "/atuf-knowledge-lab/_delete_by_query?refresh=true",
    {"query": {"term": {"document_id": "leave"}}})
assert not deleted.get("failures"), deleted
assert not deleted.get("timed_out", False), deleted
remaining = api("POST", "/atuf-knowledge-lab/_count",
    {"query": {"term": {"document_id": "leave"}}})
assert remaining["count"] == 0, remaining
result = api("POST", "/atuf-knowledge-lab/_search", vector_query)
assert result["hits"]["total"]["value"] == 0
print("Deletion verified by document ID and employees query")
