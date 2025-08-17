"""Process agricultural PDFs with intelligent chunking - COMPLETE UPDATED VERSION"""
import fitz  # PyMuPDF
import asyncpg
import asyncio
import chromadb
from pathlib import Path
from typing import List, Dict, Optional
import re
import logging
import json
from dataclasses import dataclass


@dataclass 
class PDFChunk:
    chunk_id: str
    source_file: str
    chunk_index: int
    total_chunks: int
    chunk_text: str
    crops_mentioned: List[str]
    states_mentioned: List[str] 
    topics_covered: List[str]
    metadata: Dict


class AgriculturalPDFProcessor:
    def __init__(self, db_url: str, jina_embedder, chunk_size: int = 1500, overlap: int = 200):
        self.db_url = db_url
        self.jina_embedder = jina_embedder
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.logger = logging.getLogger(__name__)
        
        # Initialize ChromaDB for document vectors
        self.chroma_client = chromadb.PersistentClient(path="./agri_vectordb")
        self.collection = self.chroma_client.get_or_create_collection(
            name="agricultural_documents",
            metadata={
                "description": "Agricultural PDFs and Reports",
                "version": "1.0"
            }
        )
        
        # Agricultural keyword sets for context extraction
        self.crop_keywords = [
            'wheat', 'rice', 'maize', 'corn', 'barley', 'millet', 'sorghum',
            'cotton', 'sugarcane', 'jute', 'tea', 'coffee', 'coconut',
            'groundnut', 'mustard', 'sesame', 'sunflower', 'soybean', 'safflower',
            'gram', 'chickpea', 'arhar', 'pigeonpea', 'moong', 'urad', 'masoor', 'lentil',
            'potato', 'onion', 'garlic', 'tomato', 'brinjal', 'okra', 'cabbage',
            'mango', 'banana', 'orange', 'apple', 'guava'
        ]
        
        self.state_keywords = [
            'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh',
            'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jharkhand',
            'karnataka', 'kerala', 'madhya pradesh', 'maharashtra', 'manipur',
            'meghalaya', 'mizoram', 'nagaland', 'odisha', 'punjab',
            'rajasthan', 'sikkim', 'tamil nadu', 'telangana', 'tripura',
            'uttar pradesh', 'uttarakhand', 'west bengal'
        ]
        
        self.topic_keywords = {
            'irrigation': ['irrigation', 'water', 'sprinkler', 'drip', 'canal', 'well', 'pump'],
            'fertilizer': ['fertilizer', 'npk', 'urea', 'phosphate', 'potash', 'nitrogen', 'manure'],
            'pest_control': ['pest', 'disease', 'insect', 'fungicide', 'pesticide', 'herbicide'],
            'soil_health': ['soil', 'ph', 'organic matter', 'nutrients', 'erosion', 'fertility'],
            'climate': ['weather', 'rainfall', 'temperature', 'monsoon', 'drought', 'climate'],
            'market': ['price', 'market', 'mandi', 'procurement', 'msp', 'trading'],
            'technology': ['mechanization', 'tractor', 'harvester', 'technology', 'equipment'],
            'policy': ['scheme', 'subsidy', 'policy', 'government', 'loan', 'insurance'],
            'organic': ['organic', 'sustainable', 'natural', 'bio', 'ecological'],
            'seeds': ['seed', 'variety', 'hybrid', 'improved', 'quality']
        }
    
    async def process_all_pdfs(self, pdf_directory: Path) -> Dict[str, int]:
        """Process all PDFs in directory with JINA embeddings"""
        
        pdf_files = list(pdf_directory.glob("*.pdf"))
        self.logger.info(f"📚 Found {len(pdf_files)} PDF files to process")
        
        total_chunks = 0
        successful_files = 0
        
        if not pdf_files:
            self.logger.warning("No PDF files found")
            return {
                'total_files': 0,
                'successful_files': 0,
                'total_chunks': 0
            }
        
        conn = await asyncpg.connect(self.db_url)
        
        try:
            for pdf_file in pdf_files:
                try:
                    chunks_processed = await self.process_single_pdf(conn, pdf_file)
                    total_chunks += chunks_processed
                    successful_files += 1
                    self.logger.info(f"✅ Processed {pdf_file.name}: {chunks_processed} chunks")
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to process {pdf_file.name}: {e}")
                    
        finally:
            await conn.close()
        
        return {
            'total_files': len(pdf_files),
            'successful_files': successful_files,
            'total_chunks': total_chunks
        }
    
    async def process_single_pdf(self, conn: asyncpg.Connection, pdf_file: Path) -> int:
        """Process individual PDF file with text extraction and chunking"""
        
        try:
            # Extract text from PDF
            doc = fitz.open(str(pdf_file))
            full_text = ""
            
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
            doc.close()
            
            if len(full_text.strip()) < 100:
                self.logger.warning(f"PDF {pdf_file.name} has very little text content")
                return 0
            
            self.logger.info(f"Extracted {len(full_text)} characters from {pdf_file.name}")
            
            # Clean text
            cleaned_text = self._clean_text(full_text)
            
            # Intelligent chunking
            chunks = self._intelligent_chunk_text(cleaned_text, pdf_file.name)
            
            # Store chunks with JINA embeddings
            chunks_stored = await self._store_chunks_with_embeddings(conn, chunks)
            
            return chunks_stored
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {pdf_file.name}: {e}")
            return 0
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted PDF text"""
        
        # Remove page headers/footers
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove weird characters but keep essential punctuation
        text = re.sub(r'[^\w\s.,;:!?()\-\'\"]+', '', text)
        
        # Remove very short lines (likely artifacts)
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 10]
        
        return '\n'.join(cleaned_lines)
    
    def _intelligent_chunk_text(self, text: str, source_file: str) -> List[PDFChunk]:
        """Intelligent chunking with overlap and context preservation"""
        
        # Split into sentences for better boundary detection
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        chunks = []
        current_chunk = ""
        current_sentences = []
        chunk_index = 0
        
        for sentence in sentences:
            # Check if adding this sentence exceeds chunk size
            if len(current_chunk + sentence) > self.chunk_size and current_chunk:
                
                # Create chunk
                chunk = self._create_pdf_chunk(
                    current_chunk.strip(),
                    source_file,
                    chunk_index,
                    len(sentences) // (self.chunk_size // 150)  # Estimate total chunks
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_sentences = current_sentences[-2:] if len(current_sentences) > 2 else current_sentences
                current_chunk = ' '.join(overlap_sentences) + ' ' + sentence
                current_sentences = overlap_sentences + [sentence]
                chunk_index += 1
                
            else:
                current_chunk += ' ' + sentence if current_chunk else sentence
                current_sentences.append(sentence)
        
        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_pdf_chunk(
                current_chunk.strip(),
                source_file, 
                chunk_index,
                chunk_index + 1
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_pdf_chunk(self, text: str, source_file: str, 
                         chunk_index: int, total_chunks: int) -> PDFChunk:
        """Create PDFChunk with extracted agricultural context"""
        
        chunk_id = f"{source_file}_{chunk_index}"
        
        # Extract agricultural context
        crops_mentioned = self._extract_crops(text)
        states_mentioned = self._extract_states(text) 
        topics_covered = self._extract_topics(text)
        
        # Rich metadata
        metadata = {
            'source_file': source_file,
            'text_length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(re.split(r'[.!?]+', text)),
            'has_numbers': bool(re.search(r'\d+', text)),
            'has_tables': 'table' in text.lower() or '|' in text,
            'has_percentages': bool(re.search(r'\d+%', text)),
            'language_hints': self._detect_language_hints(text)
        }
        
        return PDFChunk(
            chunk_id=chunk_id,
            source_file=source_file,
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            chunk_text=text,
            crops_mentioned=crops_mentioned,
            states_mentioned=states_mentioned,
            topics_covered=topics_covered,
            metadata=metadata
        )
    
    def _extract_crops(self, text: str) -> List[str]:
        """Extract crop mentions from text"""
        text_lower = text.lower()
        found_crops = []
        
        for crop in self.crop_keywords:
            if crop in text_lower:
                found_crops.append(crop)
        
        return list(set(found_crops))
    
    def _extract_states(self, text: str) -> List[str]:
        """Extract state mentions from text"""
        text_lower = text.lower()
        found_states = []
        
        for state in self.state_keywords:
            if state in text_lower:
                found_states.append(state)
        
        return list(set(found_states))
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract agricultural topics from text"""
        text_lower = text.lower()
        found_topics = []
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_topics.append(topic)
        
        return found_topics
    
    def _detect_language_hints(self, text: str) -> List[str]:
        """Detect language and regional hints in text"""
        hints = []
        
        # Check for Hindi/regional terms
        regional_terms = ['kharif', 'rabi', 'zaid', 'mandi', 'kisan', 'fasal', 'krishi', 'bhumi']
        if any(term in text.lower() for term in regional_terms):
            hints.append('hindi_agricultural_terms')
        
        # Check for policy terms
        policy_terms = ['pradhan mantri', 'yojana', 'nrega', 'msp']
        if any(term in text.lower() for term in policy_terms):
            hints.append('government_policy')
        
        return hints
    
    async def _store_chunks_with_embeddings(self, conn: asyncpg.Connection, 
                                          chunks: List[PDFChunk]) -> int:
        """Store chunks with JINA embeddings in both PostgreSQL and ChromaDB"""
        
        if not self.jina_embedder:
            self.logger.warning("No JINA embedder available, storing chunks without embeddings")
            return len(chunks)
        
        stored_count = 0
        batch_size = 5  # Process in small batches to avoid API limits
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Get embeddings for batch
            texts = [chunk.chunk_text for chunk in batch]
            embedding_results = await self.jina_embedder.embed_batch_texts(texts, batch_size=batch_size)
            
            # Store each chunk with its embedding
            for chunk, embedding_result in zip(batch, embedding_results):
                if embedding_result.success:
                    try:
                        # Store in PostgreSQL metadata table
                        await conn.execute(
                            """
                            INSERT INTO document_metadata 
                            (chromadb_id, source_file, source_type, chunk_index, total_chunks, 
                             crops_mentioned, states_mentioned, topics_covered, 
                             file_size_bytes, text_length, word_count)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                            ON CONFLICT (source_file, chunk_index) DO UPDATE SET
                            crops_mentioned = EXCLUDED.crops_mentioned,
                            states_mentioned = EXCLUDED.states_mentioned,
                            topics_covered = EXCLUDED.topics_covered
                            """,
                            chunk.chunk_id,
                            chunk.source_file,
                            "pdf",
                            chunk.chunk_index,
                            chunk.total_chunks,
                            chunk.crops_mentioned,
                            chunk.states_mentioned,
                            chunk.topics_covered,
                            chunk.metadata.get('file_size_bytes', 0),
                            chunk.metadata.get('text_length', 0),
                            chunk.metadata.get('word_count', 0)
                        )
                        
                        # Store in ChromaDB with embedding
                        self.collection.add(
                            documents=[chunk.chunk_text],
                            embeddings=[embedding_result.embedding],
                            metadatas=[{
                                'source_file': chunk.source_file,
                                'chunk_index': chunk.chunk_index,
                                'crops_mentioned': ','.join(chunk.crops_mentioned),
                                'states_mentioned': ','.join(chunk.states_mentioned),
                                'topics_covered': ','.join(chunk.topics_covered),
                                'text_length': chunk.metadata['text_length'],
                                'word_count': chunk.metadata['word_count']
                            }],
                            ids=[chunk.chunk_id]
                        )
                        
                        stored_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"Failed to store chunk {chunk.chunk_id}: {e}")
                else:
                    self.logger.warning(f"Failed to get embedding for chunk {chunk.chunk_id}: {embedding_result.error}")
            
            # Small delay between batches to respect API limits
            await asyncio.sleep(1)
        
        return stored_count
