# services/document_service.py
import os
import uuid
import logging
import aiofiles
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from fastapi import UploadFile

from models.schemas import DocumentInfo, DocumentUploadResponse
from config import settings

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.documents: Dict[str, DocumentInfo] = {}
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        
    async def upload_document(self, file: UploadFile) -> DocumentUploadResponse:
        """Upload and process document"""
        
        # Validate file
        if not self._is_allowed_file(file.filename):
            raise ValueError(f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}")
            
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise ValueError(f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        safe_filename = f"{file_id}{file_extension}"
        file_path = self.upload_dir / safe_filename
        
        try:
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
                
            # Create document info
            doc_info = DocumentInfo(
                id=file_id,
                filename=file.filename,
                size=len(content),
                upload_time=datetime.now(),
                status="processed",
                type=file_extension.lstrip('.')
            )
            
            self.documents[file_id] = doc_info
            
            logger.info(f"📄 Document uploaded: {file.filename} ({len(content)} bytes)")
            
            # TODO: Process document for RAG (extract text, create embeddings, etc.)
            await self._process_document(file_path, doc_info)
            
            return DocumentUploadResponse(
                id=file_id,
                filename=file.filename,
                message="Document uploaded and processed successfully",
                status="success"
            )
            
        except Exception as e:
            # Cleanup on error
            if file_path.exists():
                file_path.unlink()
            logger.error(f"❌ Upload failed: {str(e)}")
            raise e
    
    async def _process_document(self, file_path: Path, doc_info: DocumentInfo):
        """Process document for RAG - placeholder for actual implementation"""
        
        # This is where you'd add:
        # 1. Text extraction (PDF, DOCX, etc.)
        # 2. Text chunking
        # 3. Embedding generation
        # 4. Vector store updates
        
        logger.info(f"🔄 Processing document: {doc_info.filename}")
        
        # Simulate processing
        import asyncio
        await asyncio.sleep(0.5)
        
        logger.info(f"✅ Document processed: {doc_info.filename}")
    
    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        if not filename:
            return False
        return Path(filename).suffix.lower() in settings.ALLOWED_EXTENSIONS
    
    async def list_documents(self) -> List[DocumentInfo]:
        """Get list of uploaded documents"""
        return list(self.documents.values())
    
    async def get_document(self, document_id: str) -> Optional[DocumentInfo]:
        """Get document by ID"""
        return self.documents.get(document_id)
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document"""
        if document_id not in self.documents:
            return False
            
        doc_info = self.documents[document_id]
        file_path = self.upload_dir / f"{document_id}{Path(doc_info.filename).suffix}"
        
        # Delete file
        if file_path.exists():
            file_path.unlink()
            
        # Remove from memory
        del self.documents[document_id]
        
        logger.info(f"🗑️ Document deleted: {doc_info.filename}")
        return True

# Global instance
document_service = DocumentService()