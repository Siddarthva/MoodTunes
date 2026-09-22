import httpx
import json
import logging
from typing import Dict, Any
from app.core.config import settings
from app.schemas.mood_content import MoodContentRequest, MoodContentResponse, PostScanContentResponse

logger = logging.getLogger(__name__)

class GroqContentService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.system_prompt = (
            "You are the editorial voice of MoodTunes, a premium cinematic music application. "
            "Write short, intelligent, scientifically cautious copy for the homepage. "
            "Do not make deterministic claims (e.g., 'happy people always prefer upbeat music'). "
            "Do not use generic marketing clichés or chatbot tones. "
            "Return valid JSON matching the exact schema provided."
        )

    def get_fallback_content(self) -> Dict[str, str]:
        return {
            "headline": "Mood, translated into music.",
            "subheadline": "We read the emotional pattern in your expression and shape a music direction around it.",
            "micro_statement": "An intelligent approach to what you hear.",
            "mood_fact": "Emotion is a spectrum, not a single state. We use all seven dimensions of your expression.",
            "music_fact": "The same song can feel entirely different depending on where you are emotionally.",
            "talk_teaser": "Don't want to use the camera? You can just talk to us instead."
        }

    async def generate_home_content(self) -> Dict[str, str]:
        if not self.api_key:
            return self.get_fallback_content()

        schema_hint = {
            "headline": "string (short, impactful, e.g. Mood, translated into music.)",
            "subheadline": "string (1-2 sentences explaining the app)",
            "micro_statement": "string (very short editorial phrase)",
            "mood_fact": "string (1 sentence about emotional complexity)",
            "music_fact": "string (1 sentence about how music and emotion interact)",
            "talk_teaser": "string (1 sentence encouraging users to try the Talk feature)"
        }

        user_message = f"Generate fresh editorial copy. Output JSON strictly matching this schema: {json.dumps(schema_hint)}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.6,
            "max_tokens": 512
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    logger.error(f"Groq API error {response.status_code}: {response.text}")
                    return self.get_fallback_content()

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                
                # Validate the required keys exist
                for key in schema_hint.keys():
                    if key not in parsed:
                        return self.get_fallback_content()
                        
                return parsed
                
        except Exception as e:
            logger.exception(f"Exception calling Groq API: {e}")
            return self.get_fallback_content()

    def get_fallback_mood_content(self, dominant_emotion: str) -> MoodContentResponse:
        fallbacks = {
            "happy": ("A bright frequency.", "The moment feels lifted.", "celebrating the sound"),
            "sad": ("Some moments need a soundtrack before they need an explanation.", "A gentle energy leaning into reflection.", "finding quiet spaces"),
            "angry": ("Grounded and deliberate.", "A strong, controlled current of energy.", "harnessing the moment"),
            "fear": ("A steady anchor in the sound.", "There is a reassuring, calm tension here.", "finding steady ground"),
            "surprise": ("An unexpected rhythm.", "The moment leans into curiosity and open energy.", "discovering the next beat"),
            "neutral": ("A quiet center.", "A balanced, open state ready for direction.", "wherever the sound leads"),
            "disgust": ("Firm boundaries and grounded focus.", "A resilient, slightly guarded energy.", "cutting through the noise")
        }
        
        selected = fallbacks.get(dominant_emotion.lower(), fallbacks["neutral"])
        
        return MoodContentResponse(
            quote=selected[0],
            interpretation=selected[1],
            small_line=selected[2],
            success=False
        )

    async def generate_mood_content(self, request: MoodContentRequest) -> MoodContentResponse:
        if not self.api_key:
            return self.get_fallback_mood_content(request.dominant_emotion)

        tone_mapping = {
            "happy": "playful, bright, celebratory",
            "sad": "gentle, hopeful, never dismissive",
            "angry": "grounded, empowering, controlled",
            "fear": "calm, reassuring, steady",
            "surprise": "curious, energetic, playful",
            "neutral": "quietly intriguing, reflective",
            "disgust": "grounded, slightly dry or resilient"
        }
        
        tone = tone_mapping.get(request.dominant_emotion.lower(), "natural, conversational")
        
        prompt = (
            "You are the editorial voice of MoodTunes. "
            "Write a short quote, an interpretation, and a micro-line based on the following mood profile. "
            f"Dominant Emotion: {request.dominant_emotion}. Tone guidelines: {tone}. "
            f"Energy: {request.energy:.2f}. Valence: {request.valence:.2f}. "
            f"Intent: {request.intent or 'None'}. "
            "Do not diagnose. Use language like 'the moment feels' rather than 'you are'. "
            "Return valid JSON matching this schema:\n"
            "{\"quote\": \"string\", \"interpretation\": \"string\", \"small_line\": \"string\"}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.5,
            "max_tokens": 300
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    logger.error(f"Groq API error {response.status_code}: {response.text}")
                    return self.get_fallback_mood_content(request.dominant_emotion)

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                
                return MoodContentResponse(
                    quote=parsed.get("quote", "The sound meets the moment."),
                    interpretation=parsed.get("interpretation", "We found the feeling. Now we're finding the sound."),
                    small_line=parsed.get("small_line", "tuning into you"),
                    success=True
                )
                
        except Exception as e:
            logger.exception(f"Exception calling Groq API: {e}")
            return self.get_fallback_mood_content(request.dominant_emotion)

    def get_fallback_post_scan_content(self, dominant_emotion: str, emotional_profile: Dict[str, Any] = None) -> PostScanContentResponse:
        dom = dominant_emotion.lower() if dominant_emotion else "neutral"
        sec = ""
        
        if emotional_profile and "weighted_genres" in emotional_profile:
            # Check secondary emotions if available in profile
            probs = emotional_profile.get("probabilities", {})
            if isinstance(probs, dict):
                sorted_probs = sorted([(k.lower(), v) for k, v in probs.items() if k.lower() != dom], key=lambda x: x[1], reverse=True)
                if sorted_probs and sorted_probs[0][1] >= 10:
                    sec = sorted_probs[0][0]

        # Multi-Emotion Dynamic Combination Matrix Fallbacks
        combinations = {
            ("angry", "sad"): (
                "A little fire beneath the quiet.",
                "Your expression leans intense, but there is a quieter emotional current underneath it.",
                "Five tracks carrying a little weight.",
                "intense_melancholic"
            ),
            ("sad", "angry"): (
                "Hurt turning into intensity.",
                "The signal carries a strong, reflective weight with underlying intensity.",
                "Five tracks carrying a little weight.",
                "reflective_intense"
            ),
            ("happy", "surprise"): (
                "Something bright just happened.",
                "The spectrum is leaning energetic, positive, and a little unexpected.",
                "Five tracks for the unexpected energy.",
                "bright_playful"
            ),
            ("surprise", "happy"): (
                "An unexpected spark.",
                "Curiosity meets bright energy in a lifted moment.",
                "Five tracks for the unexpected energy.",
                "curious_bright"
            ),
            ("fear", "sad"): (
                "Take the volume down for a moment.",
                "The current signal leans quieter, introspective, and more reflective.",
                "Five tracks to slow the room down.",
                "quiet_grounding"
            ),
            ("sad", "fear"): (
                "A gentle anchor in the quiet.",
                "There is a quiet, cautious tension that calls for steady ground.",
                "Five tracks to slow the room down.",
                "gentle_reassuring"
            ),
            ("sad", "neutral"): (
                "A quiet kind of sound.",
                "Nothing needs to be rushed. The moment is calm, quiet, and reflective.",
                "Five tracks for a quieter moment.",
                "quiet_contemplative"
            ),
            ("happy", "neutral"): (
                "A calm kind of good.",
                "Nothing needs to be dramatic. The spectrum is simply leaning warm and positive.",
                "Five tracks for the good kind of calm.",
                "warm_positive"
            ),
            ("angry", "surprise"): (
                "There is some electricity here.",
                "The expression combines intensity with a strong element of unpredictability.",
                "Five tracks for the volatile energy.",
                "intense_unpredictable"
            ),
            ("fear", "neutral"): (
                "A steady beat to anchor the room.",
                "The signal is cautious and grounded, seeking a calm foundation.",
                "Five tracks for a steady, grounded rhythm.",
                "cautious_grounded"
            ),
        }

        combo_key = (dom, sec)
        if combo_key in combinations:
            h, r, m, t = combinations[combo_key]
            return PostScanContentResponse(
                quote=h,
                headline=h,
                reflection=r,
                music_intro=m,
                tone=t,
                visual_direction=t,
                success=False
            )

        # Single-Emotion Base Fallbacks
        single_fallbacks = {
            "happy": (
                "Some moments don't need fixing. They just need the right song.",
                "The music gives the moment a place to live. It doesn't have to be perfect, it just has to belong here.",
                "Five tracks for the lifted moment.",
                "bright_celebratory"
            ),
            "sad": (
                "You don't have to change the feeling. You can simply give it somewhere to go.",
                "Music doesn't fix it, but it holds it. The sound meets you exactly where you are.",
                "Five tracks for where you are.",
                "gentle_melancholic"
            ),
            "angry": (
                "Maybe this moment isn't asking for an answer. Maybe it's asking for a soundtrack.",
                "There's an energy here that needs expression. Let the music carry the weight for a while.",
                "Five tracks for the intensity.",
                "grounded_intense"
            ),
            "fear": (
                "A steady beat can be a place to anchor.",
                "When the moment feels uncertain, the right rhythm provides a foundation you can rely on.",
                "Five tracks to anchor the moment.",
                "steady_reassuring"
            ),
            "surprise": (
                "Curiosity is an open door.",
                "The feeling is shifting, leaning into what comes next. The sound follows that same sense of discovery.",
                "Five tracks for the unexpected.",
                "curious_exploratory"
            ),
            "neutral": (
                "A quiet moment is just space waiting to be filled.",
                "There is power in a balanced state. The music doesn't have to push; it just has to accompany you.",
                "Five tracks for a balanced state.",
                "calm_understated"
            ),
            "disgust": (
                "Clarity often sounds like a single, piercing note.",
                "When you know what doesn't belong, it becomes much easier to hear what does. Stay grounded in the sound.",
                "Five tracks cutting through the noise.",
                "grounded_resilient"
            )
        }

        h, r, m, t = single_fallbacks.get(dom, single_fallbacks["neutral"])

        return PostScanContentResponse(
            quote=h,
            headline=h,
            reflection=r,
            music_intro=m,
            tone=t,
            visual_direction=t,
            success=False
        )

    async def generate_post_scan_content(self, request: MoodContentRequest) -> PostScanContentResponse:
        if not self.api_key:
            return self.get_fallback_post_scan_content(request.dominant_emotion, request.emotional_profile)

        profile = request.emotional_profile or {}
        probs_summary = profile.get("probabilities", {})

        system_instruction = (
            "You are the MoodTunes emotional copy engine. "
            "Given a seven-class facial-expression distribution and derived music profile, "
            "generate a concise contextual reflection and music introduction. "
            "Treat the expression as a signal, not a definitive statement of the user's internal emotional state. "
            "Never diagnose. Never claim certainty. Respect mixed emotions. Avoid toxic positivity. Match the tone to the emotional mixture."
        )

        user_prompt = (
            f"Dominant Emotion: {request.dominant_emotion}\n"
            f"Emotion Distribution: {json.dumps(probs_summary)}\n"
            f"Energy: {request.energy:.2f}, Valence: {request.valence:.2f}, Tempo: {profile.get('tempo', 'medium')}\n"
            f"Intent: {request.intent or 'None'}\n\n"
            "Return valid JSON matching this exact schema:\n"
            "{\n"
            '  "headline": "short phrase <= 10 words",\n'
            '  "reflection": "1-2 sentences <= 25 words",\n'
            '  "music_intro": "short sentence <= 18 words",\n'
            '  "tone": "emotional tone descriptor",\n'
            '  "visual_direction": "theme descriptor"\n'
            "}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.5,
            "max_tokens": 300
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    return self.get_fallback_post_scan_content(request.dominant_emotion, request.emotional_profile)

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                
                headline = parsed.get("headline", "The sound meets the moment.")
                reflection = parsed.get("reflection", "You don't have to change the feeling. You can simply give it somewhere to go.")
                music_intro = parsed.get("music_intro", "Five tracks tuned to your emotional frequency.")
                tone = parsed.get("tone", "natural")
                v_dir = parsed.get("visual_direction", "balanced")

                return PostScanContentResponse(
                    quote=headline,
                    headline=headline,
                    reflection=reflection,
                    music_intro=music_intro,
                    tone=tone,
                    visual_direction=v_dir,
                    success=True
                )
                
        except Exception as e:
            logger.exception(f"Exception calling Groq API: {e}")
            return self.get_fallback_post_scan_content(request.dominant_emotion, request.emotional_profile)

    async def interpret_mood(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interprets a 7-class facial-expression spectrum without diagnosing.
        Generates contextual reflection, tone, music direction, and conversation opening.
        """
        emotion = request_data.get("emotion", {})
        dom = (emotion.get("dominant") or "neutral").lower()
        probs = emotion.get("probabilities", {})
        prof = request_data.get("emotional_profile", {}) or {}
        
        energy = prof.get("energy", 50.0)
        valence = prof.get("valence", 50.0)
        tempo = prof.get("tempo", "medium")

        # Compute summary string
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        top_two = [f"{k.upper()} ({v:.1f}%)" for k, v in sorted_probs[:2] if v > 5]
        summary_str = " with ".join(top_two) if top_two else f"{dom.upper()} spectrum"

        if not self.api_key:
            return self._fallback_interpretation(dom, summary_str, energy, valence, tempo)

        system_instruction = (
            "You are the emotional interpretation layer of MoodTunes. "
            "You receive a seven-class facial-expression spectrum produced by MoodTunes. "
            "Interpret the pattern as an expressive signal rather than a definitive statement about the user's internal emotional state. "
            "Acknowledge mixed emotions when meaningful. Generate a concise, thoughtful reflection that helps the user decide whether they want music or conversation. "
            "Never diagnose. Never claim certainty about what the user is actually feeling. Never assume the reason behind the expression. "
            "Do not force the user toward music or conversation. Do not generate song titles, artist names, fake URLs, medical claims, or toxic positivity."
        )

        user_prompt = (
            f"Dominant Emotion: {dom}\n"
            f"7-Class Distribution: {json.dumps(probs)}\n"
            f"Energy: {energy}, Valence: {valence}, Tempo: {tempo}\n\n"
            "Return valid JSON matching this exact schema:\n"
            "{\n"
            '  "headline": "Short 3-6 word contextual headline",\n'
            '  "reflection": "Concise 1-2 sentence non-diagnostic reflection",\n'
            '  "spectrum_summary": "Short 1-sentence summary of expression pattern",\n'
            '  "tone": "Comfort tone descriptor (e.g., quiet, safe, grounded, warm)",\n'
            '  "music_direction": {\n'
            '    "energy": number (0-100),\n'
            '    "valence": number (0-100),\n'
            '    "tempo": "slow|medium|fast",\n'
            '    "genres": ["string"],\n'
            '    "descriptors": ["string"]\n'
            '  },\n'
            '  "conversation_direction": {\n'
            '    "tone": "conversational tone descriptor",\n'
            '    "opening": "Gentle non-presumptuous conversation opening statement"\n'
            '  }\n'
            "}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.5,
            "max_tokens": 450
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.base_url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    content = json.loads(data["choices"][0]["message"]["content"])
                    content["success"] = True
                    return content
        except Exception as e:
            logger.exception(f"Error calling Groq for mood interpretation: {e}")

        return self._fallback_interpretation(dom, summary_str, energy, valence, tempo)

    def _fallback_interpretation(self, dom: str, summary_str: str, energy: float, valence: float, tempo: str) -> Dict[str, Any]:
        fallbacks = {
            "sad": ("A quiet moment in focus", "There seems to be a subtle weight to this expression. You don't have to change it—you can find sound or talk it through.", "gentle, patient, safe"),
            "angry": ("Grounded clarity", "Intensity carries energy. Whether you want to channel it into music or process it out loud, the space is yours.", "calm, direct, grounded"),
            "fear": ("A reassuring atmosphere", "Uncertainty asks for steady ground. Take a breath and choose the direction that feels safest.", "reassuring, quiet, steady"),
            "happy": ("An expansive moment", "Warmth naturally opens space. You can explore a vibrant soundtrack or talk freely.", "warm, open, energetic"),
            "surprise": ("Unexpected perspective", "A moment of discovery. Choose whether you'd like a soundtrack for the energy or a conversation.", "curious, open"),
            "neutral": ("A balanced, present state", "The canvas is clear. You can find music to set the tone or talk about whatever is on your mind.", "balanced, natural"),
            "disgust": ("Resilient focus", "Clear boundaries allow you to see what fits and what doesn't. Take your time choosing what comes next.", "direct, grounded")
        }
        h, r, t = fallbacks.get(dom, fallbacks["neutral"])
        return {
            "success": True,
            "headline": h,
            "reflection": r,
            "spectrum_summary": f"Expression pattern leaning toward {summary_str}",
            "tone": t,
            "music_direction": {
                "energy": energy,
                "valence": valence,
                "tempo": tempo,
                "genres": ["ambient", "indie", "lofi"],
                "descriptors": ["contextual", "atmospheric"]
            },
            "conversation_direction": {
                "tone": t,
                "opening": f"There seems to be a {t.split(',')[0]} shape to this moment. If you'd like, you can tell me what's on your mind."
            }
        }

