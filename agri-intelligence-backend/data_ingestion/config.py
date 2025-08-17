"""
WORKING Configuration for Agricultural Intelligence Data Ingestion Pipeline
"""
from pathlib import Path
from typing import List, Optional
import os

# Force load .env FIRST
from dotenv import load_dotenv
load_dotenv(override=True)

# Pydantic v2 imports
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class AgriculturalIngestionConfig(BaseSettings):
    """WORKING Configuration class"""
    
    # EXPLICIT environment variable mapping - this is the key!
    database_url: str = Field(
        default="postgresql://agri_user:agri_password@localhost:5432/agri_db",
        description="Database URL"
    )
    
    jina_api_key: str = Field(
        ...,  # Required
        description="Jina AI API key"
    )
    
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Gemini API key (optional)"
    )
    
    # Data directories
    csv_directory: Path = Field(default=Path('./data/raw/csvs'))
    pdf_directory: Path = Field(default=Path('./data/raw/pdfs'))
    output_directory: Path = Field(default=Path('./data/processed'))
    
    # Processing config
    chunk_size: int = Field(default=1500, ge=500, le=4000)
    overlap: int = Field(default=200, ge=50, le=500)
    
    # Agricultural crops
    supported_crops: List[str] = Field(
        default=[
            'wheat', 'rice', 'maize', 'barley', 'millet', 'sorghum',
            'cotton', 'sugarcane', 'jute', 'tea', 'coffee',
            'groundnut', 'mustard', 'sesame', 'sunflower', 'soybean',
            'gram', 'arhar', 'moong', 'urad', 'masoor',
            'potato', 'onion', 'garlic', 'tomato', 'brinjal'
        ]
    )
    
    # PYDANTIC V2 CONFIGURATION - THIS IS CRITICAL!
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,  # Allow case insensitive matching
        extra='ignore'
    )
    
    @field_validator('csv_directory', 'pdf_directory', 'output_directory')
    @classmethod
    def validate_directories(cls, v):
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

def test_config():
    """Test configuration loading"""
    print("🧪 Testing Configuration Loading...")
    
    # Check environment variables
    print(f"JINA_API_KEY in environment: {bool(os.getenv('JINA_API_KEY'))}")
    print(f"DATABASE_URL in environment: {bool(os.getenv('DATABASE_URL'))}")
    
    # Try to load config
    try:
        config = AgriculturalIngestionConfig()
        print("✅ Configuration loaded successfully!")
        print(f"Jina API Key length: {len(config.jina_api_key)} characters")
        print(f"Database URL: {config.database_url.split('@')[-1] if '@' in config.database_url else config.database_url}")
        return config
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return None

def validate_setup():
    """Validate complete setup"""
    config = test_config()
    if not config:
        return False
    
    print("\n🔍 Validating Setup...")
    
    # Check directories
    csv_exists = config.csv_directory.exists()
    pdf_exists = config.pdf_directory.exists()
    print(f"📁 CSV Directory: {config.csv_directory} {'✅' if csv_exists else '❌'}")
    print(f"📁 PDF Directory: {config.pdf_directory} {'✅' if pdf_exists else '❌'}")
    
    # Check data files
    csv_files = list(config.csv_directory.glob('*.csv')) if csv_exists else []
    pdf_files = list(config.pdf_directory.glob('*.pdf')) if pdf_exists else []
    print(f"📊 CSV Files: {len(csv_files)}")
    print(f"📚 PDF Files: {len(pdf_files)}")
    
    # Overall validation
    all_good = bool(config.jina_api_key) and (len(csv_files) > 0 or len(pdf_files) > 0)
    print(f"\n🎯 Overall Status: {'✅ READY FOR INGESTION!' if all_good else '❌ Issues detected'}")
    
    return all_good

# Create global config instance
try:
    config = AgriculturalIngestionConfig()
    print("✅ Global config loaded successfully")
except Exception as e:
    print(f"⚠️ Global config failed: {e}")
    config = None

if __name__ == "__main__":
    print("🌾 Agricultural Intelligence - Configuration Test")
    print("="*60)
    
    validate_setup()
