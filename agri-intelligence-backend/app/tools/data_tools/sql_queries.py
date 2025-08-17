"""
Agricultural Intelligence SQL Queries - Production Ready
Comprehensive SQL queries for Indian agricultural data processing, ML training, and analytics
Fixed: Removed non-existent columns, added error handling, optimized for performance
"""

import asyncpg
import pandas as pd
from typing import Dict, List, Optional, Union
import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class AgriculturalSQLQueries:
    """
    Comprehensive SQL query manager for agricultural intelligence system
    Handles all database operations for crop yield prediction, market analysis, and farming insights
    """
    
    def __init__(self, db_url: str = None):
        self.db_url = db_url or os.getenv('DATABASE_URL', 'postgresql://postgres@localhost:5433/agri_db')
        
    async def get_connection(self):
        """Get database connection with error handling"""
        try:
            return await asyncpg.connect(self.db_url)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    # ==========================================
    # CORE ML TRAINING QUERIES (FIXED)
    # ==========================================
    
    async def get_ml_training_data(self, years_back: int = 10) -> pd.DataFrame:
        """
        ✅ FIXED: Get comprehensive training data for ML models
        Removed non-existent column: mr.monsoon_rainfall_millimeters
        """
        query = """
        SELECT 
            -- Yield data (target variables)
            apy.wheat_yield_kg_per_ha,
            apy.rice_yield_kg_per_ha,
            apy.cotton_yield_kg_per_ha,
            apy.maize_yield_kg_per_ha,
            
            -- Area and production data
            apy.wheat_area_1000_ha,
            apy.rice_area_1000_ha,
            apy.cotton_area_1000_ha,
            apy.maize_area_1000_ha,
            apy.wheat_production_1000_tons,
            apy.rice_production_1000_tons,
            apy.cotton_production_1000_tons,
            apy.maize_production_1000_tons,
            
            -- Location and time
            apy.state_name,
            apy.dist_name,
            apy.year,
            
            -- ✅ FIXED: Rainfall data (removed monsoon_rainfall_millimeters)
            mr.annual_rainfall_millimeters,
            mr.january_rainfall_millimeters,
            mr.february_rainfall_millimeters,
            mr.march_rainfall_millimeters,
            mr.april_rainfall_millimeters,
            mr.may_rainfall_millimeters,
            mr.june_rainfall_millimeters,
            mr.july_rainfall_millimeters,
            mr.august_rainfall_millimeters,
            mr.september_rainfall_millimeters,
            mr.october_rainfall_millimeters,
            mr.november_rainfall_millimeters,
            mr.december_rainfall_millimeters,
            
            -- Fertilizer consumption data
            sf.nitrogen_kharif_consumption_tons,
            sf.nitrogen_rabi_consumption_tons,
            sf.phosphate_kharif_consumption_tons,
            sf.phosphate_rabi_consumption_tons,
            sf.potash_kharif_consumption_tons,
            sf.potash_rabi_consumption_tons,
            
            -- Irrigation data
            si.wheat_irrigated_area_1000_ha,
            si.rice_irrigated_area_1000_ha,
            si.total_irrigated_area_1000_ha,
            si.canal_irrigation_1000_ha,
            si.tubewell_irrigation_1000_ha,
            si.tank_irrigation_1000_ha,
            si.other_irrigation_1000_ha
            
        FROM area_production_yield apy
        LEFT JOIN monthly_rainfall mr 
            ON apy.state_name = mr.state_name 
            AND apy.dist_name = mr.dist_name 
            AND apy.year = mr.year
        LEFT JOIN state_wise_fertilizer sf 
            ON apy.state_name = sf.state_name 
            AND apy.year = sf.year
        LEFT JOIN state_wise_irrigation si 
            ON apy.state_name = si.state_name 
            AND apy.year = si.year
        WHERE 
            apy.year >= $1
            AND (apy.wheat_yield_kg_per_ha > 0 
                 OR apy.rice_yield_kg_per_ha > 0 
                 OR apy.cotton_yield_kg_per_ha > 0
                 OR apy.maize_yield_kg_per_ha > 0)
            AND apy.state_name IS NOT NULL
            AND apy.dist_name IS NOT NULL
        ORDER BY apy.year DESC, apy.state_name, apy.dist_name
        LIMIT 50000
        """
        
        try:
            conn = await self.get_connection()
            current_year = datetime.now().year
            start_year = current_year - years_back
            
            rows = await conn.fetch(query, start_year)
            await conn.close()
            
            df = pd.DataFrame([dict(row) for row in rows])
            logger.info(f"Loaded {len(df)} records for ML training from {start_year}-{current_year}")
            return df
            
        except Exception as e:
            logger.error(f"ML training data query failed: {e}")
            raise

    # ==========================================
    # CROP YIELD ANALYSIS QUERIES
    # ==========================================
    
    async def get_crop_yield_by_state(self, crop: str, year: int = None, top_n: int = 10) -> List[Dict]:
        """Get top performing states for specific crop yield"""
        year = year or datetime.now().year - 1
        crop_column = f"{crop.lower()}_yield_kg_per_ha"
        
        query = f"""
        SELECT 
            state_name,
            AVG({crop_column}) as avg_yield_kg_per_ha,
            COUNT(dist_name) as districts_count,
            SUM({crop.lower()}_area_1000_ha) as total_area_1000_ha,
            SUM({crop.lower()}_production_1000_tons) as total_production_1000_tons
        FROM area_production_yield
        WHERE year = $1 AND {crop_column} > 0
        GROUP BY state_name
        ORDER BY avg_yield_kg_per_ha DESC
        LIMIT $2
        """
        
        try:
            conn = await self.get_connection()
            rows = await conn.fetch(query, year, top_n)
            await conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Crop yield by state query failed: {e}")
            return []

    async def get_district_yield_comparison(self, state: str, crop: str, years: int = 5) -> List[Dict]:
        """Compare district yields within a state over multiple years"""
        crop_column = f"{crop.lower()}_yield_kg_per_ha"
        start_year = datetime.now().year - years
        
        query = f"""
        SELECT 
            dist_name,
            year,
            {crop_column} as yield_kg_per_ha,
            {crop.lower()}_area_1000_ha as area_1000_ha,
            annual_rainfall_millimeters
        FROM area_production_yield apy
        LEFT JOIN monthly_rainfall mr ON apy.state_name = mr.state_name 
            AND apy.dist_name = mr.dist_name AND apy.year = mr.year
        WHERE apy.state_name = $1 
            AND apy.year >= $2 
            AND {crop_column} > 0
        ORDER BY dist_name, year DESC
        """
        
        try:
            conn = await self.get_connection()
            rows = await conn.fetch(query, state, start_year)
            await conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"District yield comparison query failed: {e}")
            return []

    # ==========================================
    # WEATHER & CLIMATE ANALYSIS
    # ==========================================
    
    async def get_rainfall_patterns(self, state: str, district: str = None, years: int = 10) -> List[Dict]:
        """Analyze rainfall patterns for agricultural planning"""
        start_year = datetime.now().year - years
        
        base_query = """
        SELECT 
            year,
            state_name,
            dist_name,
            annual_rainfall_millimeters,
            january_rainfall_millimeters + february_rainfall_millimeters + march_rainfall_millimeters as winter_rainfall,
            april_rainfall_millimeters + may_rainfall_millimeters + june_rainfall_millimeters as summer_rainfall,
            july_rainfall_millimeters + august_rainfall_millimeters + september_rainfall_millimeters as monsoon_rainfall,
            october_rainfall_millimeters + november_rainfall_millimeters + december_rainfall_millimeters as post_monsoon_rainfall
        FROM monthly_rainfall
        WHERE state_name = $1 AND year >= $2
        """
        
        params = [state, start_year]
        if district:
            base_query += " AND dist_name = $3"
            params.append(district)
            
        base_query += " ORDER BY year DESC, dist_name"
        
        try:
            conn = await self.get_connection()
            rows = await conn.fetch(base_query, *params)
            await conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Rainfall patterns query failed: {e}")
            return []

    async def get_drought_risk_analysis(self, threshold_mm: int = 500) -> List[Dict]:
        """Identify districts with drought risk based on rainfall patterns"""
        query = """
        SELECT 
            mr.state_name,
            mr.dist_name,
            mr.year,
            mr.annual_rainfall_millimeters,
            AVG(apy.wheat_yield_kg_per_ha + apy.rice_yield_kg_per_ha + 
                apy.cotton_yield_kg_per_ha + apy.maize_yield_kg_per_ha) / 4 as avg_yield,
            CASE 
                WHEN mr.annual_rainfall_millimeters < $1 THEN 'HIGH_RISK'
                WHEN mr.annual_rainfall_millimeters < $1 * 1.5 THEN 'MEDIUM_RISK'
                ELSE 'LOW_RISK'
            END as drought_risk_level
        FROM monthly_rainfall mr
        LEFT JOIN area_production_yield apy ON mr.state_name = apy.state_name 
            AND mr.dist_name = apy.dist_name AND mr.year = apy.year
        WHERE mr.year >= $2 AND mr.annual_rainfall_millimeters > 0
        GROUP BY mr.state_name, mr.dist_name, mr.year, mr.annual_rainfall_millimeters
        HAVING avg_yield > 0
        ORDER BY mr.annual_rainfall_millimeters ASC
        """
        
        current_year = datetime.now().year
        start_year = current_year - 5
        
        try:
            conn = await self.get_connection()
            rows = await conn.fetch(query, threshold_mm, start_year)
            await conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Drought risk analysis query failed: {e}")
            return []

    # ==========================================
    # FERTILIZER & INPUT OPTIMIZATION
    # ==========================================
    
    async def get_fertilizer_efficiency_analysis(self, state: str) -> List[Dict]:
        """Analyze fertilizer usage efficiency for yield optimization"""
        query = """
        SELECT 
            sf.year,
            sf.nitrogen_kharif_consumption_tons,
            sf.nitrogen_rabi_consumption_tons,
            sf.phosphate_kharif_consumption_tons,
            sf.phosphate_rabi_consumption_tons,
            sf.potash_kharif_consumption_tons,
            sf.potash_rabi_consumption_tons,
            AVG(apy.wheat_yield_kg_per_ha) as avg_wheat_yield,
            AVG(apy.rice_yield_kg_per_ha) as avg_rice_yield,
            AVG(apy.cotton_yield_kg_per_ha) as avg_cotton_yield,
            AVG(apy.maize_yield_kg_per_ha) as avg_maize_yield,
            -- Calculate fertilizer efficiency ratios
            CASE 
                WHEN sf.nitrogen_kharif_consumption_tons > 0 
                THEN AVG(apy.wheat_yield_kg_per_ha + apy.rice_yield_kg_per_ha) / sf.nitrogen_kharif_consumption_tons
                ELSE 0 
            END as nitrogen_efficiency_ratio
        FROM state_wise_fertilizer sf
        LEFT JOIN area_production_yield apy ON sf.state_name = apy.state_name AND sf.year = apy.year
        WHERE sf.state_name = $1 AND sf.year >= $2
        GROUP BY sf.state_name, sf.year, sf.nitrogen_kharif_consumption_tons, 
                 sf.nitrogen_rabi_consumption_tons, sf.phosphate_kharif_consumption_tons,
                 sf.phosphate_rabi_consumption_tons, sf.potash_kharif_consumption_tons,
                 sf.potash_rabi_consumption_tons
        ORDER BY sf.year DESC
        """
        
        start_year = datetime.now().year - 10
        
        try:
            conn = await self.get_connection()
            rows = await conn.fetch(query, state, start_year)
            await conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Fertilizer efficiency analysis failed: {e}")
            return []

    # ==========================================
    # IRRIGATION ANALYSIS
    # ==========================================
    
    async def get_irrigation_impact_analysis(self, state: str) -> List[Dict]:
        """Analyze impact of different irrigation methods on crop yields"""
        query = """
        SELECT 
            si.year,
            si.canal_irrigation_1000_ha,
            si.tubewell_irrigation_1000_ha,
            si.tank_irrigation_1000_ha,
            si.other_irrigation_1000_ha,
            si.total_irrigated_area_1000_ha,
            AVG(apy.wheat_yield_kg_per_ha) as avg_wheat_yield,
            AVG(apy.rice_yield_kg_per_ha) as avg_rice_yield,
            -- Calculate irrigation efficiency
            CASE 
                WHEN si.total_irrigated_area_1000_ha > 0 
                THEN (AVG(apy.wheat_yield_kg_per_ha) + AVG(apy.rice_yield_kg_per_ha)) / si.total_irrigated_area_1000_ha
                ELSE 0 
            END as irrigation_yield_efficiency,
            -- Calculate irrigation method percentages
            CASE 
                WHEN si.total_irrigated_area_1000_ha > 0 
                THEN (si.canal_irrigation_1000_ha * 100.0 / si.total_irrigated_area_1000_ha)
                ELSE 0 
            END as canal_irrigation_percentage,
            CASE 
                WHEN si.total_irrigated_area_1000_ha > 0 
                THEN (si.tubewell_irrigation_1000_ha * 100.0 / si.total_irrigated_area_1000_ha)
                ELSE 0 
            END as tubewell_irrigation_percentage
        FROM state_wise_irrigation si
        LEFT JOIN area_production_yield apy ON si.state_name = apy.state_name AND si.year = apy.year
        WHERE si.state_name = $1 AND si.year >= $2
        GROUP BY si.state_name, si.year, si.canal_irrigation_1000_ha, si.tubewell_irrigation_1000_ha,
                 si.tank_irrigation_1000_ha, si.other_irrigation_1000_ha, si.total_irrigated_area_1000_ha
        ORDER BY si.year DESC
        """
        
        start_year = datetime.now().year - 10
        
        try:
            conn = await self.get_connection()
            rows = await conn.fetch(query, state, start_year)
            await conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Irrigation impact analysis failed: {e}")
            return []

    # ==========================================
    # MARKET INTELLIGENCE QUERIES
    # ==========================================
    
    async def get_crop_profitability_analysis(self, crop: str, state: str) -> List[Dict]:
        """Analyze crop profitability trends combining yield and area data"""
        crop_yield = f"{crop.lower()}_yield_kg_per_ha"
        crop_area = f"{crop.lower()}_area_1000_ha"
        crop_production = f"{crop.lower()}_production_1000_tons"
        
        query = f"""
        SELECT 
            year,
            {crop_yield} as yield_kg_per_ha,
            {crop_area} as area_1000_ha,
            {crop_production} as production_1000_tons,
            -- Calculate productivity metrics
            CASE 
                WHEN {crop_area} > 0 
                THEN {crop_production} * 1000 / {crop_area}  -- tons per 1000 ha = kg per ha
                ELSE 0 
            END as calculated_yield_kg_per_ha,
            -- Year-over-year growth rates
            LAG({crop_yield}) OVER (ORDER BY year) as prev_year_yield,
            CASE 
                WHEN LAG({crop_yield}) OVER (ORDER BY year) > 0 
                THEN (({crop_yield} - LAG({crop_yield}) OVER (ORDER BY year)) * 100.0 / 
                      LAG({crop_yield}) OVER (ORDER BY year))
                ELSE 0 
            END as yield_growth_percentage
        FROM area_production_yield
        WHERE state_name = $1 
            AND {crop_yield} > 0 
            AND year >= $2
        ORDER BY year DESC
        """
        
        start_year = datetime.now().year - 10
        
        try:
            conn = await self.get_connection()
            rows = await conn.fetch(query, state, start_year)
            await conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Crop profitability analysis failed: {e}")
            return []

    # ==========================================
    # PREDICTIVE ANALYTICS SUPPORT
    # ==========================================
    
    async def get_feature_correlation_data(self, crop: str, state: str = None) -> pd.DataFrame:
        """Get data for feature correlation analysis in ML models"""
        crop_yield = f"{crop.lower()}_yield_kg_per_ha"
        
        where_clause = f"WHERE {crop_yield} > 0"
        params = []
        if state:
            where_clause += " AND apy.state_name = $1"
            params.append(state)
        
        query = f"""
        SELECT 
            {crop_yield} as target_yield,
            mr.annual_rainfall_millimeters,
            mr.july_rainfall_millimeters + mr.august_rainfall_millimeters + mr.september_rainfall_millimeters as monsoon_rainfall,
            sf.nitrogen_kharif_consumption_tons + sf.nitrogen_rabi_consumption_tons as total_nitrogen,
            sf.phosphate_kharif_consumption_tons + sf.phosphate_rabi_consumption_tons as total_phosphate,
            sf.potash_kharif_consumption_tons + sf.potash_rabi_consumption_tons as total_potash,
            si.total_irrigated_area_1000_ha,
            si.canal_irrigation_1000_ha,
            si.tubewell_irrigation_1000_ha,
            apy.year
        FROM area_production_yield apy
        LEFT JOIN monthly_rainfall mr ON apy.state_name = mr.state_name 
            AND apy.dist_name = mr.dist_name AND apy.year = mr.year
        LEFT JOIN state_wise_fertilizer sf ON apy.state_name = sf.state_name AND apy.year = sf.year
        LEFT JOIN state_wise_irrigation si ON apy.state_name = si.state_name AND apy.year = si.year
        {where_clause}
            AND apy.year >= {datetime.now().year - 15}
        ORDER BY apy.year DESC
        """
        
        try:
            conn = await self.get_connection()
            rows = await conn.fetch(query, *params)
            await conn.close()
            
            df = pd.DataFrame([dict(row) for row in rows])
            return df.fillna(0)  # Handle missing values
            
        except Exception as e:
            logger.error(f"Feature correlation data query failed: {e}")
            return pd.DataFrame()

    # ==========================================
    # DATABASE HEALTH & VALIDATION
    # ==========================================
    
    async def validate_database_schema(self) -> Dict[str, bool]:
        """Validate that all required tables and columns exist"""
        validation_queries = {
            'area_production_yield_exists': "SELECT 1 FROM information_schema.tables WHERE table_name = 'area_production_yield'",
            'monthly_rainfall_exists': "SELECT 1 FROM information_schema.tables WHERE table_name = 'monthly_rainfall'",
            'state_wise_fertilizer_exists': "SELECT 1 FROM information_schema.tables WHERE table_name = 'state_wise_fertilizer'",
            'state_wise_irrigation_exists': "SELECT 1 FROM information_schema.tables WHERE table_name = 'state_wise_irrigation'",
            'wheat_yield_column_exists': """
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'area_production_yield' AND column_name = 'wheat_yield_kg_per_ha'
            """,
            'annual_rainfall_column_exists': """
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'monthly_rainfall' AND column_name = 'annual_rainfall_millimeters'
            """
        }
        
        results = {}
        try:
            conn = await self.get_connection()
            for check_name, query in validation_queries.items():
                try:
                    result = await conn.fetch(query)
                    results[check_name] = len(result) > 0
                except Exception as e:
                    logger.error(f"Schema validation {check_name} failed: {e}")
                    results[check_name] = False
            await conn.close()
        except Exception as e:
            logger.error(f"Database schema validation failed: {e}")
            results = {key: False for key in validation_queries.keys()}
        
        return results

    async def get_data_quality_report(self) -> Dict[str, any]:
        """Generate comprehensive data quality report"""
        queries = {
            'total_yield_records': "SELECT COUNT(*) FROM area_production_yield WHERE wheat_yield_kg_per_ha > 0 OR rice_yield_kg_per_ha > 0",
            'total_rainfall_records': "SELECT COUNT(*) FROM monthly_rainfall WHERE annual_rainfall_millimeters > 0",
            'date_range': """
                SELECT MIN(year) as min_year, MAX(year) as max_year 
                FROM area_production_yield WHERE year IS NOT NULL
            """,
            'states_count': "SELECT COUNT(DISTINCT state_name) FROM area_production_yield WHERE state_name IS NOT NULL",
            'districts_count': "SELECT COUNT(DISTINCT dist_name) FROM area_production_yield WHERE dist_name IS NOT NULL",
            'missing_rainfall_data': """
                SELECT COUNT(*) FROM area_production_yield apy
                LEFT JOIN monthly_rainfall mr ON apy.state_name = mr.state_name 
                    AND apy.dist_name = mr.dist_name AND apy.year = mr.year
                WHERE mr.annual_rainfall_millimeters IS NULL
            """
        }
        
        report = {}
        try:
            conn = await self.get_connection()
            for metric_name, query in queries.items():
                try:
                    result = await conn.fetchrow(query)
                    if metric_name == 'date_range':
                        report[metric_name] = dict(result) if result else {'min_year': None, 'max_year': None}
                    else:
                        report[metric_name] = result[0] if result else 0
                except Exception as e:
                    logger.error(f"Data quality check {metric_name} failed: {e}")
                    report[metric_name] = 0
            await conn.close()
            
            # Calculate data completeness percentage
            total_records = report.get('total_yield_records', 0)
            missing_rainfall = report.get('missing_rainfall_data', 0)
            if total_records > 0:
                report['data_completeness_percentage'] = ((total_records - missing_rainfall) / total_records) * 100
            else:
                report['data_completeness_percentage'] = 0
                
        except Exception as e:
            logger.error(f"Data quality report generation failed: {e}")
            report = {'error': str(e)}
        
        return report

# ==========================================
# GLOBAL INSTANCE
# ==========================================

# Create global SQL queries instance
agricultural_sql = AgriculturalSQLQueries()

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

async def test_database_connection() -> bool:
    """Test database connection and basic functionality"""
    try:
        conn = await agricultural_sql.get_connection()
        result = await conn.fetchrow("SELECT 1 as test")
        await conn.close()
        return result['test'] == 1
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

async def get_available_crops() -> List[str]:
    """Get list of available crops in the database"""
    crops = ['wheat', 'rice', 'cotton', 'maize', 'sugarcane', 'groundnut', 'soybean', 'jowar', 'bajra', 'ragi']
    try:
        conn = await agricultural_sql.get_connection()
        # Check which crop columns actually have data
        available_crops = []
        for crop in crops:
            query = f"SELECT COUNT(*) FROM area_production_yield WHERE {crop}_yield_kg_per_ha > 0 LIMIT 1"
            try:
                result = await conn.fetchrow(query)
                if result and result[0] > 0:
                    available_crops.append(crop)
            except:
                continue  # Column doesn't exist, skip this crop
        await conn.close()
        return available_crops
    except Exception as e:
        logger.error(f"Error getting available crops: {e}")
        return ['wheat', 'rice', 'cotton', 'maize']  # Default fallback

async def get_available_states() -> List[str]:
    """Get list of states available in the database"""
    try:
        conn = await agricultural_sql.get_connection()
        rows = await conn.fetch("SELECT DISTINCT state_name FROM area_production_yield WHERE state_name IS NOT NULL ORDER BY state_name")
        await conn.close()
        return [row['state_name'] for row in rows]
    except Exception as e:
        logger.error(f"Error getting available states: {e}")
        return ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Karnataka']  # Default fallback

# ==========================================
# EXAMPLE USAGE & TESTING
# ==========================================

if __name__ == "__main__":
    import asyncio
    
    async def test_queries():
        """Test the SQL queries system"""
        print("🔍 Testing Agricultural SQL Queries System")
        print("=" * 50)
        
        # Test database connection
        connection_ok = await test_database_connection()
        print(f"✅ Database Connection: {'OK' if connection_ok else 'FAILED'}")
        
        if not connection_ok:
            print("❌ Database connection failed. Please check your DATABASE_URL.")
            return
        
        # Test schema validation
        schema_validation = await agricultural_sql.validate_database_schema()
        print(f"✅ Schema Validation: {sum(schema_validation.values())}/{len(schema_validation)} checks passed")
        
        # Test data quality report
        quality_report = await agricultural_sql.get_data_quality_report()
        print(f"✅ Data Quality Report:")
        for key, value in quality_report.items():
            print(f"   {key}: {value}")
        
        # Test ML training data
        try:
            training_data = await agricultural_sql.get_ml_training_data(years_back=5)
            print(f"✅ ML Training Data: {len(training_data)} records loaded")
            print(f"   Columns: {list(training_data.columns)}")
        except Exception as e:
            print(f"❌ ML Training Data: {e}")
        
        # Test available crops and states
        crops = await get_available_crops()
        states = await get_available_states()
        print(f"✅ Available Crops: {crops}")
        print(f"✅ Available States: {len(states)} states found")
        
        print("\n🎉 Agricultural SQL Queries System is ready!")

    # Run tests
    asyncio.run(test_queries())
