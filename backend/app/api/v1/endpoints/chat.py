import logging
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.v1.chat import ChatRequest, ChatResponse
from app.schemas.response import success_response, APIResponse
from app.services.ai_service import AIService

router = APIRouter()
logger = logging.getLogger(__name__)

def get_ai_service():
    return AIService()

@router.post("/", response_model=APIResponse)
async def chat(
    request: ChatRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Echo-less AI Chat endpoint. Receives a message and returns a real AI response.
    """
    logger.info(f"Received chat message: {request.message[:50]}...")
    
    response_text = await ai_service.get_chat_response(
        message=request.message,
        history=request.history or [],
        session_id=request.session_id
    )
    
    return success_response(
        data=ChatResponse(response=response_text),
        message="AI response generated successfully."
    )
