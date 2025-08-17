"""Main pipeline orchestrator for agricultural data ingestion - FIXED VERSION"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime
import sys

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from .csv_processor import AgriculturalCSVProcessor
from .pdf_processor import AgriculturalPDFProcessor  
from .vector_embedder import JinaEmbeddingService


class AgriculturalDataPipeline:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.jina_embedder = None
        if config.get('jina_api_key'):
            self.jina_embedder = JinaEmbeddingService(config['jina_api_key'])
        
        self.csv_processor = AgriculturalCSVProcessor(
            config['database_url'], 
            self.jina_embedder
        )
        self.pdf_processor = AgriculturalPDFProcessor(
            config['database_url'],
            self.jina_embedder,
            config.get('chunk_size', 1500),
            config.get('overlap', 200)
        )
        
    async def run_complete_pipeline(self) -> Dict[str, Any]:
        """Run the complete data ingestion pipeline"""
        
        start_time = datetime.utcnow()
        self.logger.info("🚀 Starting Agricultural Intelligence Data Ingestion Pipeline")
        
        results = {
            'start_time': start_time.isoformat(),
            'csv_results': {},
            'pdf_results': {},
            'total_processing_time': 0,
            'success': False,
            'errors': []
        }
        
        try:
            # Phase 1: Process CSV files
            self.logger.info("📊 Phase 1: Processing CSV files...")
            csv_results = await self.csv_processor.process_all_csvs(
                Path(self.config['csv_directory'])
            )
            
            csv_summary = {
                'total_files': len(csv_results),
                'successful_files': sum(1 for r in csv_results if r.success),
                'total_records': sum(r.records_processed for r in csv_results),
                'total_insights': sum(r.insights_generated for r in csv_results),
                'files': [
                    {
                        'name': r.file_name,
                        'success': r.success,
                        'records': r.records_processed,
                        'insights': r.insights_generated,
                        'error': r.error
                    } for r in csv_results
                ]
            }
            results['csv_results'] = csv_summary
            
            self.logger.info(f"✅ CSV processing complete: {csv_summary['successful_files']}/{csv_summary['total_files']} files")
            
            # Phase 2: Process PDF files
            self.logger.info("📚 Phase 2: Processing PDF files...")
            pdf_results = await self.pdf_processor.process_all_pdfs(
                Path(self.config['pdf_directory'])
            )
            
            results['pdf_results'] = pdf_results
            
            self.logger.info(f"✅ PDF processing complete: {pdf_results['successful_files']}/{pdf_results['total_files']} files, {pdf_results['total_chunks']} chunks")
            
            # Calculate total processing time
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            results['total_processing_time'] = processing_time
            results['end_time'] = end_time.isoformat()
            results['success'] = True
            
            self.logger.info(f"🎉 Pipeline completed successfully in {processing_time:.1f} seconds")
            
            # Generate summary report
            await self._generate_summary_report(results)
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline failed: {e}")
            results['errors'].append(str(e))
            results['success'] = False
            
        return results
    
    async def _generate_summary_report(self, results: Dict[str, Any]):
        """Generate and save summary report"""
        
        report_path = Path(self.config.get('output_directory', './data/processed')) / 'ingestion_report.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        self.logger.info(f"📋 Summary report saved to {report_path}")
        
        # Print summary to console
        print("\n" + "="*60)
        print("🌾 AGRICULTURAL INTELLIGENCE DATA INGESTION COMPLETE")
        print("="*60)
        print(f"📊 CSV Files: {results['csv_results']['successful_files']}/{results['csv_results']['total_files']} processed")
        print(f"📚 PDF Files: {results['pdf_results']['successful_files']}/{results['pdf_results']['total_files']} processed") 
        print(f"💾 Total Records: {results['csv_results']['total_records']:,}")
        print(f"🧩 Total Chunks: {results['pdf_results']['total_chunks']:,}")
        print(f"🧠 Insights Generated: {results['csv_results']['total_insights']:,}")
        print(f"⏱️  Processing Time: {results['total_processing_time']:.1f} seconds")
        print("="*60)
        print("🎯 Your agricultural intelligence database is ready for semantic search!")
        print("="*60)
        
        return {
            'success': True,
            'csv_processed': results['csv_results']['successful_files'],
            'pdf_processed': results['pdf_results']['successful_files'],
            'total_records': results['csv_results']['total_records'],
            'vector_embeddings': results['pdf_results']['total_chunks']
        }
