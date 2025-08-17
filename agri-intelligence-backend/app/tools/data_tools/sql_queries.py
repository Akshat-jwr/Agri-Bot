"""
SQL Query Tools for Agricultural Data
Queries your PostgreSQL database with agricultural datasets
"""
import asyncpg
import pandas as pd
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AgriculturalDataQueryTool:
    def __init__(self, db_url: str):
        self.db_url = db_url
        
    async def get_crop_yield_data(self, state: str, crop: str, 
                                 years: int = 5) -> List[Dict]:
        """Get crop yield data for state and crop"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT state_name, dist_name, year, 
                       {crop}_area_1000_ha as area,
                       {crop}_production_1000_tons as production,
                       {crop}_yield_kg_per_ha as yield
                FROM area_production_yield 
                WHERE LOWER(state_name) = LOWER($1) 
                  AND year >= $2 
                  AND {crop}_yield_kg_per_ha > 0
                ORDER BY year DESC, dist_name
                LIMIT 500
            """.format(crop=crop.lower())
            
            current_year = datetime.now().year
            start_year = current_year - years
            
            rows = await conn.fetch(query, state, start_year)
            
            result = []
            for row in rows:
                result.append({
                    'state': row['state_name'],
                    'district': row['dist_name'], 
                    'year': row['year'],
                    'area_1000_ha': float(row['area']) if row['area'] else 0,
                    'production_1000_tons': float(row['production']) if row['production'] else 0,
                    'yield_kg_per_ha': float(row['yield']) if row['yield'] else 0
                })
                
            await conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Crop yield query error: {e}")
            return [{'error': str(e)}]

    async def get_fertilizer_consumption_data(self, state: str, 
                                            years: int = 3) -> List[Dict]:
        """Get fertilizer consumption data for state"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT state_name, dist_name, year,
                       nitrogen_kharif_consumption_tons,
                       nitrogen_rabi_consumption_tons,
                       phosphate_kharif_consumption_tons,
                       phosphate_rabi_consumption_tons,
                       potash_kharif_consumption_tons,
                       potash_rabi_consumption_tons,
                       total_kharif_consumption_tons,
                       total_rabi_consumption_tons
                FROM state_wise_fertilizer
                WHERE LOWER(state_name) = LOWER($1)
                  AND year >= $2
                ORDER BY year DESC, dist_name
                LIMIT 200
            """
            
            current_year = datetime.now().year
            start_year = current_year - years
            
            rows = await conn.fetch(query, state, start_year)
            
            result = []
            for row in rows:
                result.append({
                    'state': row['state_name'],
                    'district': row['dist_name'],
                    'year': row['year'],
                    'nitrogen_kharif_tons': float(row['nitrogen_kharif_consumption_tons']) if row['nitrogen_kharif_consumption_tons'] else 0,
                    'nitrogen_rabi_tons': float(row['nitrogen_rabi_consumption_tons']) if row['nitrogen_rabi_consumption_tons'] else 0,
                    'phosphate_kharif_tons': float(row['phosphate_kharif_consumption_tons']) if row['phosphate_kharif_consumption_tons'] else 0,
                    'phosphate_rabi_tons': float(row['phosphate_rabi_consumption_tons']) if row['phosphate_rabi_consumption_tons'] else 0,
                    'potash_kharif_tons': float(row['potash_kharif_consumption_tons']) if row['potash_kharif_consumption_tons'] else 0,
                    'potash_rabi_tons': float(row['potash_rabi_consumption_tons']) if row['potash_rabi_consumption_tons'] else 0,
                    'total_kharif_tons': float(row['total_kharif_consumption_tons']) if row['total_kharif_consumption_tons'] else 0,
                    'total_rabi_tons': float(row['total_rabi_consumption_tons']) if row['total_rabi_consumption_tons'] else 0
                })
                
            await conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Fertilizer query error: {e}")
            return [{'error': str(e)}]

    async def get_rainfall_data(self, state: str, years: int = 5) -> List[Dict]:
        """Get rainfall data for state"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            query = """
                SELECT state_name, dist_name, year,
                       january_rainfall_millimeters, february_rainfall_millimeters,
                       march_rainfall_millimeters, april_rainfall_millimeters,
                       may_rainfall_millimeters, june_rainfall_millimeters,
                       july_rainfall_millimeters, august_rainfall_millimeters,
                       september_rainfall_millimeters, october_rainfall_millimeters,
                       november_rainfall_millimeters, december_rainfall_millimeters,
                       annual_rainfall_millimeters
                FROM monthly_rainfall
                WHERE LOWER(state_name) = LOWER($1)
                  AND year >= $2
                ORDER BY year DESC, dist_name
                LIMIT 300
            """
            
            current_year = datetime.now().year
            start_year = current_year - years
            
            rows = await conn.fetch(query, state, start_year)
            
            result = []
            for row in rows:
                monthly_data = {}
                months = ['january', 'february', 'march', 'april', 'may', 'june',
                         'july', 'august', 'september', 'october', 'november', 'december']
                
                for month in months:
                    col_name = f'{month}_rainfall_millimeters'
                    monthly_data[f'{month}_mm'] = float(row[col_name]) if row[col_name] else 0
                
                result.append({
                    'state': row['state_name'],
                    'district': row['dist_name'],
                    'year': row['year'],
                    'annual_rainfall_mm': float(row['annual_rainfall_millimeters']) if row['annual_rainfall_millimeters'] else 0,
                    'monthly_rainfall': monthly_data
                })
                
            await conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Rainfall query error: {e}")
            return [{'error': str(e)}]

    async def get_market_price_data(self, commodity: str = None, 
                                   state: str = None, days: int = 30) -> List[Dict]:
        """Get market price data from your market data table"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            where_conditions = []
            params = []
            param_count = 1
            
            if commodity:
                where_conditions.append(f"LOWER(commodity) = LOWER(${param_count})")
                params.append(commodity)
                param_count += 1
                
            if state:
                where_conditions.append(f"LOWER(state) = LOWER(${param_count})")
                params.append(state)
                param_count += 1
            
            # Add date filter
            cutoff_date = datetime.now() - timedelta(days=days)
            where_conditions.append(f"arrival_date >= ${param_count}")
            params.append(cutoff_date.date())
            
            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            query = f"""
                SELECT state, district, market, commodity, variety,
                       arrival_date, min_price, max_price, modal_price
                FROM market_data
                {where_clause}
                ORDER BY arrival_date DESC, commodity, state
                LIMIT 500
            """
            
            rows = await conn.fetch(query, *params)
            
            result = []
            for row in rows:
                result.append({
                    'state': row['state'],
                    'district': row['district'],
                    'market': row['market'],
                    'commodity': row['commodity'],
                    'variety': row['variety'],
                    'date': row['arrival_date'].strftime('%Y-%m-%d'),
                    'min_price': float(row['min_price']) if row['min_price'] else 0,
                    'max_price': float(row['max_price']) if row['max_price'] else 0,
                    'modal_price': float(row['modal_price']) if row['modal_price'] else 0
                })
                
            await conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Market price query error: {e}")
            return [{'error': str(e)}]

    async def get_agricultural_statistics(self, state: str) -> Dict:
        """Get comprehensive agricultural statistics for a state"""
        try:
            conn = await asyncpg.connect(self.db_url)
            
            # Get crop diversity
            crop_query = """
                SELECT COUNT(DISTINCT CASE WHEN rice_yield_kg_per_ha > 0 THEN 'rice' END) +
                       COUNT(DISTINCT CASE WHEN wheat_yield_kg_per_ha > 0 THEN 'wheat' END) +
                       COUNT(DISTINCT CASE WHEN cotton_yield_kg_per_ha > 0 THEN 'cotton' END) +
                       COUNT(DISTINCT CASE WHEN maize_yield_kg_per_ha > 0 THEN 'maize' END) as crop_diversity
                FROM area_production_yield
                WHERE LOWER(state_name) = LOWER($1)
            """
            
            # Get average yields
            yield_query = """
                SELECT AVG(rice_yield_kg_per_ha) as avg_rice_yield,
                       AVG(wheat_yield_kg_per_ha) as avg_wheat_yield,
                       AVG(cotton_yield_kg_per_ha) as avg_cotton_yield,
                       AVG(maize_yield_kg_per_ha) as avg_maize_yield
                FROM area_production_yield
                WHERE LOWER(state_name) = LOWER($1)
                  AND year >= $2
            """
            
            # Get irrigated area percentage
            irrigation_query = """
                SELECT AVG(rice_irrigated_area_1000_ha) as avg_rice_irrigated,
                       AVG(wheat_irrigated_area_1000_ha) as avg_wheat_irrigated
                FROM state_wise_irrigation
                WHERE LOWER(state_name) = LOWER($1)
            """
            
            current_year = datetime.now().year
            
            crop_result = await conn.fetchrow(crop_query, state)
            yield_result = await conn.fetchrow(yield_query, state, current_year - 5)
            irrigation_result = await conn.fetchrow(irrigation_query, state)
            
            statistics = {
                'state': state,
                'crop_diversity_score': crop_result['crop_diversity'] if crop_result else 0,
                'average_yields': {
                    'rice_kg_per_ha': float(yield_result['avg_rice_yield']) if yield_result['avg_rice_yield'] else 0,
                    'wheat_kg_per_ha': float(yield_result['avg_wheat_yield']) if yield_result['avg_wheat_yield'] else 0,
                    'cotton_kg_per_ha': float(yield_result['avg_cotton_yield']) if yield_result['avg_cotton_yield'] else 0,
                    'maize_kg_per_ha': float(yield_result['avg_maize_yield']) if yield_result['avg_maize_yield'] else 0
                },
                'irrigation_coverage': {
                    'rice_irrigated_1000_ha': float(irrigation_result['avg_rice_irrigated']) if irrigation_result['avg_rice_irrigated'] else 0,
                    'wheat_irrigated_1000_ha': float(irrigation_result['avg_wheat_irrigated']) if irrigation_result['avg_wheat_irrigated'] else 0
                }
            }
            
            await conn.close()
            return statistics
            
        except Exception as e:
            logger.error(f"Agricultural statistics query error: {e}")
            return {'error': str(e)}

# Global SQL query tool instance
sql_tool = AgriculturalDataQueryTool("postgresql://postgres@localhost:5433/agri_db")
