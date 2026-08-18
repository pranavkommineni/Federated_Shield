"""Router for Privacy-Preserved AI Chat with ai-core integration."""

from typing import Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from app.services.ai_agent_service import ai_agent_service

router = APIRouter(prefix="/chat", tags=["AI Clinical Agent Chat"])


class ChatRequest(BaseModel):
    prompt: str = Field(..., description="User message to the AI agent")
    org_name: Optional[str] = Field("Hospital Alpha (Cardiology)", description="User's organization name")
    user_name: Optional[str] = Field("Dr. Sarah Connor", description="User's display name")


class PrivacyGuarantee(BaseModel):
    epsilon_bound: str
    mechanism: str
    model_checkpoint: str
    zk_proof_hash: str


class ChatResponse(BaseModel):
    id: str
    sender: str
    content: str
    timestamp: str
    source: Optional[str] = "federated_shield_core"
    privacy_guarantee: PrivacyGuarantee


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with Federated Shield AI Agent",
    description="Send a message to the AI Agent powered by ai-core (Ollama Qwen2.5 + FL Tool Registry).",
)
def send_chat_message(payload: ChatRequest) -> ChatResponse:
    """Process query through ai-core agent service with tool calling & privacy guarantees."""
    result = ai_agent_service.process_chat(
        prompt=payload.prompt,
        org_name=payload.org_name or "Hospital Alpha (Cardiology)",
        user_name=payload.user_name or "Dr. Sarah Connor",
    )
    return ChatResponse(**result)
