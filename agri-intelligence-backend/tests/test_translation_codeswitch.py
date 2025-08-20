import asyncio
import pytest
from app.language_processing.translator import agricultural_translator

# Simple tests for code-switch and multi-language translation (identity if googletrans unavailable)

samples = [
    ("किसान को wheat price बताओ", "hi-en code-switch with English commodity"),
    ("आज मौसम कैसा है for wheat irrigation?", "Hindi-English mixed weather + irrigation"),
    ("पंजाब में मंडी cotton भाव क्या है?", "Hindi with English crop cotton"),
    ("ਮੈਂ wheat ਦੀ ਕੀਮਤ ਜਾਣਨੀ ਚਾਹੁੰਦਾ ਹਾਂ", "Punjabi + English crop")
]

@pytest.mark.parametrize("text,desc", samples)
def test_codeswitch_translation(text, desc):
    english, lang = agricultural_translator.query_to_english(text)
    assert isinstance(english, str) and len(english) > 0
    assert lang in ('hi','en','pa')  # detected language (may fallback to en)
    # Ensure English keywords preserved
    assert 'wheat' in english.lower() or 'cotton' in english.lower()

async def roundtrip(text):
    english, lang = agricultural_translator.query_to_english(text)
    back = agricultural_translator.response_to_original_language(english, lang)
    return lang, english, back

@pytest.mark.asyncio
async def test_roundtrip_idempotent_when_translator_unavailable():
    # If translator not available, english==original for non-english languages after preprocessing
    lang, english, back = await roundtrip(samples[0][0])
    if not getattr(agricultural_translator, 'translator', None):
        assert back == english
