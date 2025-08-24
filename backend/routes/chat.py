# routes/chat.py
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatMessage, ChatResponse, ErrorResponse
from services.chat_service import chat_service
from utils.logger import get_logger
from datetime import datetime

router = APIRouter()
logger = get_logger(__name__)

@router.post("/", response_model=ChatResponse)
async def send_message(message_data: ChatMessage):
    """Send a chat message and get AI response"""
    try:
        logger.info(f"💬 New chat message: {message_data.message[:50]}...")
        
        response = await chat_service.process_message(
            message_data.message, 
            message_data.conversation_id
        )
        
        logger.info(f"✅ Response generated for conversation: {response.conversation_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """Get chat history for a conversation"""
    try:
        history = await chat_service.get_conversation_history(conversation_id)
        return {"conversation_id": conversation_id, "messages": history}
    except Exception as e:
        logger.error(f"❌ History error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{conversation_id}")
async def clear_chat_history(conversation_id: str):
    """Clear chat history"""
    try:
        success = await chat_service.clear_conversation(conversation_id)
        if success:
            return {"message": "Conversation cleared"}
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
    except Exception as e:
        logger.error(f"❌ Clear history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))