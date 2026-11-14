from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import Document
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentOut, BulkCreate
from app.services.documents import create_document, update_document, remove_document
from app.services.search import search_documents

router = APIRouter()

@router.post("/documents", response_model=DocumentOut, status_code=201)
def create(data: DocumentCreate, db: Session = Depends(get_db)):
    return create_document(db, data.model_dump())

@router.post("/documents/bulk", status_code=202)
def bulk_create(data: BulkCreate, db: Session = Depends(get_db)):
    created = [create_document(db, item.model_dump()) for item in data.documents]
    return {"accepted": len(created), "ids": [doc.id for doc in created], "status": "queued_for_indexing"}

@router.get("/documents/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.scalar(select(Document).where(Document.id == document_id, Document.is_deleted.is_(False)))
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc

@router.put("/documents/{document_id}", response_model=DocumentOut)
def update(document_id: str, data: DocumentUpdate, db: Session = Depends(get_db)):
    doc = db.scalar(select(Document).where(Document.id == document_id, Document.is_deleted.is_(False)))
    if not doc:
        raise HTTPException(404, "Document not found")
    return update_document(db, doc, data.model_dump(exclude_unset=True))

@router.delete("/documents/{document_id}", status_code=204)
def delete(document_id: str, db: Session = Depends(get_db)):
    doc = db.scalar(select(Document).where(Document.id == document_id, Document.is_deleted.is_(False)))
    if not doc:
        raise HTTPException(404, "Document not found")
    remove_document(db, doc)

@router.get("/search")
def search(q: str = "", kind: str | None = None, tags: list[str] | None = Query(default=None),
           page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100),
           sort: str = Query("relevance", pattern="^(relevance|newest|oldest)$")):
    return search_documents(q, kind, tags, page, page_size, sort)
