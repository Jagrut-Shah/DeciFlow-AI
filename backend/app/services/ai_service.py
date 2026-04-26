import logging
from typing import List, Optional
from app.infrastructure.llm.vertex_adapter import VertexAdapter
from app.schemas.v1.chat import ChatMessage

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, adapter: Optional[VertexAdapter] = None):
        self.adapter = adapter or VertexAdapter()

    async def get_chat_response(self, message: str, history: List[ChatMessage] = []) -> str:
        """
        Generates a response using the LLM adapter based on user message and history.
        """
        try:
            # Prepare context from history if needed
            context = ""
            if history:
                context = "Previous conversation history:\n"
                for msg in history:
                    context += f"{msg.role.capitalize()}: {msg.content}\n"
                context += "\nCurrent User Question: "
            
            prompt = f"{context}{message}"
            
            response = await self.adapter.generate_content(
                prompt=prompt,
                model_type="flash" # Use flash for fast chat responses
            )
            
            return response or "I'm sorry, I couldn't generate a response at this time."
            
        except Exception as e:
            logger.error(f"Error in AIService.get_chat_response: {str(e)}", exc_info=True)
            return f"I encountered an error: {str(e)}"
