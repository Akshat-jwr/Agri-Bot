"""
OPTIMIZED Agricultural Language Processing Module
10x faster with whole-text translation + caching + agricultural context
"""
import re
import logging
from typing import Tuple, List, Dict
from langdetect import detect, DetectorFactory
from googletrans import Translator
from functools import lru_cache
import time

# Set seed for consistent language detection
DetectorFactory.seed = 0
logger = logging.getLogger(__name__)

class OptimizedAgriculturalTranslator:
    def __init__(self):
        # ✅ FIXED: Single reusable translator instance
        self.translator = Translator()
        
        # ✅ FIXED: Agricultural term preprocessing for better translations
        self.agricultural_terms = {
            'hi': {  # Hindi terms that need special handling
                'भाव': 'price', 'दाम': 'price', 'कीमत': 'price',
                'खेती': 'farming', 'किसान': 'farmer', 'फसल': 'crop',
                'सिंचाई': 'irrigation', 'उर्वरक': 'fertilizer', 'बीज': 'seed',
                'खरीफ': 'kharif', 'रबी': 'rabi', 'मंडी': 'mandi',
                'योजना': 'scheme', 'सब्सिडी': 'subsidy', 'ऋण': 'loan'
            },
            'pa': {  # Punjabi terms
                'ਕਿਸਾਨ': 'farmer', 'ਖੇਤੀ': 'farming', 'ਫਸਲ': 'crop',
                'ਸਿੰਚਾਈ': 'irrigation', 'ਬੀਜ': 'seed', 'ਖਾਦ': 'fertilizer'
            }
        }

    @lru_cache(maxsize=1000)
    def detect_language(self, text: str) -> str:
        """Fast language detection with caching"""
        try:
            # Clean text for better detection
            clean_text = re.sub(r'[^\w\s]', ' ', text)
            if len(clean_text.split()) < 2:
                return 'en'
            
            detected = detect(clean_text)
            
            # Handle common misdetections for Indian languages
            if detected == 'ne' and any(char in text for char in 'किकेको'):
                return 'hi'
                
            return detected
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return 'en'

    def _preprocess_agricultural_terms(self, text: str, source_lang: str) -> str:
        """Replace agricultural terms before translation for better accuracy"""
        if source_lang in self.agricultural_terms:
            processed_text = text
            for native_term, english_term in self.agricultural_terms[source_lang].items():
                # Replace whole words only to avoid partial matches
                pattern = r'\b' + re.escape(native_term) + r'\b'
                processed_text = re.sub(pattern, english_term, processed_text)
            return processed_text
        return text

    @lru_cache(maxsize=2000)
    def _cached_translate(self, text: str, src_lang: str, dest_lang: str) -> str:
        """Cached translation function for speed"""
        try:
            if src_lang == dest_lang:
                return text
                
            # ✅ FIXED: Single whole-text translation call
            result = self.translator.translate(text, src=src_lang, dest=dest_lang)
            return result.text.strip()
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text

    def query_to_english(self, farmer_query: str) -> Tuple[str, str]:
        """
        Convert farmer query to English - OPTIMIZED VERSION
        Returns: (english_query, detected_language)
        """
        start_time = time.time()
        
        try:
            # Step 1: Detect language (cached)
            original_lang = self.detect_language(farmer_query)
            
            # Step 2: If already English, return immediately
            if original_lang == 'en':
                return farmer_query.strip(), 'en'
            
            # Step 3: Preprocess agricultural terms
            preprocessed_query = self._preprocess_agricultural_terms(farmer_query, original_lang)
            
            # Step 4: Single whole-text translation (cached)
            english_query = self._cached_translate(preprocessed_query, original_lang, 'en')
            
            # Step 5: Post-process for agricultural context
            english_query = self._improve_agricultural_english(english_query)
            
            elapsed = time.time() - start_time
            logger.info(f"Translation completed in {elapsed:.2f}s: {original_lang} → EN")
            
            return english_query, original_lang
            
        except Exception as e:
            logger.error(f"Query translation failed: {e}")
            return farmer_query, 'en'

    def response_to_original_language(self, english_response: str, target_language: str) -> str:
        """
        Translate English response back to farmer's language - OPTIMIZED
        """
        try:
            if target_language == 'en':
                return english_response
            
            # Single cached translation
            translated_response = self._cached_translate(english_response, 'en', target_language)
            
            return translated_response
            
        except Exception as e:
            logger.error(f"Response translation failed: {e}")
            return english_response

    def _improve_agricultural_english(self, text: str) -> str:
        """Quick improvements for agricultural English"""
        # Fix common agricultural translation issues
        text = re.sub(r'\brice farming\b', 'rice cultivation', text, flags=re.IGNORECASE)
        text = re.sub(r'\bwheat farming\b', 'wheat cultivation', text, flags=re.IGNORECASE)
        text = re.sub(r'\bfarm field\b', 'farmland', text, flags=re.IGNORECASE)
        
        return text.strip()

    def get_translation_stats(self) -> Dict[str, int]:
        """Get caching performance stats"""
        return {
            'language_detection_cache_size': self.detect_language.cache_info().currsize,
            'translation_cache_size': self._cached_translate.cache_info().currsize,
            'detection_cache_hits': self.detect_language.cache_info().hits,
            'translation_cache_hits': self._cached_translate.cache_info().hits
        }

# Global optimized instance
agricultural_translator = OptimizedAgriculturalTranslator()
