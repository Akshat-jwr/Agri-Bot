"""
COMPLETE Agricultural Database Setup - ALL CSV tables + Document Vectors
FIXED VERSION - Including all missing tables and ChromaDB metadata
"""
import asyncpg
import asyncio
import chromadb
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def fix_database_url_for_asyncpg(url: str) -> str:
    """Convert SQLAlchemy-style URL to asyncpg-compatible URL"""
    if url.startswith('postgresql+asyncpg://'):
        return url.replace('postgresql+asyncpg://', 'postgresql://')
    elif url.startswith('postgres+asyncpg://'):
        return url.replace('postgres+asyncpg://', 'postgres://')
    return url

async def setup_complete_agricultural_database():
    """Setup COMPLETE database with ALL your CSV tables + Document vectors"""
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres@localhost:5433/agri_db')
    asyncpg_url = fix_database_url_for_asyncpg(DATABASE_URL)
    
    try:
        conn = await asyncpg.connect(asyncpg_url)
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Setup ChromaDB for document vectors
    try:
        chroma_path = os.getenv('CHROMADB_PATH', './agri_vectordb')
        chroma_client = chromadb.PersistentClient(path=chroma_path)
        collection = chroma_client.get_or_create_collection(
            name="agricultural_documents",
            metadata={
                "description": "Agricultural PDFs and Reports",
                "version": "1.0",
                "created_for": "Indian Agricultural Intelligence",
                "active": True
            }
        )
        print("✅ ChromaDB ready for document vectors")
    except Exception as e:
        print(f"⚠️  ChromaDB setup warning: {e}")
    
    try:
        print("🚀 Creating COMPLETE schema for ALL your CSV files...")
        
        async with conn.transaction():
            
            # ✅ area-production-yield.csv (EXISTING - same as before)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS area_production_yield (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER,
                    year INTEGER,
                    state_code INTEGER,
                    state_name VARCHAR(100),
                    dist_name VARCHAR(100),
                    rice_area_1000_ha FLOAT, rice_production_1000_tons FLOAT, rice_yield_kg_per_ha FLOAT,
                    wheat_area_1000_ha FLOAT, wheat_production_1000_tons FLOAT, wheat_yield_kg_per_ha FLOAT,
                    kharif_sorghum_area_1000_ha FLOAT, kharif_sorghum_production_1000_tons FLOAT, kharif_sorghum_yield_kg_per_ha FLOAT,
                    rabi_sorghum_area_1000_ha FLOAT, rabi_sorghum_production_1000_tons FLOAT, rabi_sorghum_yield_kg_per_ha FLOAT,
                    sorghum_area_1000_ha FLOAT, sorghum_production_1000_tons FLOAT, sorghum_yield_kg_per_ha FLOAT,
                    pearl_millet_area_1000_ha FLOAT, pearl_millet_production_1000_tons FLOAT, pearl_millet_yield_kg_per_ha FLOAT,
                    maize_area_1000_ha FLOAT, maize_production_1000_tons FLOAT, maize_yield_kg_per_ha FLOAT,
                    finger_millet_area_1000_ha FLOAT, finger_millet_production_1000_tons FLOAT, finger_millet_yield_kg_per_ha FLOAT,
                    barley_area_1000_ha FLOAT, barley_production_1000_tons FLOAT, barley_yield_kg_per_ha FLOAT,
                    chickpea_area_1000_ha FLOAT, chickpea_production_1000_tons FLOAT, chickpea_yield_kg_per_ha FLOAT,
                    pigeonpea_area_1000_ha FLOAT, pigeonpea_production_1000_tons FLOAT, pigeonpea_yield_kg_per_ha FLOAT,
                    minor_pulses_area_1000_ha FLOAT, minor_pulses_production_1000_tons FLOAT, minor_pulses_yield_kg_per_ha FLOAT,
                    groundnut_area_1000_ha FLOAT, groundnut_production_1000_tons FLOAT, groundnut_yield_kg_per_ha FLOAT,
                    sesamum_area_1000_ha FLOAT, sesamum_production_1000_tons FLOAT, sesamum_yield_kg_per_ha FLOAT,
                    rapeseed_and_mustard_area_1000_ha FLOAT, rapeseed_and_mustard_production_1000_tons FLOAT, rapeseed_and_mustard_yield_kg_per_ha FLOAT,
                    safflower_area_1000_ha FLOAT, safflower_production_1000_tons FLOAT, safflower_yield_kg_per_ha FLOAT,
                    castor_area_1000_ha FLOAT, castor_production_1000_tons FLOAT, castor_yield_kg_per_ha FLOAT,
                    linseed_area_1000_ha FLOAT, linseed_production_1000_tons FLOAT, linseed_yield_kg_per_ha FLOAT,
                    sunflower_area_1000_ha FLOAT, sunflower_production_1000_tons FLOAT, sunflower_yield_kg_per_ha FLOAT,
                    soyabean_area_1000_ha FLOAT, soyabean_production_1000_tons FLOAT, soyabean_yield_kg_per_ha FLOAT,
                    oilseeds_area_1000_ha FLOAT, oilseeds_production_1000_tons FLOAT, oilseeds_yield_kg_per_ha FLOAT,
                    sugarcane_area_1000_ha FLOAT, sugarcane_production_1000_tons FLOAT, sugarcane_yield_kg_per_ha FLOAT,
                    cotton_area_1000_ha FLOAT, cotton_production_1000_tons FLOAT, cotton_yield_kg_per_ha FLOAT,
                    fruits_area_1000_ha FLOAT, vegetables_area_1000_ha FLOAT, fruits_and_vegetables_area_1000_ha FLOAT,
                    potatoes_area_1000_ha FLOAT, onion_area_1000_ha FLOAT, fodder_area_1000_ha FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            print("✅ Created area_production_yield table")
            
            # ✅ NEW: State-wise-Crop-Yield-data.csv (same structure as area-production-yield)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS state_wise_crop_yield (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER,
                    year INTEGER,
                    state_code INTEGER,
                    state_name VARCHAR(100),
                    dist_name VARCHAR(100),
                    rice_area_1000_ha FLOAT, rice_production_1000_tons FLOAT, rice_yield_kg_per_ha FLOAT,
                    wheat_area_1000_ha FLOAT, wheat_production_1000_tons FLOAT, wheat_yield_kg_per_ha FLOAT,
                    kharif_sorghum_area_1000_ha FLOAT, kharif_sorghum_production_1000_tons FLOAT, kharif_sorghum_yield_kg_per_ha FLOAT,
                    rabi_sorghum_area_1000_ha FLOAT, rabi_sorghum_production_1000_tons FLOAT, rabi_sorghum_yield_kg_per_ha FLOAT,
                    sorghum_area_1000_ha FLOAT, sorghum_production_1000_tons FLOAT, sorghum_yield_kg_per_ha FLOAT,
                    pearl_millet_area_1000_ha FLOAT, pearl_millet_production_1000_tons FLOAT, pearl_millet_yield_kg_per_ha FLOAT,
                    maize_area_1000_ha FLOAT, maize_production_1000_tons FLOAT, maize_yield_kg_per_ha FLOAT,
                    finger_millet_area_1000_ha FLOAT, finger_millet_production_1000_tons FLOAT, finger_millet_yield_kg_per_ha FLOAT,
                    barley_area_1000_ha FLOAT, barley_production_1000_tons FLOAT, barley_yield_kg_per_ha FLOAT,
                    chickpea_area_1000_ha FLOAT, chickpea_production_1000_tons FLOAT, chickpea_yield_kg_per_ha FLOAT,
                    pigeonpea_area_1000_ha FLOAT, pigeonpea_production_1000_tons FLOAT, pigeonpea_yield_kg_per_ha FLOAT,
                    minor_pulses_area_1000_ha FLOAT, minor_pulses_production_1000_tons FLOAT, minor_pulses_yield_kg_per_ha FLOAT,
                    groundnut_area_1000_ha FLOAT, groundnut_production_1000_tons FLOAT, groundnut_yield_kg_per_ha FLOAT,
                    sesamum_area_1000_ha FLOAT, sesamum_production_1000_tons FLOAT, sesamum_yield_kg_per_ha FLOAT,
                    rapeseed_and_mustard_area_1000_ha FLOAT, rapeseed_and_mustard_production_1000_tons FLOAT, rapeseed_and_mustard_yield_kg_per_ha FLOAT,
                    safflower_area_1000_ha FLOAT, safflower_production_1000_tons FLOAT, safflower_yield_kg_per_ha FLOAT,
                    castor_area_1000_ha FLOAT, castor_production_1000_tons FLOAT, castor_yield_kg_per_ha FLOAT,
                    linseed_area_1000_ha FLOAT, linseed_production_1000_tons FLOAT, linseed_yield_kg_per_ha FLOAT,
                    sunflower_area_1000_ha FLOAT, sunflower_production_1000_tons FLOAT, sunflower_yield_kg_per_ha FLOAT,
                    soyabean_area_1000_ha FLOAT, soyabean_production_1000_tons FLOAT, soyabean_yield_kg_per_ha FLOAT,
                    oilseeds_area_1000_ha FLOAT, oilseeds_production_1000_tons FLOAT, oilseeds_yield_kg_per_ha FLOAT,
                    sugarcane_area_1000_ha FLOAT, sugarcane_production_1000_tons FLOAT, sugarcane_yield_kg_per_ha FLOAT,
                    cotton_area_1000_ha FLOAT, cotton_production_1000_tons FLOAT, cotton_yield_kg_per_ha FLOAT,
                    fruits_area_1000_ha FLOAT, vegetables_area_1000_ha FLOAT, fruits_and_vegetables_area_1000_ha FLOAT,
                    potatoes_area_1000_ha FLOAT, onion_area_1000_ha FLOAT, fodder_area_1000_ha FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            print("✅ Created state_wise_crop_yield table")
            
            # ✅ NEW: State-wise-fertilizer-data.csv
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS state_wise_fertilizer (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER,
                    year INTEGER,
                    state_code INTEGER,
                    state_name VARCHAR(100),
                    dist_name VARCHAR(100),
                    nitrogen_kharif_consumption_tons FLOAT,
                    nitrogen_rabi_consumption_tons FLOAT,
                    phosphate_kharif_consumption_tons FLOAT,
                    phosphate_rabi_consumption_tons FLOAT,
                    potash_kharif_consumption_tons FLOAT,
                    potash_rabi_consumption_tons FLOAT,
                    total_kharif_consumption_tons FLOAT,
                    total_rabi_consumption_tons FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            print("✅ Created state_wise_fertilizer table")
            
            # ✅ NEW: State-wise-high-yielding-crops.csv
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS state_wise_high_yielding_crops (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER,
                    year INTEGER,
                    state_code INTEGER,
                    state_name VARCHAR(100),
                    dist_name VARCHAR(100),
                    rice_area_1000_ha FLOAT,
                    wheat_area_1000_ha FLOAT,
                    sorghum_area_1000_ha FLOAT,
                    pearl_millet_area_1000_ha FLOAT,
                    maize_area_1000_ha FLOAT,
                    finger_millet_area_1000_ha FLOAT,
                    total_area_1000_ha FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            print("✅ Created state_wise_high_yielding_crops table")
            
            # ✅ NEW: State-wise-infrastructure-data.csv
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS state_wise_infrastructure (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER,
                    year INTEGER,
                    state_code INTEGER,
                    state_name VARCHAR(100),
                    dist_name VARCHAR(100),
                    banks_number_number INTEGER,
                    post_offices_number_number INTEGER,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            print("✅ Created state_wise_infrastructure table")
            
            # ✅ NEW: State-wise-irrigation-data.csv
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS state_wise_irrigation (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER,
                    year INTEGER,
                    state_code INTEGER,
                    state_name VARCHAR(100),
                    dist_name VARCHAR(100),
                    rice_irrigated_area_1000_ha FLOAT,
                    wheat_irrigated_area_1000_ha FLOAT,
                    kharif_sorghum_irrigated_area_1000_ha FLOAT,
                    rabi_sorghum_irrigated_area_1000_ha FLOAT,
                    sorghum_irrigated_area_1000_ha FLOAT,
                    pearl_millet_irrigated_area_1000_ha FLOAT,
                    maize_irrigated_area_1000_ha FLOAT,
                    finger_millet_irrigated_area_1000_ha FLOAT,
                    barley_irrigated_area_1000_ha FLOAT,
                    chickpea_irrigated_area_1000_ha FLOAT,
                    pigeonpea_irrigated_area_1000_ha FLOAT,
                    minor_pulses_irrigated_area_1000_ha FLOAT,
                    pulses_irrigated_area_1000_ha FLOAT,
                    groundnut_irrigated_area_1000_ha FLOAT,
                    sesamum_irrigated_area_1000_ha FLOAT,
                    linseed_irrigated_area_1000_ha FLOAT,
                    sugarcane_irrigated_area_1000_ha FLOAT,
                    cotton_irrigated_area_1000_ha FLOAT,
                    fruits_and_vegetables_irrigated_area_1000_ha FLOAT,
                    fodder_irrigated_area_1000_ha FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            print("✅ Created state_wise_irrigation table")
            
            # ✅ Keep existing tables (Census, market data, etc. from previous setup)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS census_data (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER, year INTEGER, state_code INTEGER,
                    state_name VARCHAR(100), dist_name VARCHAR(100),
                    total_population_1000_number FLOAT, total_male_population_1000_number FLOAT, total_female_population_1000_number FLOAT,
                    total_rural_population_1000_number FLOAT, rural_male_population_1000_number FLOAT, rural_female_population_1000_number FLOAT,
                    total_urban_population_1000_number FLOAT, urban_male_population_1000_number FLOAT, urban_female_population_1000_number FLOAT,
                    st_total_population_1000_number FLOAT, st_male_population_1000_number FLOAT, st_female_population_1000_number FLOAT,
                    st_rural_total_population_1000_number FLOAT, st_rural_male_population_1000_number FLOAT, st_rural_female_population_1000_number FLOAT,
                    st_urban_total_population_1000_number FLOAT, st_urban_male_population_1000_number FLOAT, st_urban_female_population_1000_number FLOAT,
                    sc_total_population_1000_number FLOAT, sc_male_population_1000_number FLOAT, sc_female_population_1000_number FLOAT,
                    sc_rural_total_population_1000_number FLOAT, sc_rural_male_population_1000_number FLOAT, sc_rural_female_population_1000_number FLOAT,
                    sc_urban_total_population_1000_number FLOAT, sc_urban_male_population_1000_number FLOAT, sc_urban_female_population_1000_number FLOAT,
                    total_literates_population_1000_number FLOAT, male_literates_population_1000_number FLOAT, female_literates_population_1000_number FLOAT,
                    total_rural_literates_population_1000_number FLOAT, rural_male_literates_population_1000_number FLOAT, rural_female_literates_population_1000_number FLOAT,
                    total_urban_literates_population_1000_number FLOAT, urban_male_literates_population_1000_number FLOAT, urban_female_literates_population_1000_number FLOAT,
                    total_cultivators_population_1000_number FLOAT, male_cultivators_population_1000_number FLOAT, female_cultivators_population_1000_number FLOAT,
                    total_rural_cultivators_population_1000_number FLOAT, rural_male_cultivators_population_1000_number FLOAT, rural_female_cultivators_population_1000_number FLOAT,
                    total_urban_cultivators_population_1000_number FLOAT, urban_male_cultivators_population_1000_number FLOAT, urban_female_cultivators_population_1000_number FLOAT,
                    total_agricultural_labour_population_1000_number FLOAT, male_agricultural_labour_population_1000_number FLOAT, female_agricultural_labour_population_1000_number FLOAT,
                    total_rural_agricultural_labour_population_1000_number FLOAT, rural_male_agricultural_labour_population_1000_number FLOAT, rural_female_agricultural_labour_population_1000_number FLOAT,
                    total_urban_agricultural_labour_population_1000_number FLOAT, urban_male_agricultural_labour_population_1000_number FLOAT, urban_female_agricultural_labour_population_1000_number FLOAT,
                    non_agricultural_workers_population_1000_number FLOAT, agricultural_workers_population_1000_number FLOAT, total_workers_population_1000_number FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    id SERIAL PRIMARY KEY,
                    state VARCHAR(100), district VARCHAR(100), market VARCHAR(200),
                    commodity VARCHAR(100), variety VARCHAR(100), arrival_date DATE,
                    min_price FLOAT, max_price FLOAT, modal_price FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS growing_period (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER, year INTEGER, state_code INTEGER,
                    state_name VARCHAR(100), dist_name VARCHAR(100),
                    length_of_growing_period_days_number INTEGER,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS harvest_price_data (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER, year INTEGER, state_code INTEGER,
                    state_name VARCHAR(100), dist_name VARCHAR(100),
                    rice_harvest_price_rs_per_quintal FLOAT, paddy_harvest_price_rs_per_quintal FLOAT,
                    wheat_harvest_price_rs_per_quintal FLOAT, sorghum_harvest_price_rs_per_quintal FLOAT,
                    pearl_millet_harvest_price_rs_per_quintal FLOAT, maize_harvest_price_rs_per_quintal FLOAT,
                    finger_millet_harvest_price_rs_per_quintal FLOAT, barley_harvest_price_rs_per_quintal FLOAT,
                    chickpea_harvest_price_rs_per_quintal FLOAT, pigeonpea_harvest_price_rs_per_quintal FLOAT,
                    groundnut_harvest_price_rs_per_quintal FLOAT, seasmum_harvest_price_rs_per_quintal FLOAT,
                    rape_and_mustard_harvest_price_rs_per_quintal FLOAT, castor_harvest_price_rs_per_quintal FLOAT,
                    linseed_harvest_price_rs_per_quintal FLOAT, sugarcane_gur_harvest_price_rs_per_quintal FLOAT,
                    cotton_kapas_harvest_price_rs_per_quintal FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS high_yielding_varieties (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER, year INTEGER, state_code INTEGER,
                    state_name VARCHAR(100), dist_name VARCHAR(100),
                    rice_area_1000_ha FLOAT, wheat_area_1000_ha FLOAT, sorghum_area_1000_ha FLOAT,
                    pearl_millet_area_1000_ha FLOAT, maize_area_1000_ha FLOAT, finger_millet_area_1000_ha FLOAT,
                    total_area_1000_ha FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS landuse_data (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER, year INTEGER, state_code INTEGER,
                    state_name VARCHAR(100), dist_name VARCHAR(100),
                    total_area_1000_ha FLOAT, forest_area_1000_ha FLOAT,
                    barren_and_uncultivable_land_area_1000_ha FLOAT, land_put_to_nonagricultural_use_area_1000_ha FLOAT,
                    cultivable_waste_land_area_1000_ha FLOAT, permanent_pastures_area_1000_ha FLOAT,
                    other_fallow_area_1000_ha FLOAT, current_fallow_area_1000_ha FLOAT,
                    net_cropped_area_1000_ha FLOAT, gross_cropped_area_1000_ha FLOAT, croping_intensity_percent FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS monthly_rainfall (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER, year INTEGER, state_code INTEGER,
                    state_name VARCHAR(100), dist_name VARCHAR(100),
                    january_rainfall_millimeters FLOAT, february_rainfall_millimeters FLOAT, march_rainfall_millimeters FLOAT,
                    april_rainfall_millimeters FLOAT, may_rainfall_millimeters FLOAT, june_rainfall_millimeters FLOAT,
                    july_rainfall_millimeters FLOAT, august_rainfall_millimeters FLOAT, september_rainfall_millimeters FLOAT,
                    october_rainfall_millimeters FLOAT, november_rainfall_millimeters FLOAT, december_rainfall_millimeters FLOAT,
                    annual_rainfall_millimeters FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS normal_rainfall (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER, year INTEGER, state_code INTEGER,
                    state_name VARCHAR(100), dist_name VARCHAR(100),
                    january_normal_rainfall_millimeters FLOAT, february_normal_rainfall_millimeters FLOAT, march_normal_rainfall_millimeters FLOAT,
                    april_normal_rainfall_millimeters FLOAT, may_normal_rainfall_millimeters FLOAT, june_normal_rainfall_millimeters FLOAT,
                    july_normal_rainfall_millimeters FLOAT, august_normal_rainfall_millimeters FLOAT, september_normal_rainfall_millimeters FLOAT,
                    october_normal_rainfall_millimeters FLOAT, november_normal_rainfall_millimeters FLOAT, december_normal_rainfall_millimeters FLOAT,
                    annual_normal_rainfall_millimeters FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS soil_type_data (
                    id SERIAL PRIMARY KEY,
                    dist_code INTEGER, year INTEGER, state_code INTEGER,
                    state_name VARCHAR(100), dist_name VARCHAR(100),
                    soil_type_percent_percent FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # ✅ NEW: Document metadata table for ChromaDB integration
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS document_metadata (
                    id SERIAL PRIMARY KEY,
                    chromadb_id VARCHAR(255) UNIQUE NOT NULL,
                    source_file VARCHAR(255) NOT NULL,
                    source_type VARCHAR(50) NOT NULL DEFAULT 'pdf',
                    chunk_index INTEGER NOT NULL,
                    total_chunks INTEGER NOT NULL,
                    
                    -- Agricultural context extracted from documents
                    crops_mentioned TEXT[],
                    states_mentioned TEXT[],
                    topics_covered TEXT[],
                    
                    -- Document metadata
                    file_size_bytes BIGINT,
                    text_length INTEGER,
                    word_count INTEGER,
                    
                    -- Processing info
                    processing_timestamp TIMESTAMP DEFAULT NOW(),
                    embedding_model VARCHAR(100) DEFAULT 'jina-embeddings-v2-base-en',
                    
                    -- Relations to structured data
                    related_crop_data_ids INTEGER[],
                    related_market_data_ids INTEGER[],
                    related_weather_data_ids INTEGER[],
                    
                    created_at TIMESTAMP DEFAULT NOW(),
                    
                    UNIQUE(source_file, chunk_index)
                )
            """)
            print("✅ Created document_metadata table for ChromaDB integration")
            
            print("✅ Created all remaining tables (census, market, rainfall, etc.)")
            
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_area_prod_state_year ON area_production_yield(state_name, year)",
                "CREATE INDEX IF NOT EXISTS idx_state_crop_yield_state_year ON state_wise_crop_yield(state_name, year)",
                "CREATE INDEX IF NOT EXISTS idx_fertilizer_state_year ON state_wise_fertilizer(state_name, year)",
                "CREATE INDEX IF NOT EXISTS idx_irrigation_state_year ON state_wise_irrigation(state_name, year)",
                "CREATE INDEX IF NOT EXISTS idx_infrastructure_state_year ON state_wise_infrastructure(state_name, year)",
                "CREATE INDEX IF NOT EXISTS idx_market_commodity_date ON market_data(commodity, arrival_date)",
                "CREATE INDEX IF NOT EXISTS idx_rainfall_state_year ON monthly_rainfall(state_name, year)",
                "CREATE INDEX IF NOT EXISTS idx_harvest_price_state_year ON harvest_price_data(state_name, year)",
                "CREATE INDEX IF NOT EXISTS idx_doc_metadata_source ON document_metadata(source_file)",
                "CREATE INDEX IF NOT EXISTS idx_doc_metadata_crops ON document_metadata USING gin(crops_mentioned)",
                "CREATE INDEX IF NOT EXISTS idx_doc_metadata_states ON document_metadata USING gin(states_mentioned)",
                "CREATE INDEX IF NOT EXISTS idx_doc_metadata_topics ON document_metadata USING gin(topics_covered)"
            ]
            
            for index_sql in indexes:
                await conn.execute(index_sql)
            
            print("✅ Created performance indexes")
        
        print("\n🎉 COMPLETE database setup finished!")
        print("📊 ALL Tables created:")
        print("   📈 area_production_yield - District-wise crop production")
        print("   📈 state_wise_crop_yield - State-wise crop yield data")
        print("   🧪 state_wise_fertilizer - Fertilizer consumption by season")
        print("   🌾 state_wise_high_yielding_crops - HYV crop areas")
        print("   🏗️  state_wise_infrastructure - Banks & post offices")
        print("   💧 state_wise_irrigation - Irrigation by crop")
        print("   👥 census_data - Population demographics")
        print("   💰 market_data - Daily market prices")
        print("   🌱 growing_period - Growing season length")
        print("   💵 harvest_price_data - Harvest prices")
        print("   🌾 high_yielding_varieties - HYV areas")
        print("   🌍 landuse_data - Land utilization")
        print("   🌧️  monthly_rainfall - Monthly precipitation")
        print("   🌧️  normal_rainfall - Normal precipitation")
        print("   🌱 soil_type_data - Soil characteristics")
        print("   📄 document_metadata - PDF document tracking")
        print("\n🗂️  ChromaDB ready for document vectors")
        print("🎯 Your complete Agricultural Intelligence database is ready!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(setup_complete_agricultural_database())
