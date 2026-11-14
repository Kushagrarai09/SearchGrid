from app.schemas.document import DocumentCreate, DocumentUpdate

def test_document_create_validation():
    doc = DocumentCreate(title="Search basics", content="Inverted index", kind="article", tags=["search"])
    assert doc.title == "Search basics"
    assert doc.tags == ["search"]

def test_document_update_partial():
    update = DocumentUpdate(title="Updated").model_dump(exclude_unset=True)
    assert update == {"title": "Updated"}

def test_document_title_required():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        DocumentCreate(title="")
