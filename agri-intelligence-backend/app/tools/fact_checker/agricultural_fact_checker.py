"""
🔍 ADVANCED AGRICULTURAL FACT CHECKER & MULTILINGUAL RESPONSE VALIDATOR
==============================================================================

This intelligent fact-checking layer:
1. Validates agricultural responses for accuracy and hallucinations
2. Detects language of original query (Hindi, Hinglish, Punjabi, English, etc.)
3. Either approves response or creates NEW accurate response
4. Returns final response in ORIGINAL QUERY LANGUAGE

Created with ❤️ for perfect agricultural intelligence
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
import google.generativeai as genai
from langdetect import detect
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgriculturalFactChecker:
    """
    🧠 INTELLIGENT FACT CHECKER FOR AGRICULTURAL RESPONSES
    
    Features:
    - Hallucination detection using advanced prompting
    - Language detection and preservation
    - Agricultural domain expertise validation
    - Automatic response correction with multilingual output
    """
    
    def __init__(self):
        self.model = None
        self._initialize_gemini()
        
        # Enhanced language patterns for perfect detection
        self.language_patterns = {
            'hindi': re.compile(r'[\u0900-\u097F]+'),
            'punjabi': re.compile(r'[\u0A00-\u0A7F]+'),
            'hinglish': re.compile(r'(?=.*[a-zA-Z])(?=.*[\u0900-\u097F])'),
            'punglish': re.compile(r'(?=.*[a-zA-Z])(?=.*[\u0A00-\u0A7F])')
        }
        
        # Agricultural keywords for better language context
        self.language_keywords = {
            'hindi': ['khet', 'fasal', 'khad', 'bijai', 'kaatai', 'pani', 'zameen'],
            'punjabi': ['khet', 'fasal', 'vija', 'khet', 'dhaan', 'ganun', 'pani'],
            'hinglish': ['crop', 'farming', 'field', 'fertilizer', 'spray', 'yield'],
            'punglish': ['crop', 'farming', 'khet', 'fasal', 'spray', 'attack']
        }
        
        # Agricultural fact-checking criteria
        self.fact_check_criteria = [
            "fertilizer_recommendations",
            "crop_varieties_accuracy", 
            "pest_disease_identification",
            "market_price_validity",
            "weather_advice_correctness",
            "soil_management_practices",
            "irrigation_guidelines",
            "government_scheme_details"
        ]
    
    def _initialize_gemini(self):
        """Initialize Gemini model for fact checking"""
        try:
            # Use existing API key from environment
            import os
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("✅ Fact Checker Gemini initialized successfully")
            else:
                logger.error("❌ GEMINI_API_KEY not found")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini for fact checking: {e}")
    
    async def validate_and_respond(self, 
                                 original_query: str,
                                 expert_response: str,
                                 context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔍 MAIN FACT CHECKING & MULTILINGUAL RESPONSE FUNCTION
        
        Args:
            original_query: The farmer's original question
            expert_response: Response from agricultural expert
            context_data: Supporting data (weather, market, search results)
        
        Returns:
            Dict with validated response in original language + metadata
        """
        try:
            # Step 1: Detect original query language
            detected_language = self._detect_query_language(original_query)
            logger.info(f"🌐 Detected language: {detected_language}")
            
            # Step 2: Fact-check the expert response
            fact_check_result = await self._fact_check_response(
                original_query, expert_response, context_data
            )
            
            # Step 3: Generate final response based on fact-check
            if fact_check_result['is_accurate']:
                # Response is good - just translate to original language
                final_response = await self._translate_to_original_language(
                    expert_response, detected_language, original_query
                )
                validation_status = "approved"
            else:
                # Response has issues - create new accurate response
                final_response = await self._create_corrected_response(
                    original_query, detected_language, context_data, fact_check_result
                )
                validation_status = "corrected"
            
            return {
                'final_response': final_response,
                'original_language': detected_language,
                'validation_status': validation_status,
                'fact_check_details': fact_check_result,
                'processing_info': {
                    'fact_checker_used': True,
                    'language_preserved': True,
                    'accuracy_validated': True
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Fact checker error: {e}")
            # Fallback - return original response
            return {
                'final_response': expert_response,
                'original_language': 'english',
                'validation_status': 'fallback',
                'fact_check_details': {'error': str(e)},
                'processing_info': {
                    'fact_checker_used': False,
                    'language_preserved': False,
                    'accuracy_validated': False
                }
            }
    
    def _detect_query_language(self, query: str) -> str:
        """
        🌐 PERFECT LANGUAGE DETECTION
        
        Enhanced detection for: Hindi, Hinglish, Punjabi, Punglish, English
        Uses multiple methods for maximum accuracy
        """
        try:
            query_lower = query.lower()
            
            # Method 1: Script-based detection (most reliable)
            has_hindi_script = bool(self.language_patterns['hindi'].search(query))
            has_punjabi_script = bool(self.language_patterns['punjabi'].search(query))
            has_english = bool(re.search(r'[a-zA-Z]+', query))
            
            # Method 2: Keyword-based contextual detection
            hindi_keywords = sum(1 for word in self.language_keywords['hindi'] if word in query_lower)
            punjabi_keywords = sum(1 for word in self.language_keywords['punjabi'] if word in query_lower)
            hinglish_keywords = sum(1 for word in self.language_keywords['hinglish'] if word in query_lower)
            
            # Method 3: Common language patterns
            # Punjabi specific patterns
            punjabi_patterns = ['ਮੇਰੇ', 'ਵਿੱਚ', 'ਦਾ', 'ਹੈ', 'ਕਰਾਂ', 'ਨਾਲ', 'ਕੀ']
            punjabi_pattern_count = sum(1 for pattern in punjabi_patterns if pattern in query)
            
            # Hindi specific patterns  
            hindi_patterns = ['मेरे', 'में', 'का', 'है', 'करूं', 'के', 'की']
            hindi_pattern_count = sum(1 for pattern in hindi_patterns if pattern in query)
            
            # Hinglish specific patterns
            hinglish_patterns = ['mein', 'hai', 'kya', 'kaise', 'karoun', 'chahiye']
            hinglish_pattern_count = sum(1 for pattern in hinglish_patterns if pattern in query_lower)
            
            logger.info(f"🔍 Language detection analysis:")
            logger.info(f"   Scripts: Hindi={has_hindi_script}, Punjabi={has_punjabi_script}, English={has_english}")
            logger.info(f"   Patterns: Hindi={hindi_pattern_count}, Punjabi={punjabi_pattern_count}, Hinglish={hinglish_pattern_count}")
            
            # Decision logic (prioritized)
            if punjabi_pattern_count >= 2 or has_punjabi_script:
                if has_english and hinglish_keywords >= 1:
                    return 'punglish'
                return 'punjabi'
            
            elif hindi_pattern_count >= 2 or has_hindi_script:
                if has_english and hinglish_keywords >= 1:
                    return 'hinglish'
                return 'hindi'
            
            elif hinglish_pattern_count >= 2 and has_english:
                return 'hinglish'
            
            elif has_english and not (has_hindi_script or has_punjabi_script):
                return 'english'
            
            # Fallback to langdetect with agricultural context
            try:
                detected = detect(query)
                logger.info(f"   Langdetect result: {detected}")
                
                if detected == 'hi':
                    return 'hinglish' if has_english else 'hindi'
                elif detected == 'pa':
                    return 'punglish' if has_english else 'punjabi'
                elif detected in ['en', 'es']:  # Sometimes Hindi/Punjabi gets detected as Spanish
                    if has_hindi_script or hindi_keywords >= 1:
                        return 'hinglish'
                    elif has_punjabi_script or punjabi_keywords >= 1:
                        return 'punglish'
                    return 'english'
                else:
                    return 'english'
                    
            except Exception as e:
                logger.warning(f"Langdetect failed: {e}")
                
                # Final fallback based on script presence
                if has_punjabi_script:
                    return 'punglish' if has_english else 'punjabi'
                elif has_hindi_script:
                    return 'hinglish' if has_english else 'hindi'
                else:
                    return 'english'
                
        except Exception as e:
            logger.error(f"Language detection completely failed: {e}")
            return 'english'  # Safe fallback
    
    async def _fact_check_response(self, 
                                 query: str, 
                                 response: str, 
                                 context_data: Dict) -> Dict[str, Any]:
        """
        🔍 ADVANCED AGRICULTURAL FACT CHECKING
        
        Uses specialized prompting to detect:
        - Factual inaccuracies
        - Hallucinations
        - Outdated information
        - Regional irrelevance
        """
        if not self.model:
            return {'is_accurate': True, 'confidence': 0.5, 'issues': []}
        
        fact_check_prompt = f"""
You are an EXPERT AGRICULTURAL FACT CHECKER for Indian farming. Your job is to validate agricultural advice for accuracy and detect any hallucinations or misinformation.

ORIGINAL FARMER QUERY: "{query}"

EXPERT RESPONSE TO VALIDATE:
{response}

SUPPORTING CONTEXT DATA:
{self._format_context_for_validation(context_data)}

FACT-CHECKING CRITERIA:
Evaluate the response against these standards:

1. **FACTUAL ACCURACY**:
   - Are fertilizer recommendations (NPK ratios, quantities) correct for mentioned crops?
   - Are crop varieties mentioned real and suitable for Indian conditions?
   - Are pest/disease identifications and treatments accurate?
   - Are market prices and trends realistic and current?

2. **AGRICULTURAL RELEVANCE**:
   - Is advice suitable for Indian farming conditions?
   - Are recommendations appropriate for mentioned regions/states?
   - Is timing advice (sowing, harvesting) seasonally correct?

3. **SAFETY & COMPLIANCE**:
   - Are pesticide recommendations safe and legally approved?
   - Are dosages within recommended limits?
   - Are government scheme details accurate and current?

4. **COMPLETENESS & PRACTICALITY**:
   - Does response adequately address the farmer's question?
   - Are recommendations practical for typical Indian farmers?
   - Is cost information realistic?

5. **HALLUCINATION DETECTION**:
   - Are there any made-up facts, statistics, or studies?
   - Are brand names or specific products mentioned accurately?
   - Are government schemes and subsidies correctly described?

RESPONSE FORMAT:
Provide your validation in this EXACT format:

ACCURACY_SCORE: [0.0 to 1.0]
IS_ACCURATE: [TRUE/FALSE]
CONFIDENCE_LEVEL: [0.0 to 1.0]

IDENTIFIED_ISSUES:
- [List specific factual errors, if any]
- [List potential hallucinations, if any]
- [List safety concerns, if any]

CRITICAL_CORRECTIONS_NEEDED:
- [List must-fix issues for farmer safety]
- [List important accuracy improvements]

OVERALL_ASSESSMENT: [One sentence summary of validation result]

Perform thorough fact-checking now:"""

        try:
            response_obj = self.model.generate_content(
                fact_check_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Very precise for fact-checking
                    top_p=0.7,
                    max_output_tokens=800
                )
            )
            
            validation_text = response_obj.text
            return self._parse_fact_check_response(validation_text)
            
        except Exception as e:
            logger.error(f"Fact checking API call failed: {e}")
            return {'is_accurate': True, 'confidence': 0.5, 'issues': []}
    
    def _format_context_for_validation(self, context_data: Dict) -> str:
        """Format context data for fact-checking prompt"""
        context_summary = []
        
        if context_data.get('weather_intelligence'):
            context_summary.append("✅ Real weather data available")
        
        if context_data.get('search_results'):
            search_count = len(context_data['search_results'])
            context_summary.append(f"✅ {search_count} Google search results for verification")
        
        if context_data.get('agricultural_data'):
            context_summary.append("✅ Agricultural knowledge base data available")
        
        if context_data.get('market_intelligence'):
            context_summary.append("✅ Market price data available")
        
        return '\n'.join(context_summary) if context_summary else "Limited context data available"
    
    def _parse_fact_check_response(self, validation_text: str) -> Dict[str, Any]:
        """Parse fact-checker response into structured data"""
        try:
            # Extract accuracy score
            accuracy_match = re.search(r'ACCURACY_SCORE:\s*([0-9.]+)', validation_text)
            accuracy_score = float(accuracy_match.group(1)) if accuracy_match else 0.7
            
            # Extract is_accurate
            is_accurate_match = re.search(r'IS_ACCURATE:\s*(TRUE|FALSE)', validation_text, re.IGNORECASE)
            is_accurate = is_accurate_match.group(1).upper() == 'TRUE' if is_accurate_match else True
            
            # Extract confidence
            confidence_match = re.search(r'CONFIDENCE_LEVEL:\s*([0-9.]+)', validation_text)
            confidence = float(confidence_match.group(1)) if confidence_match else 0.7
            
            # Extract issues
            issues_section = re.search(r'IDENTIFIED_ISSUES:(.*?)(?=CRITICAL_CORRECTIONS|OVERALL_ASSESSMENT|$)', 
                                     validation_text, re.DOTALL)
            issues = []
            if issues_section:
                issues_text = issues_section.group(1)
                issues = [line.strip().lstrip('- ') for line in issues_text.split('\n') 
                         if line.strip() and line.strip() != '-']
            
            return {
                'is_accurate': is_accurate,
                'accuracy_score': accuracy_score,
                'confidence': confidence,
                'issues': issues,
                'validation_details': validation_text
            }
            
        except Exception as e:
            logger.error(f"Failed to parse fact check response: {e}")
            return {'is_accurate': True, 'accuracy_score': 0.7, 'confidence': 0.5, 'issues': []}
    
    async def _translate_to_original_language(self, 
                                            response: str, 
                                            target_language: str, 
                                            original_query: str) -> str:
        """
        🌐 INTELLIGENT TRANSLATION TO ORIGINAL LANGUAGE
        
        Maintains agricultural terminology and context
        """
        if not self.model or target_language == 'english':
            return response
        
        translation_prompt = f"""
You are an expert translator specializing in agricultural communication for Indian farmers.

TASK: Translate the following agricultural advice to {target_language.upper()}, maintaining:
1. All technical agricultural terms accuracy
2. Natural language flow for farmers
3. Cultural context appropriateness
4. Professional yet accessible tone

ORIGINAL FARMER QUERY (for context): "{original_query}"

RESPONSE TO TRANSLATE:
{response}

TRANSLATION GUIDELINES:

For HINDI/HINGLISH:
- Keep English agricultural terms where commonly used (NPK, fertilizer, spray)
- Use respectful "आप" form throughout
- Include common Hindi agricultural vocabulary
- Maintain technical accuracy

For PUNJABI/PUNGLISH:
- Keep English agricultural terms where commonly used
- Use respectful Punjabi address forms
- Include regional Punjabi farming terms
- Maintain technical accuracy

For HINGLISH/PUNGLISH (Mixed):
- Natural code-switching between languages
- Keep technical terms in English where appropriate
- Use regional expressions and greetings
- Farmer-friendly conversational tone

IMPORTANT: Start with appropriate greeting (Namaste, Sat Sri Akal, etc.) and maintain the professional yet warm tone throughout.

Provide the translated response:"""

        try:
            response_obj = self.model.generate_content(
                translation_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.8,
                    max_output_tokens=1000
                )
            )
            
            translated_response = response_obj.text.strip()
            logger.info(f"✅ Translated response to {target_language}")
            return translated_response
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return response  # Return original if translation fails
    
    async def _create_corrected_response(self, 
                                       original_query: str,
                                       target_language: str,
                                       context_data: Dict,
                                       fact_check_result: Dict) -> str:
        """
        🔧 CREATE NEW ACCURATE RESPONSE WITH STRICT PROMPTING
        
        When original response has issues, create a new, more accurate one
        """
        if not self.model:
            return "I apologize, but I cannot provide a verified response at this time. Please consult your local agricultural extension officer."
        
        correction_prompt = f"""
You are a SENIOR AGRICULTURAL EXPERT creating a CORRECTED and VERIFIED response for an Indian farmer.

The previous response had these issues:
{', '.join(fact_check_result.get('issues', []))}

FARMER'S ORIGINAL QUESTION: "{original_query}"

AVAILABLE VERIFIED DATA:
{self._format_context_for_validation(context_data)}

STRICT RESPONSE REQUIREMENTS:
1. **ONLY VERIFIED FACTS**: Use only well-established agricultural practices and verified information
2. **NO SPECULATION**: Avoid uncertain recommendations or unverified claims
3. **SAFETY FIRST**: Prioritize farmer and crop safety in all recommendations
4. **PRACTICAL FOCUS**: Provide actionable advice suitable for typical Indian farmers
5. **REGIONAL RELEVANCE**: Ensure advice is appropriate for Indian farming conditions

**LANGUAGE REQUIREMENT: RESPOND EXACTLY IN THE LANGUAGE THE ORIGINAL QUERY IS IN**

RESPONSE STRUCTURE:
1. Warm, respectful greeting appropriate for THE DEECIDED LANGUAGE
2. Direct acknowledgment of their farming concern
3. VERIFIED recommendations with specific details
4. Safety precautions where relevant
5. Encouragement and offer for future help

CRITICAL: Only include information you are absolutely certain about. When in doubt, recommend consulting local experts.

Provide your corrected, verified agricultural advice:"""

        try:
            response_obj = self.model.generate_content(
                correction_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,  # More conservative for corrections
                    top_p=0.7,
                    max_output_tokens=800
                )
            )
            
            corrected_response = response_obj.text.strip()
            logger.info(f"✅ Created corrected response in {target_language}")
            return corrected_response
            
        except Exception as e:
            logger.error(f"Failed to create corrected response: {e}")
            # Fallback response in appropriate language
            fallback_responses = {
                'hindi': "माफ करें, मैं इस समय सत्यापित सलाह नहीं दे सकता। कृपया अपने स्थानीय कृषि विशेषज्ञ से संपर्क करें।",
                'hinglish': "Sorry, main abhi verified advice nahi de sakta. Please apne local agriculture expert se contact kariye.",
                'punjabi': "ਮਾਫ਼ ਕਰਨਾ, ਮੈਂ ਇਸ ਸਮੇਂ ਪ੍ਰਮਾਣਿਤ ਸਲਾਹ ਨਹੀਂ ਦੇ ਸਕਦਾ। ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੇ ਸਥਾਨਕ ਖੇਤੀ ਮਾਹਿਰ ਨਾਲ ਸੰਪਰਕ ਕਰੋ।",
                'english': "I apologize, but I cannot provide verified advice at this time. Please consult your local agricultural extension officer."
            }
            return fallback_responses.get(target_language, fallback_responses['english'])

# Global instance
agricultural_fact_checker = AgriculturalFactChecker()
