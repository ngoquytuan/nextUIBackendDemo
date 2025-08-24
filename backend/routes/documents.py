# routes/documents.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from models.schemas import DocumentInfo, DocumentUploadResponse
from services.document_service import document_service
from utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document"""
    try:
        logger.info(f"📤 Uploading: {file.filename}")
        result = await document_service.upload_document(file)
        logger.info(f"✅ Upload successful: {file.filename}")
        return result
    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[DocumentInfo])
async def list_documents():
    """Get list of uploaded documents"""
    try:
        documents = await document_service.list_documents()
        logger.info(f"📋 Listed {len(documents)} documents")
        return documents
    except Exception as e:
        logger.error(f"❌ List error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(document_id: str):
    """Get document details"""
    try:
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get document error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    try:
        success = await document_service.delete_document(document_id)
        if success:
            logger.info(f"🗑️ Document deleted: {document_id}")
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))