"""
Agricultural Tool Orchestrator with Concurrent Processing

Executes multiple tools concurrently based on query classification

File: app/tools/rag_core/tool_orchestrator.py
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

# Import your existing tools
from ..api_tools.real_weather_apis import real_weather_tool
from ..api_tools.real_market_apis import real_market_tool
from ..api_tools.government_apis import government_tool
from ..ml_tools.real_yield_prediction import real_yield_model
from ..ml_tools.price_prediction import price_tool
from ..data_tools.sql_queries import agricultural_sql
from ..vector_tools.semantic_search import search_tool
from .google_search_tool import google_search_tool
from .query_classifier import QueryClassification

logger = logging.getLogger(__name__)

@dataclass
class ToolResult:
    """Standardized tool result"""
    tool_name: str
    success: bool
    data: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None

class AgriculturalToolOrchestrator:
    """
    Orchestrates concurrent execution of agricultural intelligence tools
    Based on query classification and farmer context
    """
    
    def __init__(self):
        self.tool_registry = {
            'real_weather_apis': self._execute_weather_tools,
            'real_market_apis': self._execute_market_tools,
            'government_apis': self._execute_government_tools,
            'real_yield_prediction': self._execute_yield_prediction,
            'price_prediction': self._execute_price_prediction,
            'sql_queries': self._execute_sql_queries,
            'semantic_search': self._execute_semantic_search,
            'google_search': self._execute_google_search
        }
        
        # Default locations for tools that need coordinates
        self.state_coordinates = {
            'punjab': (30.7333, 76.7794),
            'haryana': (29.0588, 76.0856),
            'uttar pradesh': (26.8467, 80.9462),
            'maharashtra': (19.7515, 75.7139),
            'karnataka': (15.3173, 75.7139)
        }

    async def orchestrate_tools(self, 
                              classification: QueryClassification,
                              farmer_context: Optional[Dict] = None) -> Dict[str, ToolResult]:
        """
        Execute tools concurrently based on query classification
        """
        start_time = datetime.now()
        
        # Determine which tools to execute
        tools_to_execute = self._determine_tools(classification)
        
        # Prepare execution context
        execution_context = self._prepare_execution_context(classification, farmer_context)
        
        logger.info(f"🔧 Executing {len(tools_to_execute)} tools concurrently: {tools_to_execute}")
        
        # Execute tools concurrently
        tasks = []
        for tool_name in tools_to_execute:
            if tool_name in self.tool_registry:
                task = self._execute_tool_safely(tool_name, execution_context)
                tasks.append(task)
        
        # Wait for all tools to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        tool_results = {}
        for i, result in enumerate(results):
            tool_name = tools_to_execute[i]
            if isinstance(result, Exception):
                tool_results[tool_name] = ToolResult(
                    tool_name=tool_name,
                    success=False,
                    data={},
                    execution_time=0,
                    error_message=str(result)
                )
            else:
                tool_results[tool_name] = result
        
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Tool orchestration completed in {execution_time:.2f} seconds")
        
        return tool_results

    def _determine_tools(self, classification: QueryClassification) -> List[str]:
        """Determine which tools to execute based on classification"""
        primary_category = classification.primary_category
        
        # Map categories to tools
        category_tool_mapping = {
            'weather_impact': ['real_weather_apis', 'semantic_search'],
            'irrigation_planning': ['real_weather_apis', 'sql_queries', 'semantic_search'],
            # Added weather for richer contextual advice (previously missing causing empty weather section)
            'market_price_forecasting': ['real_market_apis', 'price_prediction', 'semantic_search', 'real_weather_apis'],
            'crop_selection': ['real_yield_prediction', 'sql_queries', 'semantic_search'],
            'yield_prediction': ['real_yield_prediction', 'real_weather_apis', 'sql_queries'],
            'pest_disease_management': ['semantic_search', 'google_search', 'real_weather_apis'],
            'fertilizer_optimization': ['sql_queries', 'semantic_search', 'real_yield_prediction'],
            'government_schemes': ['government_apis', 'semantic_search', 'google_search'],
            'financial_planning': ['government_apis', 'real_market_apis', 'semantic_search'],
            'seasonal_planning': ['real_weather_apis', 'semantic_search', 'sql_queries'],
            'soil_health': ['semantic_search', 'sql_queries', 'google_search'],
            # Added: general_farming baseline should still surface multi-domain context
            'general_farming': [
                'real_weather_apis',
                'real_market_apis',
                'real_yield_prediction',
                'government_apis',
                'semantic_search',
                'google_search'
            ]
        }
        
        tools = category_tool_mapping.get(primary_category, ['semantic_search'])
        
        # Add tools from secondary categories
        for secondary_category in classification.secondary_categories[:2]:  # Limit to 2 secondary
            secondary_tools = category_tool_mapping.get(secondary_category, [])
            for tool in secondary_tools:
                if tool not in tools:
                    tools.append(tool)
        # Allow richer context (cap at 6 to include core domains)
        # Ensure weather is always present for holistic advice (if not already added)
        if 'real_weather_apis' not in tools:
            tools.append('real_weather_apis')
        return tools[:6]

    def _prepare_execution_context(self, 
                                 classification: QueryClassification,
                                 farmer_context: Optional[Dict]) -> Dict[str, Any]:
        """Prepare context for tool execution"""
        context = {
            'classification': classification,
            'entities': classification.extracted_entities,
            'location': classification.location_context or {},
            'farmer_context': farmer_context or {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Add default location if not specified
        if not context['location'] and farmer_context and 'state' in farmer_context:
            context['location'] = {'state': farmer_context['state']}
        
        # Default to Punjab if no location
        if not context['location']:
            context['location'] = {'state': 'Punjab'}
        
        # Get coordinates for weather APIs
        state = context['location'].get('state', '').lower()
        if state in self.state_coordinates:
            context['coordinates'] = self.state_coordinates[state]
        else:
            context['coordinates'] = self.state_coordinates['punjab']  # Default
        
        return context

    async def _execute_tool_safely(self, tool_name: str, context: Dict[str, Any]) -> ToolResult:
        """Execute a tool safely with error handling and timing"""
        start_time = datetime.now()
        
        try:
            tool_function = self.tool_registry[tool_name]
            data = await tool_function(context)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResult(
                tool_name=tool_name,
                success=True,
                data=data,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Tool {tool_name} failed: {e}")
            
            return ToolResult(
                tool_name=tool_name,
                success=False,
                data={},
                execution_time=execution_time,
                error_message=str(e)
            )

    # Tool execution methods
    async def _execute_weather_tools(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute weather-related tools"""
        lat, lon = context['coordinates']
        
        # Get current weather and forecast concurrently
        current_weather_task = real_weather_tool.get_live_weather(lat, lon)
        forecast_task = real_weather_tool.get_agricultural_forecast(lat, lon, days=7)
        
        current_weather, forecast = await asyncio.gather(
            current_weather_task, forecast_task, return_exceptions=True
        )
        
        return {
            'current_weather': current_weather if not isinstance(current_weather, Exception) else {},
            'forecast': forecast if not isinstance(forecast, Exception) else [],
            'location': context['location']
        }

    async def _execute_market_tools(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute market price tools"""
        state = context['location'].get('state', 'Punjab')
        entities = context['entities']
        
        # Default commodity
        commodity = 'wheat'
        if entities.get('crops'):
            commodity = entities['crops'][0]
        
        # Get market data concurrently
        mandi_prices_task = real_market_tool.get_live_mandi_prices(state, commodity)
        price_analytics_task = real_market_tool.get_price_analytics(commodity)
        
        mandi_prices, analytics = await asyncio.gather(
            mandi_prices_task, price_analytics_task, return_exceptions=True
        )
        
        return {
            'mandi_prices': mandi_prices if not isinstance(mandi_prices, Exception) else [],
            'price_analytics': analytics if not isinstance(analytics, Exception) else {},
            'commodity': commodity,
            'state': state
        }

    async def _execute_government_tools(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute government schemes tools"""
        farmer_profile = {
            'state': context['location'].get('state', 'Punjab'),
            'land_size': 2,
            'crop_type': context['entities'].get('crops', ['wheat'])[0] if context['entities'].get('crops') else 'wheat'
        }
        try:
            schemes = await government_tool.get_eligible_schemes(farmer_profile)
        except NotImplementedError:
            schemes = []
        try:
            subsidies = await government_tool.get_subsidy_rates('fertilizer', farmer_profile['state'])
        except NotImplementedError:
            subsidies = []
        return {'eligible_schemes': schemes, 'subsidies': subsidies, 'farmer_profile': farmer_profile}

    async def _execute_yield_prediction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute yield prediction"""
        # Prepare farm data
        farm_data = {
            'crop_type': context['entities'].get('crops', ['wheat'])[0] if context['entities'].get('crops') else 'wheat',
            'state': context['location'].get('state', 'Punjab'),
            'district': context['location'].get('district', 'Ludhiana'),
            'annual_rainfall': 600,  # Default
            'nitrogen_kharif': 100,  # Default
            'crop_area': 2.0  # Default
        }
        
        prediction = await real_yield_model.predict_yield(farm_data)
        
        return {
            'yield_prediction': prediction,
            'farm_data': farm_data
        }

    async def _execute_price_prediction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute price prediction"""
        commodity = 'wheat'
        if context['entities'].get('crops'):
            commodity = context['entities']['crops'][0]
        
        # Mock current market data for prediction
        current_market_data = {
            'current_price': 3000,
            'price_week_ago': 2950,
            'price_ma_7': 2980,
            'price_ma_30': 2950,
            'price_volatility': 120
        }
        
        prediction = price_tool.predict_price(commodity, current_market_data)
        
        return {
            'price_prediction': prediction,
            'commodity': commodity
        }

    async def _execute_sql_queries(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL database queries"""
        state = context['location'].get('state', 'Punjab')
        crop = context['entities'].get('crops', ['wheat'])[0] if context['entities'].get('crops') else 'wheat'
        
        # Get relevant agricultural data
        yield_data = await agricultural_sql.get_crop_yield_by_state(crop)
        rainfall_data = await agricultural_sql.get_rainfall_patterns(state)
        
        return {
            'yield_data': yield_data,
            'rainfall_data': rainfall_data[:5],  # Limit results
            'crop': crop,
            'state': state
        }

    async def _execute_semantic_search(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute semantic document search"""
        classification = context['classification']
        
        # Build search query from classification
        search_query = f"{classification.primary_category} farming advice"
        if context['entities'].get('crops'):
            search_query += f" {context['entities']['crops'][0]}"
        
        results = await search_tool.search_agricultural_documents(search_query, n_results=3)
        
        return {
            'search_results': results,
            'search_query': search_query
        }

    async def _execute_google_search(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Google Search for real-time information (no mock)."""
        classification = context['classification']
        base_query = classification.primary_category.replace('_', ' ')
        if context['entities'].get('crops'):
            base_query += f" {context['entities']['crops'][0]}"
        if context['location'].get('state'):
            base_query += f" {context['location']['state']}"
        results = await google_search_tool.search_agricultural_info(
            query=base_query,
            location=context['location'].get('state'),
            num_results=5
        )
        return {
            'web_results': results,
            'search_query': base_query
        }

# Global orchestrator instance
tool_orchestrator = AgriculturalToolOrchestrator()
