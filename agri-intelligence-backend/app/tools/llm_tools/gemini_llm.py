"""
Gemini LLM Integration for Agricultural Intelligence

Provides intelligent response generation using Google's Gemini 2.5 Pro
with category-specific prompts and agricultural expertise

File: app/tools/llm_tools/gemini_llm.py
"""
import google.generativeai as genai
import logging
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiLLMTool:
    """
    Advanced Gemini 2.5 Pro integration with category-specific agricultural prompting
    """
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("✅ Gemini LLM initialized with agricultural expertise")
        else:
            logger.warning("gemini_api_key not set in .env. Using fallback responses.")
            self.model = None
        
        # Agricultural category-specific system prompts
        self.system_prompts = self._initialize_agricultural_prompts()
        
        # Category-based tool priorities
        self.category_tool_priorities = self._initialize_tool_priorities()
    
    def _initialize_agricultural_prompts(self) -> Dict[str, str]:
        """Initialize category-specific system prompts for agricultural intelligence"""
        return {
            'fertilizer_optimization': """You are a senior agricultural scientist with 25 years of experience in soil nutrition and fertilizer management in India. You specialize in:
- NPK fertilizer optimization for Indian crops
- Soil testing interpretation and recommendations
- Organic and chemical fertilizer integration
- State-specific fertilizer schedules for different crops
- Cost-effective fertilization strategies for small farmers

Always provide:
- Specific NPK ratios and quantities per hectare/acre
- Timing of fertilizer application (basal, top-dressing)
- Soil test-based recommendations
- Organic alternatives and their benefits
- Cost calculations and ROI for farmers
- Local fertilizer availability and brands""",

            'weather_impact': """You are an agricultural meteorologist and climate expert specializing in Indian farming systems. Your expertise includes:
- Weather pattern analysis for crop planning
- Climate-resilient farming practices
- Monsoon prediction and crop timing
- Extreme weather event management
- Seasonal crop calendars for different agro-climatic zones

Always provide:
- Weather-based farming recommendations
- Crop protection strategies for adverse weather
- Irrigation scheduling based on weather forecasts
- Seasonal planning advice
- Climate change adaptation techniques
- Regional weather pattern insights""",

            'crop_selection': """You are a crop scientist and plant breeder with expertise in:
- High-yielding variety recommendations for Indian conditions
- Crop rotation and intercropping systems
- Agro-climatic zone-specific crop selection
- Market-oriented crop planning
- Sustainable farming practices
- Traditional and modern crop varieties

Always provide:
- Specific variety names and their characteristics
- Yield expectations and market potential
- Soil and climate suitability analysis
- Crop calendar and growth stages
- Input requirements and profitability analysis
- Seed sources and certification details""",

            'pest_disease_management': """You are an entomologist and plant pathologist specializing in:
- Integrated Pest Management (IPM) for Indian crops
- Disease identification and management
- Biological control agents and their application
- Pesticide resistance management
- Organic pest control methods
- Economic threshold levels for pest control

Always provide:
- Accurate pest/disease identification
- IPM strategies with biological and chemical options
- Preventive measures and cultural practices
- Spray schedules and application techniques
- Resistance management strategies
- Cost-effective treatment options""",

            'yield_prediction': """You are an agricultural engineer and precision farming expert with focus on:
- Yield optimization techniques
- Precision agriculture tools and techniques
- Farm mechanization for productivity enhancement
- Input-output optimization
- Technology adoption in farming
- Data-driven farming decisions

Always provide:
- Specific yield targets and achievement strategies
- Technology recommendations for yield improvement
- Input optimization for maximum productivity
- Mechanization advice for efficiency
- Cost-benefit analysis of interventions
- Modern farming technique adoption""",

            'market_price_forecasting': """You are an agricultural economist and market analyst specializing in:
- Agricultural commodity market trends
- Price forecasting and market intelligence
- Value addition and post-harvest management
- Agricultural marketing strategies
- Government policy impact on prices
- Export-import dynamics in agriculture

Always provide:
- Current market price analysis and trends
- Price forecasting for the next 3-6 months
- Best selling strategies and timing
- Value addition opportunities
- Market linkage suggestions
- Policy impact on pricing""",

            'soil_health': """You are a soil scientist with expertise in:
- Soil health assessment and improvement
- Soil testing interpretation
- Organic matter management
- Micronutrient management
- Soil conservation practices
- Sustainable soil management

Always provide:
- Soil health indicators and improvement strategies
- Organic matter enhancement techniques
- Micronutrient deficiency corrections
- Soil conservation practices
- pH management and amelioration
- Long-term soil sustainability plans""",

            'irrigation_planning': """You are an irrigation engineer specializing in:
- Micro-irrigation systems design and implementation
- Water use efficiency in agriculture
- Crop water requirement calculations
- Irrigation scheduling and automation
- Drip and sprinkler system selection
- Water conservation techniques

Always provide:
- Irrigation system recommendations
- Water requirement calculations
- Irrigation scheduling based on crop and climate
- System design and cost estimation
- Water conservation strategies
- Maintenance and troubleshooting guides""",

            'government_schemes': """You are an agricultural extension officer with 30 years of experience in:
- Government agricultural schemes and subsidies
- Application procedures and documentation
- Eligibility criteria and benefits
- State and central government programs
- Financial assistance programs for farmers
- Agricultural insurance schemes

Always provide:
- Relevant scheme names and benefits
- Step-by-step application procedures
- Required documents and eligibility criteria
- Contact information for local offices
- Timeline for approvals and disbursements
- Tips for successful applications""",

            'seasonal_planning': """You are a farming systems specialist with expertise in:
- Seasonal crop planning and calendars
- Multi-cropping systems optimization
- Resource planning and allocation
- Farm enterprise planning
- Income diversification strategies
- Risk management in farming

Always provide:
- Season-wise crop planning recommendations
- Resource allocation and timing
- Multi-cropping opportunities
- Income optimization strategies
- Risk mitigation approaches
- Farm planning calendars""",

            'general_farming': """You are a general agricultural advisor with comprehensive knowledge of:
- Holistic farming approaches
- Sustainable agriculture practices
- Farm management principles
- Agricultural best practices
- Technology integration in farming
- Farmer welfare and development

Always provide:
- Comprehensive farming advice
- Best practice recommendations
- Technology adoption guidance
- Sustainable farming approaches
- Economic viability analysis
- Overall farm development strategies"""
        }
    
    def _initialize_tool_priorities(self) -> Dict[str, List[str]]:
        """Define which tools are most relevant for each category"""
        return {
            'fertilizer_optimization': ['semantic_search', 'sql_queries', 'real_yield_prediction'],
            'weather_impact': ['real_weather_apis', 'semantic_search', 'sql_queries'],
            'crop_selection': ['real_yield_prediction', 'semantic_search', 'sql_queries', 'real_weather_apis'],
            'pest_disease_management': ['semantic_search', 'real_weather_apis', 'google_search'],
            'yield_prediction': ['real_yield_prediction', 'sql_queries', 'real_weather_apis', 'semantic_search'],
            'market_price_forecasting': ['real_market_apis', 'sql_queries', 'google_search'],
            # Include weather to let price advice reflect short-term climatic impacts
            'market_price_forecasting': ['real_market_apis', 'real_weather_apis', 'sql_queries', 'google_search'],
            'soil_health': ['semantic_search', 'sql_queries', 'real_yield_prediction'],
            'irrigation_planning': ['real_weather_apis', 'semantic_search', 'sql_queries'],
            'government_schemes': ['government_apis', 'google_search', 'semantic_search'],
            'seasonal_planning': ['real_weather_apis', 'sql_queries', 'semantic_search', 'real_yield_prediction'],
            'general_farming': ['semantic_search', 'real_weather_apis', 'sql_queries']
        }
    
    async def generate_agricultural_response(self, 
                                           query: str,
                                           classification: Dict[str, Any],
                                           context_data: Dict[str, Any],
                                           farmer_context: Optional[Dict] = None) -> str:
        """
        Generate intelligent agricultural response using category-specific prompts
        
        Args:
            query: Original farmer question
            classification: Query classification results
            context_data: All gathered context (weather, market, search results, etc.)
            farmer_context: Optional farmer location/profile info
            
        Returns:
            Intelligent, contextual agricultural advice from domain expert
        """
        if not self.model:
            return self._generate_fallback_response(classification)
        
        try:
            category = classification.get('primary_category', 'general_farming')
            
            # Build category-specific expert prompt
            prompt = self._build_expert_agricultural_prompt(
                query, classification, context_data, farmer_context, category
            )
            
            logger.info(f"🤖 Calling Gemini with {category} expert persona...")
            
            # Generate response using Gemini with expert prompting
            response = await self._call_gemini_with_expert_prompt(prompt, category)
            
            logger.info(f"✅ Generated {len(response)} character expert response")
            return response
            
        except Exception as e:
            logger.error(f"❌ Gemini LLM error: {e}")
            return self._generate_fallback_response(classification)
    
    def _build_expert_agricultural_prompt(self, 
                                        query: str,
                                        classification: Dict[str, Any],
                                        context_data: Dict[str, Any],
                                        farmer_context: Optional[Dict],
                                        category: str) -> str:
        """Build comprehensive expert prompt with category-specific context"""
        
        # Get category-specific system prompt
        system_prompt = self.system_prompts.get(category, self.system_prompts['general_farming'])
        
        # Extract key context elements
        crops = classification.get('extracted_entities', {}).get('crops', [])
        locations = classification.get('extracted_entities', {}).get('locations', [])
        urgency = classification.get('urgency', 'medium')
        
        # Build context sections based on category priorities
        context_sections = self._build_prioritized_context(category, context_data)
        
        # Farmer profile context
        farmer_info = ""
        if farmer_context:
            farmer_info = f"""
FARMER PROFILE:
- Location: {farmer_context.get('location', 'Not specified')}
- Farm size: {farmer_context.get('farm_size', 'Not specified')}
- Experience: {farmer_context.get('experience', 'Not specified')}
- Crops grown: {farmer_context.get('crops', 'Not specified')}
"""
        
        # Build the comprehensive expert prompt
        prompt = f"""{system_prompt}

CURRENT CONSULTATION:
A farmer has approached you with this question: "{query}"

QUERY ANALYSIS:
- Primary concern: {category.replace('_', ' ').title()}
- Crops mentioned: {', '.join(crops) if crops else 'Not specified'}
- Location context: {', '.join(locations) if locations else 'General India'}
- Urgency level: {urgency}

{farmer_info}

AVAILABLE DATA & CONTEXT:
{context_sections}

EXPERT RESPONSE GUIDELINES:
1. Start with a warm, respectful greeting (use "Namaste" or "Namaskar")
2. Acknowledge their specific concern with empathy
3. Provide expert analysis based on the available data
4. Give specific, actionable recommendations with exact quantities/timing
5. Include relevant local context and best practices
6. Mention any risks or precautions
7. Suggest follow-up actions or consultations if needed
8. Use simple, farmer-friendly language while maintaining expertise
9. Include cost considerations and ROI where relevant
10. End with encouragement and availability for future questions

RESPONSE LENGTH: 300-500 words for comprehensive yet focused advice.

Please provide your expert agricultural consultation:"""

        return prompt
    
    def _build_prioritized_context(self, category: str, context_data: Dict[str, Any]) -> str:
        """Build context sections prioritized for the specific category"""
        
        context_sections = []
        priorities = self.category_tool_priorities.get(category, ['semantic_search', 'real_weather_apis'])
        
        # Weather context (high priority for weather_impact, irrigation, seasonal planning)
        if any(tool in priorities for tool in ['real_weather_apis']) and context_data.get('weather_intelligence'):
            weather = context_data['weather_intelligence']
            current = weather.get('current_conditions', {})
            if current:
                context_sections.append(f"""
CURRENT WEATHER CONDITIONS:
- Temperature: {current.get('temperature', 'N/A')}°C
- Humidity: {current.get('humidity', 'N/A')}%
- Weather: {current.get('weather_description', 'N/A')}
- Location: {current.get('location', 'N/A')}
- Agricultural advisories: {', '.join(weather.get('agricultural_advisories', [])[:2])}""")
        
        # Google Search results (high priority for latest information)
        if context_data.get('search_results'):
            search_insights = []
            for i, result in enumerate(context_data['search_results'][:3], 1):
                search_insights.append(f"""
{i}. {result.get('title', 'No title')} (Source: {result.get('source', 'Unknown')})
   Summary: {result.get('snippet', 'No summary available')[:150]}...
   Relevance: {result.get('relevance_score', 0.5):.1f}/1.0""")
            
            context_sections.append(f"""
LATEST AGRICULTURAL INFORMATION (Google Search):
{''.join(search_insights)}""")
        
        # Agricultural knowledge base (high priority for most categories)
        if 'semantic_search' in priorities and context_data.get('agricultural_data', {}).get('search_results'):
            search_results = context_data['agricultural_data']['search_results'][:3]
            knowledge_text = ""
            for i, result in enumerate(search_results, 1):
                knowledge_text += f"\n{i}. {result.get('document_text', '')[:200]}..."
            
            context_sections.append(f"""
RELEVANT AGRICULTURAL KNOWLEDGE:
{knowledge_text}""")
        
        # Yield prediction data (high priority for yield, crop selection)
        if 'real_yield_prediction' in priorities and context_data.get('agricultural_data', {}).get('yield_forecast'):
            yield_data = context_data['agricultural_data']['yield_forecast']
            context_sections.append(f"""
YIELD PREDICTION ANALYSIS:
- Predicted yield: {yield_data.get('predicted_yield_kg_per_ha', 'N/A')} kg/ha
- Confidence level: {yield_data.get('prediction_confidence', 'N/A')}
- Recommendations: {', '.join(yield_data.get('recommendations', [])[:3])}""")
        
        # Market intelligence (high priority for market forecasting)
        if 'real_market_apis' in priorities and context_data.get('market_intelligence'):
            market = context_data['market_intelligence']
            if market.get('current_prices'):
                price_info = market['current_prices'][0] if market['current_prices'] else {}
                context_sections.append(f"""
MARKET PRICE INFORMATION:
- Commodity: {price_info.get('commodity', 'N/A')}
- Current price: ₹{price_info.get('modal_price', 'N/A')} per quintal
- Market: {price_info.get('market', 'N/A')}
- Trend: {price_info.get('trend', 'N/A')}""")
        
        # Historical agricultural data
        if 'sql_queries' in priorities:
            context_sections.append("""
HISTORICAL DATA REFERENCE:
- Regional yield patterns and trends available
- Historical weather impact analysis
- Best practice outcomes from similar conditions""")
        
        return '\n'.join(context_sections) if context_sections else "Limited data available - providing general expert guidance."
    
    async def _call_gemini_with_expert_prompt(self, prompt: str, category: str) -> str:
        """Call Gemini API with category-specific configuration"""
        try:
            # Category-specific generation config
            generation_config = {
                'temperature': 0.3,  # More deterministic for agricultural advice
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 1000,
            }
            
            # Adjust temperature based on category
            if category in ['pest_disease_management', 'fertilizer_optimization']:
                generation_config['temperature'] = 0.1  # Very precise for technical advice
            elif category in ['seasonal_planning', 'crop_selection']:
                generation_config['temperature'] = 0.4  # Slightly more creative for planning
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(**generation_config)
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _generate_fallback_response(self, classification: Dict[str, Any]) -> str:
        """Generate category-specific fallback response when LLM is unavailable"""
        category = classification.get('primary_category', 'general_farming')
        
        expert_fallback_responses = {
            'fertilizer_optimization': """Namaste! For optimal fertilizer management:

**Soil Testing First**: Always conduct soil testing to determine NPK status before fertilizer application.

**NPK Recommendations** (General guidelines):
- Wheat: 120kg N + 60kg P₂O₅ + 40kg K₂O per hectare
- Rice: 120kg N + 60kg P₂O₅ + 40kg K₂O per hectare  
- Cotton: 120kg N + 60kg P₂O₅ + 60kg K₂O per hectare

**Application Strategy**:
- Apply full P & K + 1/3 N as basal dose
- Remaining N in 2-3 split applications
- Use organic matter (FYM/compost) @ 5-10 tonnes/hectare

**Cost Optimization**: 
- Buy fertilizers during off-season for better rates
- Consider DAP + Urea combination for NPK supply
- Use soil test-based fertilizer recommendations for precise application

For specific recommendations, consult your nearest Krishi Vigyan Kendra with your soil test report.""",

            'weather_impact': """Namaste! Weather-based farming guidance:

**Current Weather Monitoring**:
- Check daily weather forecasts for farming decisions
- Use IMD weather advisories for agricultural planning
- Monitor temperature, rainfall, and humidity trends

**Weather-Smart Practices**:
- **Heavy Rain**: Ensure proper field drainage, delay fertilizer application
- **Dry Spell**: Plan irrigation, use mulching to conserve moisture
- **High Temperature**: Schedule irrigation early morning/evening, provide shade for sensitive crops
- **High Humidity**: Monitor for fungal diseases, ensure good air circulation

**Seasonal Planning**:
- Plan sowing based on monsoon onset predictions
- Adjust crop varieties based on expected rainfall patterns
- Maintain weather-resilient seed varieties in stock

**Risk Management**:
- Crop insurance enrollment before season starts
- Emergency contact numbers for weather alerts
- Backup irrigation arrangements for dry periods

Stay connected with local weather updates and agricultural meteorology services.""",

            'crop_selection': """Namaste! For optimal crop selection:

**Key Selection Criteria**:
1. **Soil Type**: Match crop requirements with your soil characteristics
2. **Climate**: Choose varieties suited to your agro-climatic zone
3. **Water Availability**: Select crops matching your irrigation capacity
4. **Market Demand**: Research local market prices and demand trends

**High-Yielding Varieties** (Popular recommendations):
- **Wheat**: HD-2967, DBW-88, HD-3086
- **Rice**: Swarna, IR-64, Pusa Basmati-1
- **Cotton**: Bt cotton varieties approved for your state
- **Maize**: Pioneer, Syngenta hybrids

**Diversification Benefits**:
- Include leguminous crops for soil nitrogen enrichment
- Plan crop rotation to break pest-disease cycles
- Consider high-value crops like vegetables/fruits if suitable

**Resource Planning**:
- Calculate input costs vs expected returns
- Ensure availability of quality seeds and inputs
- Plan labor requirements during peak seasons

Consult your local agriculture extension officer for region-specific variety recommendations.""",

            'pest_disease_management': """Namaste! For effective pest and disease management:

**Integrated Pest Management (IPM) Approach**:

**Prevention First**:
- Use certified, disease-resistant seeds
- Maintain proper field sanitation
- Follow recommended crop rotation
- Balanced fertilization (avoid excess nitrogen)

**Monitoring & Identification**:
- Regular field scouting (2-3 times per week)
- Learn to identify common pests and diseases
- Use pheromone traps for insect monitoring
- Maintain pest activity records

**Control Strategies**:
1. **Biological Control**: Encourage natural predators, use bio-pesticides
2. **Cultural Control**: Timely sowing, proper spacing, weed management
3. **Chemical Control**: Use only when economic threshold is reached

**Safe Pesticide Use**:
- Read labels carefully and follow instructions
- Use recommended doses and timing
- Wear protective equipment during application
- Maintain pre-harvest intervals

**Emergency Action**: If severe infestation occurs, immediately consult your nearest agricultural extension officer or call the farmer helpline for expert guidance.

Remember: Prevention is always better and cheaper than cure!""",

            'yield_prediction': """Namaste! For maximizing crop yield:

**Yield Enhancement Strategies**:

**Seed & Variety Management**:
- Use certified seeds of high-yielding varieties
- Ensure proper seed treatment before sowing
- Maintain optimal plant population per hectare
- Choose varieties suited to your local conditions

**Nutrition Management**:
- Conduct soil testing for balanced fertilization
- Apply organic matter regularly (5-10 tonnes FYM/hectare)
- Follow recommended NPK application schedules
- Address micronutrient deficiencies (Zinc, Iron, Boron)

**Water Management**:
- Ensure timely irrigation at critical growth stages
- Use efficient irrigation methods (drip/sprinkler)
- Maintain proper drainage during heavy rains
- Monitor soil moisture levels

**Crop Management**:
- Timely field operations (sowing, weeding, harvesting)
- Proper plant protection measures
- Regular field monitoring and problem identification
- Use of growth promoters where beneficial

**Expected Yields** (with good management):
- Wheat: 40-50 quintals/hectare
- Rice: 50-60 quintals/hectare
- Cotton: 15-20 quintals/hectare

Focus on these fundamentals for consistent high yields!""",

            'market_price_forecasting': """Namaste! For better market decisions:

**Market Intelligence Strategies**:

**Price Monitoring**:
- Check daily mandi prices through eNAM portal
- Follow commodity price trends for your crops
- Monitor prices in nearby mandis for best rates
- Track seasonal price patterns for your crops

**Marketing Strategies**:
- **Timing**: Avoid harvesting rush, wait for price recovery
- **Storage**: Invest in proper storage to wait for better prices
- **Grading**: Clean and grade your produce for premium prices
- **Direct Marketing**: Explore Farmer Producer Organizations (FPOs)

**Government Support**:
- Know Minimum Support Prices (MSP) for your crops
- Register with nearby procurement centers
- Understand government procurement procedures
- Consider Price Deficiency Payment Schemes where available

**Value Addition**:
- Explore primary processing opportunities
- Connect with food processing units
- Consider direct consumer marketing
- Join farmer collectives for better bargaining power

**Planning Advice**:
- Diversify crops to spread market risks
- Plan production based on demand forecasts
- Maintain market contacts and relationships

Use government agriculture marketing apps and stay connected with local market committees for real-time information.""",

            'general_farming': """Namaste! Here's comprehensive farming guidance:

**Fundamental Best Practices**:

**Soil Health Management**:
- Regular soil testing (every 2-3 years)
- Organic matter addition (FYM, compost, green manure)
- Balanced fertilization based on soil test results
- Crop rotation to maintain soil fertility

**Water Conservation**:
- Adopt efficient irrigation methods
- Rainwater harvesting where possible
- Mulching to reduce water evaporation
- Proper drainage systems for excess water

**Integrated Farming**:
- Combine crops with dairy/poultry for additional income
- Kitchen gardening for family nutrition
- Vermicomposting for organic fertilizer production
- Agroforestry for long-term sustainability

**Technology Adoption**:
- Use weather-based agro-advisories
- Adopt precision farming tools gradually
- Connect with agricultural apps and portals
- Regular training and skill upgradation

**Financial Planning**:
- Crop insurance enrollment
- Maintain farming records and accounts
- Explore government schemes and subsidies
- Plan for emergency funds

**Continuous Learning**:
- Connect with Krishi Vigyan Kendras
- Join farmer groups and cooperatives
- Attend agricultural training programs
- Share experiences with fellow farmers

Remember: Successful farming combines traditional wisdom with modern science!"""
        }
        
        return expert_fallback_responses.get(category, expert_fallback_responses['general_farming'])
    
    def get_expert_specialization(self, category: str) -> str:
        """Get the expert specialization for a given category"""
        expert_info = {
            'fertilizer_optimization': "Senior Agricultural Scientist - Soil Nutrition & Fertilizer Management",
            'weather_impact': "Agricultural Meteorologist & Climate Expert",
            'crop_selection': "Crop Scientist & Plant Breeder",
            'pest_disease_management': "Entomologist & Plant Pathologist",
            'yield_prediction': "Agricultural Engineer & Precision Farming Expert",
            'market_price_forecasting': "Agricultural Economist & Market Analyst",
            'soil_health': "Soil Health & Management Specialist",
            'irrigation_planning': "Irrigation Engineer & Water Management Expert",
            'government_schemes': "Agricultural Extension & Schemes Expert",
            'seasonal_planning': "Farming Systems & Planning Specialist",
            'general_farming': "General Agricultural Advisory Expert"
        }
        return expert_info.get(category, expert_info['general_farming'])

# Global instance
agricultural_llm = GeminiLLMTool()
