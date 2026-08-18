"""Router for Customer / Doctor Privacy-Preserved Model Inference."""

from fastapi import APIRouter, status
from app.schemas.inference import InferenceRequest, InferenceResponse
from app.services.inference_engine import inference_engine

router = APIRouter(prefix="/inference", tags=["Customer Inference Playground"])


@router.post(
    "/predict",
    response_model=InferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Run privacy-preserved disease risk inference",
    description="Test predictions using the aggregated Global Federated Model without exposing patient raw training data.",
)
def run_model_inference(payload: InferenceRequest) -> InferenceResponse:
    """Execute risk prediction with explainable feature weights and DP guarantees."""
    result = inference_engine.predict_risk(
        age=payload.age,
        gender=payload.gender,
        blood_pressure_sys=payload.blood_pressure_sys,
        cholesterol=payload.cholesterol,
        glucose=payload.glucose,
        heart_rate=payload.heart_rate,
        smoking=payload.smoking,
    )
    return InferenceResponse(**result)
