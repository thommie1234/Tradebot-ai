"""
Chat API routes - AI trading assistant
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from optifire.core.logger import logger


router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model."""
    question: str


class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str
    timestamp: str


@router.post("/ask", response_model=ChatResponse)
async def ask_question(message: ChatMessage, request: Request):
    """
    Ask the AI trading assistant a question.

    Examples:
    - "Waarom is NVDA gekocht?"
    - "Hoeveel winst heb ik gemaakt vandaag?"
    - "Welke kansen heb je gezien?"
    - "Controleer AAPL voor mij"
    """
    try:
        from datetime import datetime
        from optifire.services.trading_assistant import TradingAssistant

        # Get global state
        g = request.app.state.g

        # Create assistant
        assistant = TradingAssistant(
            db=g.db,
            broker=g.broker,
            openai=g.openai
        )

        # Ask question
        answer = await assistant.ask(message.question)

        return ChatResponse(
            answer=answer,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_chat_history(request: Request, limit: int = 50):
    """
    Get chat history (if we decide to store it in the database).

    For now, returns empty list - client-side storage only.
    """
    return []
