from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    content: str = ""
    kind: str = Field(default="document", min_length=1, max_length=40)
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    content: str | None = None
    kind: str | None = Field(default=None, min_length=1, max_length=40)
    tags: list[str] | None = None
    metadata: dict | None = None

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    content: str
    kind: str
    tags: list[str]
    metadata: dict
    created_at: datetime
    updated_at: datetime

class BulkCreate(BaseModel):
    documents: list[DocumentCreate] = Field(min_length=1, max_length=500)
