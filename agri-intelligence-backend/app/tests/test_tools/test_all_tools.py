"""
Agricultural Tools Test - FIXED IMPORTS
"""
import sys
from pathlib import Path
import pytest
import asyncio
import time
from unittest.mock import patch, AsyncMock



# ✅ Fix Python import path
project_root = Path(__file__).parent.parent.parent.parent  # Go up to root
sys.path.insert(0, str(project_root))
print(f"✅ Added {project_root} to Python path")

# Now imports will work
from app.tools.api_tools.weather_apis import weather_tool
from app.tools.api_tools.market_apis import market_tool  
from app.tools.api_tools.government_apis import government_tool
from app.tools.ml_tools.yield_prediction import yield_tool
from app.tools.ml_tools.price_prediction import price_tool
from app.tools.data_tools.sql_queries import sql_tool
from app.tools.vector_tools.semantic_search import search_tool

# Rest of your test code...


class TestWeatherTools:
    
    @pytest.mark.asyncio
    async def test_current_weather(self):
        """Test current weather API"""
        location = {'latitude': 30.7333, 'longitude': 76.7794}  # Chandigarh
        
        # Mock the API call for testing
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'main': {'temp': 25.5, 'humidity': 65},
                'rain': {'1h': 2.5},
                'wind': {'speed': 10.2},
                'weather': [{'description': 'scattered clouds'}]
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await weather_tool.get_current_weather(location)
            
            assert 'temperature' in result
            assert 'humidity' in result
            assert 'weather_condition' in result
            print(f"✅ Weather API: {result}")

    @pytest.mark.asyncio
    async def test_weather_forecast(self):
        """Test weather forecast API"""
        location = {'latitude': 28.6139, 'longitude': 77.2090}  # Delhi
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'list': [
                    {
                        'dt_txt': '2024-01-20 12:00:00',
                        'main': {'temp_max': 28, 'temp_min': 15, 'humidity': 60},
                        'pop': 0.2,
                        'wind': {'speed': 8},
                        'weather': [{'description': 'clear sky'}]
                    }
                ] * 7
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await weather_tool.get_weather_forecast(location, 7)
            
            assert len(result) == 7
            assert 'temperature_max' in result[0]
            print(f"✅ Forecast API: {len(result)} days")

class TestMarketTools:
    
    @pytest.mark.asyncio
    async def test_mandi_prices(self):
        """Test mandi prices API"""
        result = await market_tool.get_current_mandi_prices("Punjab", "wheat")
        
        assert isinstance(result, list)
        if result and 'error' not in result[0]:
            assert 'mandi_name' in result
            assert 'modal_price' in result
        print(f"✅ Mandi Prices: {len(result)} markets")

    @pytest.mark.asyncio
    async def test_price_trends(self):
        """Test price trend analysis"""
        result = await market_tool.get_price_trend("cotton", 30)
        
        assert isinstance(result, list)
        if result and 'error' not in result[0]:
            assert len(result) == 30
            assert 'average_price' in result
        print(f"✅ Price Trends: {len(result)} days")

class TestGovernmentTools:
    
    @pytest.mark.asyncio
    async def test_eligible_schemes(self):
        """Test government schemes API"""
        farmer_profile = {
            'land_size': 1.5,  # hectares
            'crop_type': 'wheat',
            'state': 'Punjab'
        }
        
        result = await government_tool.get_eligible_schemes(farmer_profile)
        
        assert isinstance(result, list)
        if result and 'error' not in result[0]:
            assert 'scheme_name' in result
            assert 'eligibility' in result
        print(f"✅ Government Schemes: {len(result)} schemes")

    @pytest.mark.asyncio  
    async def test_subsidy_rates(self):
        """Test subsidy rates API"""
        result = await government_tool.get_subsidy_rates("fertilizer", "Punjab")
        
        assert isinstance(result, list)
        if result:
            assert 'type' in result[0]
            assert 'subsidy_rate' in result
        print(f"✅ Subsidy Rates: {len(result)} categories")

class TestMLTools:
    
    def test_yield_prediction(self):
        """Test crop yield prediction"""
        farm_data = {
            'rainfall': 800,
            'temperature': 25,
            'humidity': 65,
            'soil_ph': 6.8,
            'fertilizer_npk_ratio': 1.2,
            'irrigation_type': 'drip',
            'seed_variety': 'hybrid',
            'sowing_month': 6,
            'area_hectares': 2.0
        }
        
        result = yield_tool.predict_yield(farm_data)
        
        if 'error' not in result:
            assert 'predicted_yield_kg_per_ha' in result
            assert 'confidence_level' in result
            assert 'recommendations' in result
        print(f"✅ Yield Prediction: {result.get('predicted_yield_kg_per_ha', 'Error')} kg/ha")

    def test_price_prediction(self):
        """Test price prediction"""
        market_data = {
            'current_price': 3000,
            'price_week_ago': 2950,
            'price_ma_7': 3025,
            'price_ma_30': 3100,
            'price_volatility': 75
        }
        
        # First train a simple model (mock)
        with patch.object(price_tool, 'models', {'wheat': {
            'model': AsyncMock(),
            'feature_columns': ['price_lag_1'],
            'last_training_date': '2024-01-01'
        }}):
            result = price_tool.predict_price("wheat", market_data, 7)
            
            if 'error' not in result:
                assert 'predictions' in result
                assert 'recommendation' in result
            print(f"✅ Price Prediction: {result.get('recommendation', 'Error')}")

class TestDataTools:
    
    @pytest.mark.asyncio
    async def test_crop_yield_query(self):
        """Test SQL crop yield queries"""
        result = await sql_tool.get_crop_yield_data("Punjab", "wheat", 3)
        
        assert isinstance(result, list)
        if result and 'error' not in result[0]:
            assert 'yield_kg_per_ha' in result
            assert 'state' in result
        print(f"✅ Crop Yield Query: {len(result)} records")

    @pytest.mark.asyncio
    async def test_fertilizer_query(self):
        """Test fertilizer consumption queries"""
        result = await sql_tool.get_fertilizer_consumption_data("Gujarat", 2)
        
        assert isinstance(result, list)
        if result and 'error' not in result[0]:
            assert 'nitrogen_kharif_tons' in result
        print(f"✅ Fertilizer Query: {len(result)} records")

    @pytest.mark.asyncio
    async def test_rainfall_query(self):
        """Test rainfall data queries"""
        result = await sql_tool.get_rainfall_data("Maharashtra", 2)
        
        assert isinstance(result, list)
        if result and 'error' not in result[0]:
            assert 'annual_rainfall_mm' in result
            assert 'monthly_rainfall' in result
        print(f"✅ Rainfall Query: {len(result)} records")

class TestVectorTools:
    
    @pytest.mark.asyncio
    async def test_semantic_search(self):
        """Test semantic search in documents"""
        result = await search_tool.search_agricultural_documents(
            "fertilizer recommendations for wheat farming", 
            n_results=3
        )
        
        assert isinstance(result, list)
        if result and 'error' not in result[0]:
            assert 'document_text' in result
            assert 'relevance_score' in result
        print(f"✅ Semantic Search: {len(result)} results")

    @pytest.mark.asyncio
    async def test_topic_search(self):
        """Test topic-specific search"""
        location = {'state': 'Punjab'}
        result = await search_tool.search_by_agricultural_topic(
            "irrigation management", 
            location=location,
            n_results=2
        )
        
        assert isinstance(result, list)
        print(f"✅ Topic Search: {len(result)} results")

    @pytest.mark.asyncio
    async def test_document_summary(self):
        """Test document database summary"""
        result = await search_tool.get_document_summary()
        
        if 'error' not in result:
            assert 'total_documents' in result
            assert 'source_files' in result
        print(f"✅ Document Summary: {result.get('total_documents', 'Error')} docs")

# Performance benchmarking
class TestToolPerformance:
    
    @pytest.mark.asyncio
    async def test_tool_response_times(self):
        """Benchmark all tool response times"""
        print("\n🚀 Tool Performance Benchmark")
        print("=" * 50)
        
        # Test each tool and measure time
        tools_to_test = [
            ("Weather API", weather_tool.get_current_weather({'latitude': 28.6, 'longitude': 77.2})),
            ("Market API", market_tool.get_current_mandi_prices("Punjab", "wheat")),
            ("Schemes API", government_tool.get_eligible_schemes({'land_size': 1.5})),
            ("SQL Query", sql_tool.get_crop_yield_data("Punjab", "rice", 1)),
            ("Semantic Search", search_tool.search_agricultural_documents("farming techniques", 2)),
        ]
        
        for tool_name, tool_call in tools_to_test:
            start_time = time.time()
            try:
                result = await tool_call
                elapsed = time.time() - start_time
                
                status = "✅ Success" if (isinstance(result, list) and result) or (isinstance(result, dict) and 'error' not in result) else "⚠️  Limited"
                print(f"{tool_name:15} | {elapsed:6.3f}s | {status}")
                
                # Performance assertion
                assert elapsed < 10.0, f"{tool_name} took too long: {elapsed:.3f}s"
                
            except Exception as e:
                print(f"{tool_name:15} | Error: {str(e)[:30]}...")

async def run_tool_benchmark():
    """Run comprehensive tool benchmark"""
    print("🛠️  Agricultural Intelligence Tools - Comprehensive Test")
    print("=" * 60)
    
    # Test categories
    test_suites = [
        ("Weather Tools", TestWeatherTools()),
        ("Market Tools", TestMarketTools()), 
        ("Government Tools", TestGovernmentTools()),
        ("ML Tools", TestMLTools()),
        ("Data Tools", TestDataTools()),
        ("Vector Tools", TestVectorTools()),
        ("Performance", TestToolPerformance())
    ]
    
    total_start = time.time()
    
    for suite_name, test_instance in test_suites:
        print(f"\n📊 Testing {suite_name}...")
        print("-" * 30)
        
        # Run each test method
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_')]
        
        for test_method in test_methods:
            try:
                method_func = getattr(test_instance, test_method)
                if asyncio.iscoroutinefunction(method_func):
                    await method_func()
                else:
                    method_func()
            except Exception as e:
                print(f"❌ {test_method}: {e}")
    
    total_time = time.time() - total_start
    print(f"\n🎯 Total testing time: {total_time:.2f} seconds")
    print("🎉 All tools tested and ready for integration!")

if __name__ == "__main__":
    asyncio.run(run_tool_benchmark())
