# backend/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import logging
import uvicorn
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Backend API",
    description="Backend for RAG Document Chat System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://0.0.0.0:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    content: str
    role: str
    timestamp: datetime
    sources: List[dict] = []
    conversation_id: str

class DocumentInfo(BaseModel):
    id: str
    filename: str
    size: int
    upload_time: datetime
    status: str
    type: str

# In-memory storage (for demo)
conversations = {}
documents = {}

# Create upload directory
os.makedirs("uploads", exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "RAG Backend API is running! 🚀",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "endpoints": {
            "chat": "/api/v1/chat",
            "documents": "/api/v1/documents",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Chat endpoints
@app.post("/api/v1/chat", response_model=ChatResponse)
async def send_message(message_data: ChatMessage):
    """Send a chat message and get AI response"""
    try:
        logger.info(f"💬 New message: {message_data.message[:50]}...")
        
        conversation_id = message_data.conversation_id or str(uuid.uuid4())
        
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Add user message
        user_msg = {
            "id": str(uuid.uuid4()),
            "content": message_data.message,
            "role": "user",
            "timestamp": datetime.now()
        }
        conversations[conversation_id].append(user_msg)
        
        # Generate AI response
        ai_content = generate_demo_response(message_data.message)
        
        response = ChatResponse(
            id=str(uuid.uuid4()),
            content=ai_content,
            role="assistant", 
            timestamp=datetime.now(),
            conversation_id=conversation_id,
            sources=[
                {
                    "id": "demo_doc",
                    "filename": "sample_document.pdf",
                    "page": 1,
                    "relevance_score": 0.85
                }
            ]
        )
        
        # Add to conversation
        conversations[conversation_id].append(response.dict())
        
        logger.info(f"✅ Response generated: {len(ai_content)} chars")
        return response
        
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_demo_response(message: str) -> str:
    """Generate demo AI responses"""
    message_lower = message.lower()
    
    if "hello" in message_lower or "hi" in message_lower:
        return "Hello! 👋 I'm your RAG assistant. I can help you with questions about your uploaded documents. What would you like to know?"
        
    elif "document" in message_lower or "upload" in message_lower:
        return "I can see you're interested in documents! 📄 You can upload files using the upload button in the sidebar. I support PDF, TXT, DOCX, and MD files. Once uploaded, I can answer questions about their content."
        
    elif "what" in message_lower and "?" in message:
        return f"That's a great question! 🤔 You asked: '{message}'\n\nIn a full RAG system, I would:\n• 🔍 Search through your uploaded documents\n• 📄 Find relevant passages\n• 🤖 Generate an informed response\n• 📚 Provide source citations\n\nFor now, this is a demo response. Try uploading some documents first!"
        
    elif "how" in message_lower:
        return f"Great question about '{message}'! 💡\n\nHere's how I would help in a real RAG system:\n\n1. **Document Processing**: I analyze your uploaded files\n2. **Semantic Search**: I find relevant information\n3. **Context Assembly**: I gather the most relevant passages\n4. **Response Generation**: I create a comprehensive answer\n5. **Source Attribution**: I show you where the info came from\n\nTry uploading documents and asking specific questions!"
        
    elif len(message) > 50:
        return f"I see you have a detailed question! 📝\n\nYour message: '{message[:100]}...'\n\nThis is a comprehensive query that would benefit from document context. In a production RAG system, I would:\n\n• Parse your question for key concepts\n• Search relevant documents\n• Rank information by relevance\n• Synthesize a detailed answer\n\nUpload some documents related to your question for better results!"
        
    else:
        return f"Thanks for your message: '{message}' 💬\n\nI'm a RAG (Retrieval-Augmented Generation) assistant. I work best when you:\n\n• Upload documents I can reference\n• Ask specific questions about their content\n• Need help understanding complex topics\n\nTry asking something like:\n- 'What is this document about?'\n- 'Summarize the main points'\n- 'Explain [specific concept] from the document'\n\nWhat would you like to explore?"

@app.get("/api/v1/chat/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """Get chat history"""
    history = conversations.get(conversation_id, [])
    return {"conversation_id": conversation_id, "messages": history}

# Document endpoints  
@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document"""
    try:
        logger.info(f"📤 Uploading: {file.filename}")
        
        # Validate file
        allowed_extensions = ['.pdf', '.txt', '.docx', '.md']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not allowed. Allowed: {allowed_extensions}"
            )
        
        # Generate unique ID
        file_id = str(uuid.uuid4())
        content = await file.read()
        
        # Save file
        file_path = f"uploads/{file_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Store document info
        doc_info = DocumentInfo(
            id=file_id,
            filename=file.filename,
            size=len(content),
            upload_time=datetime.now(),
            status="processed",
            type=file_ext.lstrip('.')
        )
        documents[file_id] = doc_info
        
        logger.info(f"✅ Uploaded: {file.filename} ({len(content)} bytes)")
        
        return {
            "id": file_id,
            "filename": file.filename,
            "message": f"Document '{file.filename}' uploaded successfully! 🎉",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/v1/documents", response_model=List[DocumentInfo])
async def list_documents():
    """Get list of documents"""
    docs = list(documents.values())
    logger.info(f"📋 Listed {len(docs)} documents")
    return docs

@app.delete("/api/v1/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_info = documents[document_id]
    
    # Delete file
    try:
        file_path = f"uploads/{document_id}_{doc_info.filename}"
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.warning(f"⚠️ Could not delete file: {e}")
    
    # Remove from memory
    del documents[document_id]
    
    logger.info(f"🗑️ Deleted: {doc_info.filename}")
    return {"message": f"Document '{doc_info.filename}' deleted successfully"}

if __name__ == "__main__":
    logger.info("🚀 Starting RAG Backend...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )