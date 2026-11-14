from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.models import Document, OutboxEvent
from app.services.cache import invalidate_search_cache

def serialize(doc: Document) -> dict:
    return {"id": doc.id, "title": doc.title, "content": doc.content, "kind": doc.kind,
            "tags": doc.tags or [], "metadata": doc.metadata_json or {},
            "created_at": doc.created_at.isoformat(), "updated_at": doc.updated_at.isoformat()}

def add_event(db: Session, doc: Document, event_type: str):
    db.add(OutboxEvent(aggregate_id=doc.id, event_type=event_type, payload=serialize(doc)))

def create_document(db: Session, data: dict):
    doc = Document(title=data["title"], content=data.get("content", ""), kind=data.get("kind", "document"),
                   tags=data.get("tags", []), metadata_json=data.get("metadata", {}))
    db.add(doc)
    db.flush()
    add_event(db, doc, "document.upsert")
    db.commit()
    db.refresh(doc)
    invalidate_search_cache()
    return doc

def update_document(db: Session, doc: Document, data: dict):
    mapping = {"title": "title", "content": "content", "kind": "kind", "tags": "tags", "metadata": "metadata_json"}
    for key, value in data.items():
        if key in mapping and value is not None:
            setattr(doc, mapping[key], value)
    doc.updated_at = datetime.now(timezone.utc)
    add_event(db, doc, "document.upsert")
    db.commit()
    db.refresh(doc)
    invalidate_search_cache()
    return doc

def remove_document(db: Session, doc: Document):
    doc.is_deleted = True
    doc.updated_at = datetime.now(timezone.utc)
    db.add(OutboxEvent(aggregate_id=doc.id, event_type="document.delete", payload={"id": doc.id}))
    db.commit()
    invalidate_search_cache()
