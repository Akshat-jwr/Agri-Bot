"""
Semantic Search Tool for Agricultural Documents
Searches through your ChromaDB PDF embeddings
"""
import chromadb
from typing import Dict, List, Optional
import logging
import os

logger = logging.getLogger(__name__)

class SemanticSearchTool:
    def __init__(self, chroma_path: str = "./agri_vectordb"):
        try:
            self.client = chromadb.Client()
            # Try to get existing collection or create it
            try:
                self.collection = self.client.get_collection("agricultural_documents")
                logger.info(f"Connected to existing ChromaDB collection with {self.collection.count()} documents")
            except:
                # Collection doesn't exist, create it with sample data
                logger.warning("Agricultural documents collection not found, creating with sample data")
                self.collection = self._create_sample_collection()
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.collection = None
    def _create_sample_collection(self):
        """Create collection with sample agricultural data"""
        try:
            # First check if collection exists and delete it
            try:
                self.client.delete_collection("agricultural_documents")
            except:
                pass  # Collection doesn't exist
                
            collection = self.client.create_collection(name="agricultural_documents")
            
            # Add sample agricultural documents
            sample_docs = [
                {
                    "id": "fert_1",
                    "document": "NPK fertilizers are essential for crop growth. Nitrogen promotes leafy growth, Phosphorus aids root development, and Potassium enhances disease resistance. For wheat crops in Punjab, apply 120kg N, 60kg P2O5, and 40kg K2O per hectare. Split nitrogen application: 50% at sowing, 25% at first irrigation, 25% at second irrigation.",
                    "metadata": {
                        "source_file": "fertilizer_guide.pdf",
                        "chunk_index": 1,
                        "crops_mentioned": "wheat",
                        "states_mentioned": "punjab",
                        "topics_covered": "fertilizer,npk,application",
                        "text_length": 340,
                        "word_count": 52
                    }
                },
                {
                    "id": "fert_2", 
                    "document": "Organic fertilizers like farmyard manure and compost improve soil structure and provide slow-release nutrients. Apply 5-10 tons of well-decomposed FYM per hectare before sowing. Vermicompost contains beneficial microorganisms and is rich in NPK. Green manuring with leguminous crops like dhaincha and sesbania adds nitrogen naturally.",
                    "metadata": {
                        "source_file": "organic_farming.pdf",
                        "chunk_index": 1,
                        "crops_mentioned": "dhaincha,sesbania",
                        "states_mentioned": "all",
                        "topics_covered": "fertilizer,organic,fym,vermicompost",
                        "text_length": 295,
                        "word_count": 45
                    }
                },
                {
                    "id": "weather_1",
                    "document": "Weather monitoring is crucial for farming decisions. Temperature, humidity, rainfall, and wind patterns affect crop growth. Use weather forecasts to plan irrigation, fertilizer application, and pest control. High humidity promotes fungal diseases. Strong winds can damage crops during flowering. Install weather stations for real-time monitoring.",
                    "metadata": {
                        "source_file": "weather_guide.pdf", 
                        "chunk_index": 1,
                        "crops_mentioned": "all",
                        "states_mentioned": "all",
                        "topics_covered": "weather,monitoring,irrigation,pest_control",
                        "text_length": 320,
                        "word_count": 48
                    }
                },
                {
                    "id": "market_1",
                    "document": "Market price analysis helps farmers decide when to sell crops. Monitor mandi prices regularly. Price trends show seasonal variations - wheat prices are typically higher in April-May. Store crops in proper conditions to wait for better prices. Use government MSP as price floor. Consider transportation costs when selling to distant markets.",
                    "metadata": {
                        "source_file": "market_analysis.pdf",
                        "chunk_index": 1, 
                        "crops_mentioned": "wheat",
                        "states_mentioned": "all",
                        "topics_covered": "market,price,msp,storage",
                        "text_length": 310,
                        "word_count": 47
                    }
                },
                {
                    "id": "yield_1",
                    "document": "Crop yield depends on seed quality, soil health, water management, and nutrient supply. High-yielding varieties produce more but need proper care. Timely sowing is critical - late sowing reduces yield. Maintain optimal plant population. Control weeds, pests, and diseases promptly. Proper harvesting at physiological maturity ensures good quality.",
                    "metadata": {
                        "source_file": "yield_optimization.pdf",
                        "chunk_index": 1,
                        "crops_mentioned": "all",
                        "states_mentioned": "all", 
                        "topics_covered": "yield,seed,soil,irrigation,pest_control",
                        "text_length": 315,
                        "word_count": 48
                    }
                }
            ]
            
            # Add documents to collection
            collection.add(
                ids=[doc["id"] for doc in sample_docs],
                documents=[doc["document"] for doc in sample_docs],
                metadatas=[doc["metadata"] for doc in sample_docs]
            )
            
            logger.info(f"Created sample collection with {len(sample_docs)} documents")
            return collection
            
        except Exception as e:
            logger.error(f"Failed to create sample collection: {e}")
            return None
        
    async def search_agricultural_documents(self, query: str, 
                                          n_results: int = 5,
                                          filters: Dict = None) -> List[Dict]:
        """Search agricultural documents using semantic similarity"""
        if not self.collection:
            return [{'error': 'Vector database not available'}]
            
        try:
            # Build metadata filter for ChromaDB 0.4.22
            where_clause = None
            if filters:
                where_clause = {}
                if filters.get('crops'):
                    where_clause['crops_mentioned'] = {"$contains": filters['crops']}
                if filters.get('states'):
                    where_clause['states_mentioned'] = {"$contains": filters['states']}
                if filters.get('topics'):
                    where_clause['topics_covered'] = {"$contains": filters['topics']}
            
            # Perform semantic search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )
            
            # Format results
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                    distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 1.0
                    
                    search_results.append({
                        'document_text': doc[:500] + "..." if len(doc) > 500 else doc,
                        'source_file': metadata.get('source_file', 'Unknown'),
                        'chunk_index': metadata.get('chunk_index', 0),
                        'crops_mentioned': metadata.get('crops_mentioned', '').split(',') if metadata.get('crops_mentioned') else [],
                        'states_mentioned': metadata.get('states_mentioned', '').split(',') if metadata.get('states_mentioned') else [],
                        'topics_covered': metadata.get('topics_covered', '').split(',') if metadata.get('topics_covered') else [],
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
        if not self.collection:
            return {'error': 'Vector database not available'}
            
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
                for metadata in sample_results['metadatas'][0]:
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
