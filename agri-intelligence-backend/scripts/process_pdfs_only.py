"""
Standalone PDF Processing Script - FIXED VERSION
Process ONLY agricultural PDFs with JINA embeddings
Looks for PDFs in ./data/raw/pdfs directory
"""
import asyncio
import logging
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to PYTHONPATH for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import your existing processors
from data_ingestion.pdf_processor import AgriculturalPDFProcessor
from data_ingestion.vector_embedder import JinaEmbeddingService

def fix_database_url_for_asyncpg(url: str) -> str:
    """Convert SQLAlchemy-style URL to asyncpg-compatible URL"""
    if url.startswith('postgresql+asyncpg://'):
        return url.replace('postgresql+asyncpg://', 'postgresql://')
    elif url.startswith('postgres+asyncpg://'):
        return url.replace('postgres+asyncpg://', 'postgres://')
    return url

async def main():
    """Process ONLY PDFs from ./data/raw/pdfs"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pdf_processing.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    print("📄 Agricultural Intelligence - PDF Processing Only")
    print("=" * 60)

    # Load configuration
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres@localhost:5433/agri_db')
    db_url = fix_database_url_for_asyncpg(db_url)  # Fix URL format
    
    jina_api_key = os.getenv('JINA_API_KEY')
    
    # ✅ FIXED: Correct PDF directory path
    pdf_directory = Path('./data/raw/pdfs')  # Your actual PDF location
    
    print(f"🔧 Configuration:")
    print(f"   Database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print(f"   PDF Directory: {pdf_directory}")
    print(f"   JINA API Key: {'✅ Set' if jina_api_key else '❌ Missing'}")

    # Validate setup
    if not pdf_directory.exists():
        print(f"\n❌ PDF directory does not exist: {pdf_directory}")
        print(f"💡 Expected to find your PDFs at: {pdf_directory.absolute()}")
        print("Please check your directory structure!")
        return

    if not jina_api_key:
        print("\n❌ JINA_API_KEY not set in environment")
        print("💡 Please add JINA_API_KEY=your_api_key to your .env file")
        return

    # Count PDFs
    pdf_files = list(pdf_directory.glob('*.pdf'))
    print(f"\n📊 Found {len(pdf_files)} PDF files:")
    
    if not pdf_files:
        print("❌ No PDF files found!")
        print(f"💡 Please place your PDF files in: {pdf_directory}")
        return
    
    # List found PDFs
    for pdf_file in sorted(pdf_files):
        print(f"   📄 {pdf_file.name}")

    print(f"\n🚀 Starting PDF processing...")

    try:
        # Initialize services
        jina_embedder = JinaEmbeddingService(jina_api_key)
        
        pdf_processor = AgriculturalPDFProcessor(
            db_url=db_url,
            jina_embedder=jina_embedder,
            chunk_size=1500,
            overlap=200
        )

        # Process PDFs
        results = await pdf_processor.process_all_pdfs(pdf_directory)

        # Display results
        print("\n" + "=" * 60)
        print("🎉 PDF PROCESSING COMPLETED!")
        print("=" * 60)
        print(f"📊 Results Summary:")
        print(f"   📄 Total PDF files: {results['total_files']}")
        print(f"   ✅ Successfully processed: {results['successful_files']}")
        print(f"   🧩 Total text chunks: {results['total_chunks']}")
        print(f"   🔍 Vector embeddings created: {results['total_chunks']}")
        
        if results['successful_files'] > 0:
            print(f"\n🌾 Your Agricultural PDFs are now searchable!")
            print(f"🚀 Ready for semantic search queries!")
            print(f"📋 Check pdf_processing.log for detailed logs")
        else:
            print(f"\n⚠️  No PDFs were successfully processed")
            print(f"🔍 Check pdf_processing.log for error details")

    except KeyboardInterrupt:
        print("\n⏸️  PDF processing interrupted by user")
        logger.info("PDF processing interrupted by user")
        
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        print(f"\n❌ PDF processing failed: {e}")
        print("🔍 Check pdf_processing.log for full details")

if __name__ == "__main__":
    asyncio.run(main())
