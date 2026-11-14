import hashlib, json
from elasticsearch import Elasticsearch
from app.core.config import settings
from app.services.cache import cache_get, cache_set

es = Elasticsearch(settings.elasticsearch_url)
INDEX = "searchgrid-documents"

def ensure_index():
    if es.indices.exists(index=INDEX):
        return
    es.indices.create(index=INDEX, mappings={
        "properties": {
            "id": {"type": "keyword"},
            "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "content": {"type": "text"},
            "kind": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "metadata": {"type": "object", "enabled": True},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"}
        }
    }, settings={"number_of_shards": 1, "number_of_replicas": 0})

def index_document(doc: dict):
    ensure_index()
    es.index(index=INDEX, id=doc["id"], document=doc, refresh="wait_for")

def delete_document(document_id: str):
    ensure_index()
    es.delete(index=INDEX, id=document_id, ignore=[404], refresh="wait_for")

def search_documents(q: str, kind: str | None, tags: list[str] | None, page: int, page_size: int, sort: str):
    query_data = {"q": q, "kind": kind, "tags": tags, "page": page, "page_size": page_size, "sort": sort}
    cache_key = "search:" + hashlib.sha256(json.dumps(query_data, sort_keys=True).encode()).hexdigest()
    cached = cache_get(cache_key)
    if cached is not None:
        cached["cached"] = True
        return cached
    filters = []
    if kind:
        filters.append({"term": {"kind": kind}})
    if tags:
        filters.append({"terms": {"tags": tags}})
    must = ([{"multi_match": {"query": q, "fields": ["title^4", "content", "tags^2"],
                               "type": "best_fields", "fuzziness": "AUTO"}}] if q.strip()
            else [{"match_all": {}}])
    sort_clause = [{"_score": "desc"}] if sort == "relevance" and q.strip() else []
    if sort == "newest":
        sort_clause = [{"created_at": "desc"}]
    elif sort == "oldest":
        sort_clause = [{"created_at": "asc"}]
    response = es.search(index=INDEX, query={"bool": {"must": must, "filter": filters}},
                         from_=(page - 1) * page_size, size=page_size,
                         sort=sort_clause or None,
                         aggs={"kinds": {"terms": {"field": "kind"}},
                               "tags": {"terms": {"field": "tags", "size": 20}}})
    result = {"items": [{**hit["_source"], "score": hit.get("_score")} for hit in response["hits"]["hits"]],
              "total": response["hits"]["total"]["value"], "page": page, "page_size": page_size,
              "aggregations": {"kinds": response.get("aggregations", {}).get("kinds", {}).get("buckets", []),
                               "tags": response.get("aggregations", {}).get("tags", {}).get("buckets", [])},
              "cached": False}
    cache_set(cache_key, result)
    return result
