"""
Context Fusion Engine

Combines results from multiple tools into coherent agricultural advice

File: app/tools/rag_core/context_fusion.py
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from .tool_orchestrator import ToolResult
from .query_classifier import QueryClassification

logger = logging.getLogger(__name__)

@dataclass
class FusedContext:
    """Combined context from multiple tools"""
    weather_intelligence: Dict[str, Any]
    market_intelligence: Dict[str, Any]
    agricultural_data: Dict[str, Any]
    government_info: Dict[str, Any]
    web_intelligence: Dict[str, Any]
    confidence_score: float
    data_freshness: str
    synthesis_summary: str

class AgriculturalContextFusion:
    """
    Fuses results from multiple agricultural tools into coherent context
    for AI reasoning and response generation
    """
    
    def __init__(self):
        self.data_quality_weights = {
            'real_weather_apis': 0.9,
            'real_market_apis': 0.85,
            'real_yield_prediction': 0.9,
            'sql_queries': 0.8,
            'semantic_search': 0.7,
            'government_apis': 0.85,
            'google_search': 0.6
        }

    async def fuse_tool_results(self, 
                              tool_results: Dict[str, ToolResult],
                              classification: QueryClassification) -> FusedContext:
        """
        Fuse results from multiple tools into unified context
        """
        logger.info(f"🔗 Fusing results from {len(tool_results)} tools")
        
        # Extract intelligence by domain
        weather_intelligence = self._extract_weather_intelligence(tool_results)
        market_intelligence = self._extract_market_intelligence(tool_results)
        agricultural_data = self._extract_agricultural_data(tool_results)
        government_info = self._extract_government_info(tool_results)
        web_intelligence = self._extract_web_intelligence(tool_results)
        
        # Calculate overall confidence
        confidence_score = self._calculate_confidence(tool_results)
        
        # Assess data freshness
        data_freshness = self._assess_data_freshness(tool_results)
        
        # Generate synthesis summary
        synthesis_summary = self._generate_synthesis_summary(
            classification, tool_results
        )
        
        return FusedContext(
            weather_intelligence=weather_intelligence,
            market_intelligence=market_intelligence,
            agricultural_data=agricultural_data,
            government_info=government_info,
            web_intelligence=web_intelligence,
            confidence_score=confidence_score,
            data_freshness=data_freshness,
            synthesis_summary=synthesis_summary
        )
        
    # (Unreachable) placeholder to ensure code never returns dict
    # logger.debug("FusedContext constructed: %s", type(result))

    def _extract_weather_intelligence(self, tool_results: Dict[str, ToolResult]) -> Dict[str, Any]:
        """Extract and structure weather-related intelligence"""
        weather_data = {}
        
        if 'real_weather_apis' in tool_results and tool_results['real_weather_apis'].success:
            data = tool_results['real_weather_apis'].data
            weather_data = {
                'current_conditions': data.get('current_weather', {}),
                'forecast': data.get('forecast', []),
                'agricultural_advisories': self._extract_weather_advisories(data.get('forecast', [])),
                'risk_alerts': self._identify_weather_risks(data.get('forecast', [])),
                'irrigation_recommendations': self._generate_irrigation_advice(data)
            }
        
        return weather_data

    def _extract_market_intelligence(self, tool_results: Dict[str, ToolResult]) -> Dict[str, Any]:
        """Extract and structure market-related intelligence"""
        market_data = {}
        
        # Real market data
        if 'real_market_apis' in tool_results and tool_results['real_market_apis'].success:
            data = tool_results['real_market_apis'].data
            market_data.update({
                'current_prices': data.get('mandi_prices', []),
                'price_analytics': data.get('price_analytics', {}),
                'commodity_focus': data.get('commodity', 'wheat')
            })
        
        # Price predictions
        if 'price_prediction' in tool_results and tool_results['price_prediction'].success:
            data = tool_results['price_prediction'].data
            market_data.update({
                'price_forecasts': data.get('price_prediction', {}),
                'trading_recommendations': self._extract_trading_advice(data.get('price_prediction', {}))
            })
        
        return market_data

    def _extract_agricultural_data(self, tool_results: Dict[str, ToolResult]) -> Dict[str, Any]:
        """Extract agricultural production data"""
        agri_data = {}
        
        # Yield predictions
        if 'real_yield_prediction' in tool_results and tool_results['real_yield_prediction'].success:
            data = tool_results['real_yield_prediction'].data
            agri_data.update({
                'yield_forecast': data.get('yield_prediction', {}),
                'productivity_advice': data.get('yield_prediction', {}).get('recommendations', [])
            })
        
        # Historical data
        if 'sql_queries' in tool_results and tool_results['sql_queries'].success:
            data = tool_results['sql_queries'].data
            agri_data.update({
                'historical_yields': data.get('yield_data', []),
                'rainfall_patterns': data.get('rainfall_data', []),
                'regional_comparisons': self._generate_regional_insights(data)
            })
        
        # Document knowledge
        if 'semantic_search' in tool_results and tool_results['semantic_search'].success:
            data = tool_results['semantic_search'].data
            search_results = data.get('search_results', [])
            agri_data.update({
                'search_results': search_results,  # Include full search results
                'expert_knowledge': search_results,
                'best_practices': self._extract_best_practices(search_results)
            })
        
        return agri_data

    def _extract_government_info(self, tool_results: Dict[str, ToolResult]) -> Dict[str, Any]:
        """Extract government schemes and policy information"""
        gov_data = {}
        
        if 'government_apis' in tool_results and tool_results['government_apis'].success:
            data = tool_results['government_apis'].data
            gov_data = {
                'eligible_schemes': data.get('eligible_schemes', []),
                'subsidies': data.get('subsidies', []),
                'financial_benefits': self._calculate_potential_benefits(data),
                'application_guidance': self._extract_application_steps(data.get('eligible_schemes', []))
            }
        
        return gov_data

    def _extract_web_intelligence(self, tool_results: Dict[str, ToolResult]) -> Dict[str, Any]:
        """Extract web search intelligence"""
        web_data = {}
        
        if 'google_search' in tool_results and tool_results['google_search'].success:
            data = tool_results['google_search'].data
            # data may be dict (expected) or list (old path). Normalize.
            if isinstance(data, list):
                web_results = data
            else:
                web_results = data.get('web_results', []) if isinstance(data, dict) else []
            web_data = {
                'latest_news': web_results,
                'trending_topics': self._identify_trends(web_results),
                'external_resources': self._categorize_web_sources(web_results)
            }
        
        return web_data

    def _calculate_confidence(self, tool_results: Dict[str, ToolResult]) -> float:
        """Calculate overall confidence score"""
        total_weight = 0
        weighted_confidence = 0
        
        for tool_name, result in tool_results.items():
            if result.success and tool_name in self.data_quality_weights:
                weight = self.data_quality_weights[tool_name]
                confidence = 0.9 if result.success else 0.1
                
                total_weight += weight
                weighted_confidence += confidence * weight
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.5

    def _assess_data_freshness(self, tool_results: Dict[str, ToolResult]) -> str:
        """Assess freshness of combined data"""
        live_data_tools = ['real_weather_apis', 'real_market_apis', 'google_search']
        recent_data_tools = ['real_yield_prediction', 'government_apis']
        
        live_count = sum(1 for tool in live_data_tools if tool in tool_results and tool_results[tool].success)
        recent_count = sum(1 for tool in recent_data_tools if tool in tool_results and tool_results[tool].success)
        
        if live_count >= 2:
            return 'very_fresh'
        elif live_count >= 1 or recent_count >= 2:
            return 'fresh'
        else:
            return 'standard'

    def _generate_synthesis_summary(self, 
                                  classification: QueryClassification,
                                  tool_results: Dict[str, ToolResult]) -> str:
        """Generate a summary of synthesized information"""
        successful_tools = [name for name, result in tool_results.items() if result.success]
        
        summary = f"Agricultural intelligence synthesis for {classification.primary_category} query. "
        summary += f"Successfully integrated data from {len(successful_tools)} sources: {', '.join(successful_tools)}. "
        
        if classification.urgency == 'high':
            summary += "High priority response with immediate actionable advice. "
        
        confidence = self._calculate_confidence(tool_results)
        if confidence > 0.8:
            summary += "High confidence recommendations based on multiple data sources."
        elif confidence > 0.6:
            summary += "Moderate confidence recommendations - additional verification advised."
        else:
            summary += "Limited confidence - please consult local agricultural experts."
        
        return summary

    # Helper methods for extracting specific insights
    def _extract_weather_advisories(self, forecast: List[Dict]) -> List[str]:
        """Extract weather advisories from forecast"""
        advisories = []
        for day in forecast[:3]:  # Next 3 days
            if day.get('agricultural_advisory'):
                advisories.append(day['agricultural_advisory'])
        return advisories

    def _identify_weather_risks(self, forecast: List[Dict]) -> List[str]:
        """Identify weather risks"""
        risks = []
        for day in forecast[:7]:
            if day.get('temp_max', 0) > 35:
                risks.append("High temperature risk - plan irrigation")
            if day.get('rainfall', 0) > 20:
                risks.append("Heavy rainfall expected - ensure drainage")
        return list(set(risks))

    def _generate_irrigation_advice(self, weather_data: Dict) -> List[str]:
        """Generate irrigation recommendations"""
        advice = []
        current = weather_data.get('current_weather', {})
        
        if current.get('humidity', 0) < 50:
            advice.append("Low humidity detected - increase irrigation frequency")
        
        if current.get('temperature', 0) > 30:
            advice.append("High temperature - schedule irrigation during early morning or evening")
        
        return advice

    def _extract_trading_advice(self, price_data: Dict) -> List[str]:
        """Extract trading recommendations"""
        advice = []
        if price_data.get('recommendation'):
            advice.append(price_data['recommendation'])
        return advice

    def _generate_regional_insights(self, sql_data: Dict) -> Dict[str, Any]:
        """Generate regional comparison insights"""
        return {
            'state_ranking': 'data_available',
            'district_comparison': 'available',
            'benchmark_performance': 'calculated'
        }

    def _extract_best_practices(self, search_results: List[Dict]) -> List[str]:
        """Extract best practices from search results"""
        practices = []
        for result in search_results[:3]:
            if result.get('document_text'):
                practices.append(f"Expert advice: {result['document_text'][:100]}...")
        return practices

    def _calculate_potential_benefits(self, gov_data: Dict) -> Dict[str, Any]:
        """Calculate potential financial benefits"""
        total_benefit = 0
        schemes = gov_data.get('eligible_schemes', [])
        
        for scheme in schemes:
            if scheme.get('benefit_amount'):
                total_benefit += scheme['benefit_amount']
        
        return {
            'total_annual_benefit': total_benefit,
            'scheme_count': len(schemes)
        }

    def _extract_application_steps(self, schemes: List[Dict]) -> List[str]:
        """Extract application guidance"""
        steps = []
        for scheme in schemes[:2]:  # Top 2 schemes
            if scheme.get('application_process'):
                steps.append(f"{scheme['scheme_name']}: {scheme['application_process']}")
        return steps

    def _identify_trends(self, web_results: List[Dict]) -> List[str]:
        """Identify trends from web results"""
        return ['trend_analysis_pending']

    def _categorize_web_sources(self, web_results: List[Dict]) -> Dict[str, List[str]]:
        """Categorize web sources"""
        return {'government': [], 'research': [], 'news': []}

# Global fusion engine instance
context_fusion = AgriculturalContextFusion()
