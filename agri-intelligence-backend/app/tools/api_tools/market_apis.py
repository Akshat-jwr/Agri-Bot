"""
Market Price API Tools for Agricultural Intelligence
Integrates with AGMARKNET and commodity trading APIs
"""
import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MarketPriceAPITool:
    def __init__(self):
        self.agmarknet_base_url = "https://api.agmarknet.gov.in"
        self.commodity_api_url = "https://api.commodityonline.com"  # Example
        
    async def get_current_mandi_prices(self, state: str, commodity: str) -> List[Dict]:
        """Get current mandi prices for commodity in state"""
        try:
            # Simulated AGMARKNET API call (replace with actual API)
            async with aiohttp.ClientSession() as session:
                params = {
                    'state': state,
                    'commodity': commodity,
                    'date': datetime.now().strftime('%Y-%m-%d')
                }
                
                # Mock response for development
                mock_prices = [
                    {
                        'mandi_name': f'{state} APMC',
                        'commodity': commodity,
                        'variety': 'Grade A',
                        'min_price': 2800,
                        'max_price': 3200,
                        'modal_price': 3000,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'unit': 'per quintal'
                    }
                ]
                
                return mock_prices
                
        except Exception as e:
            logger.error(f"Market API error: {e}")
            return [{'error': str(e)}]

    async def get_price_trend(self, commodity: str, days: int = 30) -> List[Dict]:
        """Get price trend for commodity over last N days"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Mock price trend data
            trend_data = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                base_price = 3000
                variation = (i % 10 - 5) * 50  # Price fluctuation
                
                trend_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'commodity': commodity,
                    'average_price': base_price + variation,
                    'volume_traded': 1000 + (i % 5) * 200
                })
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Price trend error: {e}")
            return [{'error': str(e)}]

    async def get_market_advisory(self, commodity: str, location: Dict) -> Dict:
        """Get market advisory for commodity"""
        current_prices = await self.get_current_mandi_prices(location.get('state', ''), commodity)
        price_trend = await self.get_price_trend(commodity, 30)
        
        advisory = {
            'current_prices': current_prices,
            'price_trend': price_trend[-7:],  # Last 7 days
            'recommendation': self._generate_market_advice(current_prices, price_trend, commodity)
        }
        
        return advisory
    
    def _generate_market_advice(self, prices: List[Dict], trend: List[Dict], commodity: str) -> str:
        """Generate market advice based on prices and trends"""
        if not prices or not trend:
            return f"Market data unavailable for {commodity}"
        
        current_price = prices[0].get('modal_price', 0)
        trend_prices = [day['average_price'] for day in trend[-7:]]
        avg_week_price = sum(trend_prices) / len(trend_prices) if trend_prices else current_price
        
        if current_price > avg_week_price * 1.05:
            return f"Good time to sell {commodity}. Prices are above weekly average."
        elif current_price < avg_week_price * 0.95:
            return f"Consider holding {commodity}. Prices are below weekly average."
        else:
            return f"{commodity} prices are stable. Monitor market for next few days."

# Global market tool instance  
market_tool = MarketPriceAPITool()
