"""Main runner script for agricultural data ingestion pipeline"""
import asyncio
import logging
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from data_ingestion.pipeline_manager import AgriculturalDataPipeline

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data_ingestion.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def fix_database_url_for_asyncpg(url: str) -> str:
    """Convert SQLAlchemy-style URL to asyncpg-compatible URL"""
    if url.startswith('postgresql+asyncpg://'):
        return url.replace('postgresql+asyncpg://', 'postgresql://')
    elif url.startswith('postgres+asyncpg://'):
        return url.replace('postgres+asyncpg://', 'postgres://')
    return url

def load_config():
    """Load configuration from environment variables"""
    
    config = {
        'database_url': os.getenv('DATABASE_URL', 'postgresql://postgres@localhost:5433/agri_db'),
        'jina_api_key': os.getenv('JINA_API_KEY'),
        'chromadb_path': os.getenv('CHROMADB_PATH', './agri_vectordb'),
        'csv_directory': os.getenv('CSV_DIRECTORY', './data/raw/csvs'),
        'pdf_directory': os.getenv('PDF_DIRECTORY', './data/raw/pdfs'),           # ✅ FIXED: PDFs are in raw/
        'output_directory': os.getenv('OUTPUT_DIRECTORY', './data/processed'),
        'chunk_size': int(os.getenv('CHUNK_SIZE', '1500')),
        'overlap': int(os.getenv('OVERLAP', '200')),
        'batch_size': int(os.getenv('BATCH_SIZE', '100'))
    }
    
    # ✅ FIXED: Convert database URL for asyncpg compatibility
    config['database_url'] = fix_database_url_for_asyncpg(config['database_url'])
    
    return config

def validate_environment(config):
    """Validate required environment variables and directories"""
    errors = []
    warnings = []
    
    # Check required environment variables
    if not config['database_url']:
        errors.append("DATABASE_URL not found in environment")
        
    if not config['jina_api_key']:
        warnings.append("JINA_API_KEY not found - vector embeddings may not work")
    
    # Check directories exist
    csv_dir = Path(config['csv_directory'])
    pdf_dir = Path(config['pdf_directory'])
    
    if not csv_dir.exists():
        errors.append(f"CSV directory does not exist: {csv_dir}")
        
    if not pdf_dir.exists():
        errors.append(f"PDF directory does not exist: {pdf_dir}")
    
    return errors, warnings

async def main():
    """Main function to run the data ingestion pipeline"""
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🌾 Agricultural Intelligence - Data Ingestion Pipeline")
    print("=" * 60)
    
    # Load configuration from environment
    config = load_config()
    
    # Validate environment
    errors, warnings = validate_environment(config)
    
    # Handle errors
    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f"   • {error}")
        print(f"\n💡 Current paths:")
        print(f"   CSV Directory: {config['csv_directory']}")
        print(f"   PDF Directory: {config['pdf_directory']}")
        print(f"\n💡 Please check your .env file:")
        print(f"   DATABASE_URL={config['database_url']}")
        print(f"   JINA_API_KEY=your_jina_key_here")
        return
    
    # Handle warnings
    if warnings:
        print("⚠️  Configuration Warnings:")
        for warning in warnings:
            print(f"   • {warning}")
        print()
    
    # Display configuration
    print("🔧 Configuration:")
    db_display = config['database_url'].split('@')[-1] if '@' in config['database_url'] else config['database_url']
    print(f"   Database: {db_display}")
    print(f"   CSV Directory: {config['csv_directory']}")
    print(f"   PDF Directory: {config['pdf_directory']}")
    print(f"   ChromaDB Path: {config['chromadb_path']}")
    print(f"   Chunk Size: {config['chunk_size']} chars")
    
    # Count files to process
    csv_dir = Path(config['csv_directory'])
    pdf_dir = Path(config['pdf_directory'])
    
    csv_files = list(csv_dir.glob('*.csv')) if csv_dir.exists() else []
    pdf_files = list(pdf_dir.glob('*.pdf')) if pdf_dir.exists() else []
    
    print(f"\n📊 Files to Process:")
    print(f"   📈 CSV files: {len(csv_files)} (from {csv_dir})")
    print(f"   📄 PDF files: {len(pdf_files)} (from {pdf_dir})")
    
    if len(csv_files) == 0 and len(pdf_files) == 0:
        print("\n❌ No files found to process!")
        print("💡 Expected file locations:")
        print(f"   CSV files: {csv_dir}")
        print(f"   PDF files: {pdf_dir}")
        return
    
    # Show file list
    if csv_files:
        print(f"\n📈 CSV Files Found ({len(csv_files)}):")
        for csv_file in sorted(csv_files):
            print(f"   • {csv_file.name}")
            
    if pdf_files:
        print(f"\n📄 PDF Files Found ({len(pdf_files)}):")
        for pdf_file in sorted(pdf_files):
            print(f"   • {pdf_file.name}")
    
    print(f"\n🚀 Starting ingestion pipeline...")
    
    # Run pipeline
    try:
        pipeline = AgriculturalDataPipeline(config)
        results = await pipeline.run_complete_pipeline()
        
        if results['success']:
            print("\n" + "=" * 60)
            print("🎉 DATA INGESTION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("📊 Results Summary:")
            if 'csv_processed' in results:
                print(f"   📈 CSV files processed: {results['csv_processed']}")
            if 'pdf_processed' in results:
                print(f"   📄 PDF files processed: {results['pdf_processed']}")
            if 'total_records' in results:
                print(f"   📋 Total records: {results['total_records']:,}")
            if 'vector_embeddings' in results:
                print(f"   🔍 Vector embeddings: {results['vector_embeddings']:,}")
            
            print(f"\n🌾 Your Agricultural Intelligence System is now LIVE!")
            print(f"🚀 Ready to serve millions of Indian farmers!")
            print(f"📋 Detailed logs: data_ingestion.log")
            
        else:
            print("\n❌ DATA INGESTION FAILED!")
            print("🔍 Check data_ingestion.log for error details")
            if 'error' in results:
                print(f"Error: {results['error']}")
            
    except KeyboardInterrupt:
        print("\n⏸️  Pipeline interrupted by user")
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"\n❌ Pipeline failed: {e}")
        print("🔍 Check data_ingestion.log for full traceback")

if __name__ == "__main__":
    asyncio.run(main())
