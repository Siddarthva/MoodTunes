from fastapi import APIRouter, HTTPException
from app.schemas.talk import TalkRequest, TalkResponse, ErrorResponse
from app.services.groq_talk_service import GroqTalkService

router = APIRouter()
groq_talk_service = GroqTalkService()

@router.post("/talk", response_model=TalkResponse, responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}})
async def talk_endpoint(request: TalkRequest):
    try:
        # Pass the request to GroqTalkService
        response = await groq_talk_service.chat(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
