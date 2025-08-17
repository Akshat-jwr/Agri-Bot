"""
Agricultural Language Processing Module
Handles multilingual farmer queries with code-switching support
Optimized for Hindi-English, Punjabi-English, and 12+ Indian languages
"""
import re
import logging
from typing import Tuple, Optional, Dict, List
from langdetect import detect, DetectorFactory
from googletrans import Translator
from transformers import pipeline
import json
from functools import lru_cache

# Set seed for consistent language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class AgriculturalTranslator:
    def __init__(self):
        self.translator = Translator()
        self.model_cache = {}
        
        # Agricultural terminology mapping for better translation
        self.agricultural_terms = {
            'hi': {  # Hindi
                'किसान': 'farmer', 'फसल': 'crop', 'खेत': 'field',
                'सिंचाई': 'irrigation', 'उर्वरक': 'fertilizer', 'बीज': 'seed',
                'मौसम': 'weather', 'बारिश': 'rainfall', 'धान': 'rice',
                'गेहूं': 'wheat', 'मक्का': 'maize', 'कपास': 'cotton',
                'चना': 'chickpea', 'मूंग': 'moong', 'उड़द': 'urad',
                'खरीफ': 'kharif', 'रबी': 'rabi', 'जायद': 'zaid',
                'मंडी': 'mandi', 'दाम': 'price', 'योजना': 'scheme',
                'सब्सिडी': 'subsidy', 'ऋण': 'loan', 'बीमा': 'insurance'
            },
            'pa': {  # Punjabi  
                'ਕਿਸਾਨ': 'farmer', 'ਫਸਲ': 'crop', 'ਖੇਤ': 'field',
                'ਸਿੰਚਾਈ': 'irrigation', 'ਖਾਦ': 'fertilizer', 'ਬੀਜ': 'seed',
                'ਮੌਸਮ': 'weather', 'ਮੀਂਹ': 'rainfall', 'ਧਾਨ': 'rice',
                'ਕਣਕ': 'wheat', 'ਮੱਕੀ': 'maize', 'ਕਪਾਹ': 'cotton'
            },
            'gu': {  # Gujarati
                'ખેતી': 'farming', 'પાક': 'crop', 'ખેતર': 'field',
                'પાણી': 'water', 'ખાતર': 'fertilizer', 'વરસાદ': 'rainfall'
            },
            'mr': {  # Marathi
                'शेतकरी': 'farmer', 'पीक': 'crop', 'शेत': 'field',
                'पाणी': 'water', 'खत': 'fertilizer', 'पाऊस': 'rainfall'
            }
        }
        
        # Language codes mapping
        self.lang_codes = {
            'hindi': 'hi', 'punjabi': 'pa', 'gujarati': 'gu', 'marathi': 'mr',
            'tamil': 'ta', 'telugu': 'te', 'kannada': 'kn', 'malayalam': 'ml',
            'bengali': 'bn', 'odia': 'or', 'assamese': 'as', 'urdu': 'ur'
        }

    @lru_cache(maxsize=1000)
    def detect_language(self, text: str) -> str:
        """
        Detect the primary language of the text
        Returns language code (e.g., 'hi', 'en', 'pa')
        """
        try:
            # Clean text for better detection
            clean_text = re.sub(r'[^\w\s]', ' ', text)
            clean_text = re.sub(r'\s+', ' ', clean_text.strip())
            
            if len(clean_text.split()) < 2:
                return 'en'  # Default to English for short text
                
            detected = detect(clean_text)
            
            # Map some common misdetections
            if detected == 'ne' and any(char in text for char in 'किकेकोकाकी'):
                return 'hi'  # Nepali often confused with Hindi
            if detected == 'ur' and any(char in text for char in 'किकेकोकाकी'):
                return 'hi'  # Urdu script vs Hindi
                
            return detected
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return 'en'  # Default fallback

    def _preprocess_agricultural_terms(self, text: str, source_lang: str) -> str:
        """Replace common agricultural terms for better translation"""
        if source_lang in self.agricultural_terms:
            for native_term, english_term in self.agricultural_terms[source_lang].items():
                text = text.replace(native_term, english_term)
        return text

    def _translate_with_context(self, text: str, src_lang: str, dest_lang: str) -> str:
        """Translate text with agricultural context awareness"""
        try:
            # Preprocess agricultural terms
            if src_lang != 'en':
                text = self._preprocess_agricultural_terms(text, src_lang)
            
            # Handle code-switching (mixed language)
            if src_lang != 'en' and self._has_english_words(text):
                result = self._translate_mixed_language(text, src_lang, dest_lang)
            else:
                # Simple translation
                result = self.translator.translate(text, src=src_lang, dest=dest_lang).text
            
            return result
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text

    def _has_english_words(self, text: str) -> bool:
        """Check if text contains English words (for code-switching detection)"""
        english_words = re.findall(r'\b[a-zA-Z]+\b', text)
        return len(english_words) > 0

    def _translate_mixed_language(self, text: str, src_lang: str, dest_lang: str) -> str:
        """Handle code-switched text (Hindi-English, Punjabi-English, etc.)"""
        tokens = re.findall(r'\w+|\s+|[^\w\s]', text, re.UNICODE)
        translated_tokens = []
        
        for token in tokens:
            if re.match(r'^\w+$', token):  # It's a word
                try:
                    # Detect if this specific token is English
                    token_lang = detect(token) if len(token) > 2 else src_lang
                    
                    if token_lang == 'en' or token.lower() in ['and', 'or', 'the', 'a', 'an', 'in', 'on', 'at']:
                        # Keep English words as-is when translating to English
                        translated_tokens.append(token if dest_lang == 'en' else self.translator.translate(token, src='en', dest=dest_lang).text)
                    else:
                        # Translate non-English words
                        if dest_lang == 'en':
                            translated_tokens.append(self.translator.translate(token, src=src_lang, dest='en').text)
                        else:
                            # First to English, then to target language
                            eng_token = self.translator.translate(token, src=src_lang, dest='en').text
                            translated_tokens.append(self.translator.translate(eng_token, src='en', dest=dest_lang).text)
                            
                except Exception:
                    translated_tokens.append(token)
            else:
                translated_tokens.append(token)  # Punctuation/spaces
        
        result = ''.join(translated_tokens)
        # Clean up spacing around punctuation
        result = re.sub(r'\s+([,.;:!?])', r'\1', result)
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result

    def query_to_english(self, farmer_query: str) -> Tuple[str, str]:
        """
        Convert farmer query to English for processing
        Returns: (english_query, detected_language)
        """
        try:
            # Detect original language
            original_lang = self.detect_language(farmer_query)
            
            logger.info(f"Detected language: {original_lang} for query: {farmer_query[:50]}...")
            
            # If already English, return as-is
            if original_lang == 'en':
                return farmer_query.strip(), 'en'
            
            # Translate to English
            english_query = self._translate_with_context(farmer_query, original_lang, 'en')
            
            # Post-process for agricultural context
            english_query = self._improve_agricultural_english(english_query)
            
            logger.info(f"Translated to English: {english_query}")
            
            return english_query.strip(), original_lang
            
        except Exception as e:
            logger.error(f"Query translation failed: {e}")
            return farmer_query, 'en'  # Fallback

    def response_to_original_language(self, english_response: str, target_language: str) -> str:
        """
        Translate English response back to farmer's original language
        """
        try:
            # If target is English, return as-is
            if target_language == 'en':
                return english_response
            
            # Translate response back to original language
            translated_response = self._translate_with_context(english_response, 'en', target_language)
            
            # Post-process for natural language flow
            translated_response = self._improve_response_fluency(translated_response, target_language)
            
            logger.info(f"Translated response to {target_language}: {translated_response[:100]}...")
            
            return translated_response
            
        except Exception as e:
            logger.error(f"Response translation failed: {e}")
            return english_response  # Fallback to English

    def _improve_agricultural_english(self, text: str) -> str:
        """Improve English translation for agricultural context"""
        # Common improvements for agricultural queries
        text = re.sub(r'\bfarm land\b', 'farmland', text, flags=re.IGNORECASE)
        text = re.sub(r'\brice crop\b', 'rice', text, flags=re.IGNORECASE)
        text = re.sub(r'\bwheat crop\b', 'wheat', text, flags=re.IGNORECASE)
        text = re.sub(r'\bwater irrigation\b', 'irrigation', text, flags=re.IGNORECASE)
        text = re.sub(r'\bmoney loan\b', 'loan', text, flags=re.IGNORECASE)
        
        # Fix common grammar issues
        text = re.sub(r'\bi need to know about\b', 'tell me about', text, flags=re.IGNORECASE)
        text = re.sub(r'\bwhat is the\b', 'what are the', text, flags=re.IGNORECASE)
        
        return text.strip()

    def _improve_response_fluency(self, text: str, target_lang: str) -> str:
        """Improve response fluency in target language"""
        # Add language-specific improvements here
        if target_lang == 'hi':
            # Add respectful Hindi terms
            text = re.sub(r'^([A-Z])', r'आपके लिए \1', text)
        
        return text

    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Return list of supported languages"""
        return [
            {'code': 'hi', 'name': 'Hindi', 'native': 'हिन्दी'},
            {'code': 'pa', 'name': 'Punjabi', 'native': 'ਪੰਜਾਬੀ'},
            {'code': 'gu', 'name': 'Gujarati', 'native': 'ગુજરાતી'},
            {'code': 'mr', 'name': 'Marathi', 'native': 'मराठी'},
            {'code': 'ta', 'name': 'Tamil', 'native': 'தமிழ்'},
            {'code': 'te', 'name': 'Telugu', 'native': 'తెలుగు'},
            {'code': 'kn', 'name': 'Kannada', 'native': 'ಕನ್ನಡ'},
            {'code': 'ml', 'name': 'Malayalam', 'native': 'മലയാളം'},
            {'code': 'bn', 'name': 'Bengali', 'native': 'বাংলা'},
            {'code': 'or', 'name': 'Odia', 'native': 'ଓଡ଼ିଆ'},
            {'code': 'as', 'name': 'Assamese', 'native': 'অসমীয়া'},
            {'code': 'ur', 'name': 'Urdu', 'native': 'اردو'},
            {'code': 'en', 'name': 'English', 'native': 'English'}
        ]

# Global instance
agricultural_translator = AgriculturalTranslator()
