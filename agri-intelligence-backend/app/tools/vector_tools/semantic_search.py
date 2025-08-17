"""
Semantic Search Tool for Agricultural Documents
Searches through your ChromaDB PDF embeddings
"""
import chromadb
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SemanticSearchTool:
    def __init__(self, chroma_path: str = "./agri_vectordb"):
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_collection("agricultural_documents")
        
    async def search_agricultural_documents(self, query: str, 
                                          n_results: int = 5,
                                          filters: Dict = None) -> List[Dict]:
        """Search agricultural documents using semantic similarity"""
        try:
            # Build metadata filter
            where_clause = {}
            if filters:
                if filters.get('crops'):
                    # Filter by crops mentioned in documents
                    where_clause['crops_mentioned'] = {"$contains": filters['crops']}
                if filters.get('states'):
                    where_clause['states_mentioned'] = {"$contains": filters['states']}
                if filters.get('topics'):
                    where_clause['topics_covered'] = {"$contains": filters['topics']}
            
            # Perform semantic search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            # Format results
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    distance = results['distances'][i] if results['distances'] else 1.0
                    
                    search_results.append({
                        'document_text': doc[:500] + "..." if len(doc) > 500 else doc,
                        'source_file': metadata.get('source_file', 'Unknown'),
                        'chunk_index': metadata.get('chunk_index', 0),
                        'crops_mentioned': metadata.get('crops_mentioned', '').split(','),
                        'states_mentioned': metadata.get('states_mentioned', '').split(','),
                        'topics_covered': metadata.get('topics_covered', '').split(','),
                        'relevance_score': round(1 - distance, 3),  # Convert distance to similarity
                        'text_length': metadata.get('text_length', 0),
                        'word_count': metadata.get('word_count', 0)
                    })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return [{'error': str(e)}]

    async def search_by_agricultural_topic(self, topic: str, 
                                         location: Dict = None,
                                         n_results: int = 3) -> List[Dict]:
        """Search for specific agricultural topics with location context"""
        try:
            # Build location-aware query
            location_context = ""
            filters = {}
            
            if location and location.get('state'):
                location_context = f" in {location['state']}"
                filters['states'] = location['state'].lower()
            
            enhanced_query = f"{topic}{location_context}"
            
            # Search with topic-specific filters
            topic_filters = self._build_topic_filters(topic)
            if topic_filters:
                filters.update(topic_filters)
            
            results = await self.search_agricultural_documents(
                enhanced_query, 
                n_results=n_results,
                filters=filters
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Topic search error: {e}")
            return [{'error': str(e)}]
    
    def _build_topic_filters(self, topic: str) -> Dict:
        """Build filters based on agricultural topic"""
        topic_lower = topic.lower()
        filters = {}
        
        # Topic-based filtering
        if any(word in topic_lower for word in ['fertilizer', 'nutrient', 'soil']):
            filters['topics'] = 'fertilizer'
        elif any(word in topic_lower for word in ['irrigation', 'water']):
            filters['topics'] = 'irrigation'  
        elif any(word in topic_lower for word in ['pest', 'disease', 'insect']):
            filters['topics'] = 'pest_control'
        elif any(word in topic_lower for word in ['weather', 'climate', 'rain']):
            filters['topics'] = 'climate'
        elif any(word in topic_lower for word in ['price', 'market', 'sell']):
            filters['topics'] = 'market'
        elif any(word in topic_lower for word in ['scheme', 'subsidy', 'government']):
            filters['topics'] = 'policy'
            
        return filters

    async def get_document_summary(self) -> Dict:
        """Get summary of documents in the vector database"""
        try:
            # Get collection info
            collection_count = self.collection.count()
            
            # Sample some documents to analyze content
            sample_results = self.collection.query(
                query_texts=["agriculture farming"],
                n_results=min(20, collection_count)
            )
            
            # Analyze metadata
            all_crops = set()
            all_states = set()
            all_topics = set()
            source_files = set()
            
            if sample_results['metadatas'] and sample_results['metadatas'][0]:
                for metadata in sample_results['metadatas']:
                    if metadata.get('crops_mentioned'):
                        all_crops.update(metadata['crops_mentioned'].split(','))
                    if metadata.get('states_mentioned'):
                        all_states.update(metadata['states_mentioned'].split(','))
                    if metadata.get('topics_covered'):
                        all_topics.update(metadata['topics_covered'].split(','))
                    if metadata.get('source_file'):
                        source_files.add(metadata['source_file'])
            
            return {
                'total_documents': collection_count,
                'source_files': list(source_files),
                'crops_covered': [crop.strip() for crop in all_crops if crop.strip()],
                'states_covered': [state.strip() for state in all_states if state.strip()],
                'topics_covered': [topic.strip() for topic in all_topics if topic.strip()],
                'database_status': 'active'
            }
            
        except Exception as e:
            logger.error(f"Document summary error: {e}")
            return {'error': str(e)}

# Global semantic search tool instance
search_tool = SemanticSearchTool()
