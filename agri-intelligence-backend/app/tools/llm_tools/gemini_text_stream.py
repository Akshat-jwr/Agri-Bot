"""Gemini text token streaming helper.

Uses google-genai client to stream incremental text tokens.
"""
import os
import logging
from typing import AsyncGenerator, Optional

try:
    from google import genai
except ImportError:
    genai = None  # defer error until use

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.0-flash-exp")

async def stream_gemini_text(prompt: str, system: Optional[str] = None) -> AsyncGenerator[str, None]:
    if genai is None:
        raise RuntimeError("google-genai not installed. Add google-genai to requirements.")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY") or os.getenv("google_ai_api_key")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY / GOOGLE_AI_API_KEY env var.")

    client = genai.Client(api_key=api_key)

    # SDK streaming shape may evolve; adapt if needed.
    cfg = {}
    if system:
        cfg["system_instruction"] = system

    try:
        session = client.aio.responses.stream(
            model=DEFAULT_MODEL,
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            config=cfg
        )
        async for event in session:
            # Token / text parts
            if getattr(event, "model_output", None):
                for part in event.model_output.parts:
                    text = getattr(part, "text", None)
                    if text:
                        yield text
            # (Optional) handle reasoning tokens, etc.
    except Exception as e:
        logger.error(f"Gemini streaming failed: {e}")
        raise
