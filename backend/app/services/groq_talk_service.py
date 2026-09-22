import httpx
import json
import logging
from typing import Dict, Any
from app.core.config import settings
from app.schemas.talk import TalkRequest, TalkResponse

logger = logging.getLogger(__name__)

# Configurable Tone Engine Profiles
TONE_PROFILES = {
    "sad": {"tone": "gentle, patient, validating", "humour": "minimal", "length": "short-medium"},
    "angry": {"tone": "calm, direct, validating", "humour": "minimal unless clearly invited", "length": "short"},
    "fear": {"tone": "reassuring, grounded, calm", "humour": "minimal", "length": "short-medium"},
    "happy": {"tone": "warm, playful, energetic", "humour": "moderate when appropriate", "length": "medium"},
    "surprise": {"tone": "curious, conversational", "humour": "moderate", "length": "medium"},
    "neutral": {"tone": "natural, conversational", "humour": "light", "length": "medium"},
    "disgust": {"tone": "direct, grounded", "humour": "light only when appropriate", "length": "short-medium"},
}

class GroqTalkService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.system_prompt = (
            "You are the conversational companion inside MoodTunes. Your job is to respond naturally, "
            "respectfully, and comfortably to what the user says. You may adapt your tone using the supplied "
            "emotional signal, but you must never claim to know the user's true emotions. You are not a therapist, "
            "doctor, psychologist, or crisis counselor. Do not diagnose conditions or make clinical claims. "
            "Listen before advising. Do not turn every conversation into a music recommendation. "
            "Use light humour only when the user's tone and emotional context make it appropriate. "
            "Never make jokes about trauma, grief, self-harm, abuse, serious illness, or other sensitive distress. "
            "When the user appears frustrated or upset, acknowledge the frustration rather than immediately trying to cheer them up. "
            "When the user is playful, you may be playful. When the user wants practical advice, provide concise practical suggestions. "
            "When the user simply wants to vent, let them vent. Do not be excessively verbose. Do not pretend to be human. "
            "If the user expresses imminent self-harm or danger, respond seriously and encourage contacting emergency services "
            "or a trusted person and seeking immediate real-world help. Do not use humour in safety-critical situations."
        )

    def _build_context_prompt(self, request: TalkRequest) -> str:
        instructions = ""
        
        # Apply tone engine if emotion profile is available
        if request.emotion_profile:
            dominant = request.emotion_profile.get("dominant_emotion", "neutral")
            tone_rules = TONE_PROFILES.get(dominant, TONE_PROFILES["neutral"])
            
            instructions += (
                f"\n\n[EMOTIONAL SIGNAL DETECTED: {dominant}]\n"
                f"Apply these tonal guidelines to your response:\n"
                f"- Tone: {tone_rules['tone']}\n"
                f"- Humour allowed: {tone_rules['humour']}\n"
                f"- Response length: {tone_rules['length']}\n"
            )
            
        instructions += (
            f"\n\n[RESPONSE SCHEMA]\n"
            "Return ONLY valid JSON matching this schema:\n"
            "{\n"
            '  "message": "Your conversational response",\n'
            '  "tone": "gentle|neutral|playful|grounded",\n'
            '  "should_suggest_music": false,\n'
            '  "music_reason": "Reason for suggesting music, or empty if false",\n'
            '  "safety_level": "normal|caution|urgent"\n'
            "}"
        )
        
        return instructions

    def _fallback_response(self, text: str = "I'm having trouble connecting right now, but I'm here.") -> TalkResponse:
        return TalkResponse(
            success=False,
            message=text,
            tone="neutral",
            should_suggest_music=False,
            music_reason="",
            safety_level="normal"
        )

    async def chat(self, request: TalkRequest) -> TalkResponse:
        if not self.api_key:
            logger.warning("GROQ_API_KEY not configured for Talk feature.")
            return self._fallback_response("The conversational engine is currently offline due to a missing API key.")

        # Build history (limit to last 6 messages to bound tokens)
        history = request.conversation[-6:] if request.conversation else []
        messages = [{"role": "system", "content": self.system_prompt + self._build_context_prompt(request)}]
        
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
            
        # Append current user message
        messages.append({"role": "user", "content": request.message})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.4,
            "max_tokens": 512
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                
                if response.status_code == 429:
                    logger.warning("Groq API rate limited.")
                    return self._fallback_response("I'm receiving too many messages right now. Let's pause for a moment.")
                    
                if response.status_code != 200:
                    logger.error(f"Groq API error {response.status_code}: {response.text}")
                    return self._fallback_response()

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                
                return TalkResponse(
                    success=True,
                    message=parsed.get("message", "I hear you."),
                    tone=parsed.get("tone", "neutral"),
                    should_suggest_music=parsed.get("should_suggest_music", False),
                    music_reason=parsed.get("music_reason", ""),
                    safety_level=parsed.get("safety_level", "normal")
                )
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode Groq JSON: {e}")
            return self._fallback_response()
        except Exception as e:
            logger.exception(f"Exception calling Groq API: {e}")
            return self._fallback_response()
