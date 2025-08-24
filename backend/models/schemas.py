# models/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    content: str
    role: MessageRole
    timestamp: datetime
    sources: Optional[List[dict]] = []
    conversation_id: str

class DocumentInfo(BaseModel):
    id: str
    filename: str
    size: int
    upload_time: datetime
    status: str
    type: str

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    message: str
    status: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime