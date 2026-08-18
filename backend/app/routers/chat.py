"""AI Chat Router forwarding clinical queries to ai-core."""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.services.ai_agent_service import ai_agent_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["AI Clinical Chat Agent"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Clinical or privacy query from user")
    org_name: Optional[str] = Field("AIIMS New Delhi (Cardiology)", description="User's organization name")
    user_name: Optional[str] = Field("Dr. Priya Nair", description="User's display name")


class PrivacyGuaranteeResponse(BaseModel):
    epsilon_bound: str
    mechanism: str
    model_checkpoint: str
    zk_proof_hash: str


class ChatResponse(BaseModel):
    id: str
    sender: str = "assistant"
    content: str
    timestamp: str
    source: str
    privacy_guarantee: Optional[PrivacyGuaranteeResponse] = None


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_agent(payload: ChatRequest):
    """
    POST /chat:
    Receives user query, routes through ai-core (Ollama agent or fallback engine),
    and returns friendly clinical insights.
    """
    try:
        result = ai_agent_service.process_chat(
            prompt=payload.message,
            org_name=payload.org_name or "AIIMS New Delhi (Cardiology)",
            user_name=payload.user_name or "Dr. Priya Nair",
        )
        return result
    except Exception as e:
        logger.error(f"Error processing chat in ai-core: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Agent inference failed: {str(e)}",
        )
