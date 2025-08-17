"""
Enhanced database manager for agricultural intelligence data ingestion
Supports PostgreSQL with pgvector extension for semantic search
"""
import asyncpg
import asyncio
import logging
from typing import Any, Optional, Dict, List
from contextlib import asynccontextmanager
import json
from datetime import datetime

class AgriculturalDatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
        self.logger = logging.getLogger(__name__)
        
    async def initialize_pool(self, min_connections: int = 5, max_connections: int = 20):
        """Initialize connection pool for better performance"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=min_connections,
                max_size=max_connections,
                command_timeout=60
            )
            self.logger.info(f"Database pool initialized with {min_connections}-{max_connections} connections")
    
    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            self.logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager for database connections"""
        if not self.pool:
            await self.initialize_pool()
        
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute_with_retry(self, query: str, *args, max_retries: int = 3):
        """Execute query with retry logic"""
        for attempt in range(max_retries):
            try:
                async with self.get_connection() as conn:
                    return await conn.execute(query, *args)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                self.logger.warning(f"Query attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)
    
    async def fetch_with_retry(self, query: str, *args, max_retries: int = 3):
        """Fetch query with retry logic"""
        for attempt in range(max_retries):
            try:
                async with self.get_connection() as conn:
                    return await conn.fetch(query, *args)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                self.logger.warning(f"Fetch attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)
    
    # Agricultural-specific database operations
    
    async def insert_csv_batch(self, table_name: str, records: List[Dict], 
                              conflict_action: str = "DO NOTHING"):
        """Batch insert CSV records with conflict handling"""
        if not records:
            return 0
        
        # Get first record to determine columns
        sample_record = records[0]
        columns = list(sample_record.keys())
        
        # Build query
        placeholders = [f"${i+1}" for i in range(len(columns))]
        query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            ON CONFLICT {conflict_action}
        """
        
        inserted_count = 0
        batch_size = 1000  # Process in batches
        
        async with self.get_connection() as conn:
            async with conn.transaction():
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    
                    for record in batch:
                        try:
                            values = [record.get(col) for col in columns]
                            await conn.execute(query, *values)
                            inserted_count += 1
                        except Exception as e:
                            self.logger.warning(f"Failed to insert record: {e}")
                            continue
        
        return inserted_count
    
    async def insert_document_chunk(self, source_file: str, chunk_index: int,
                                  total_chunks: int, chunk_text: str,
                                  embedding: List[float], metadata: Dict,
                                  crops: List[str] = None, states: List[str] = None,
                                  topics: List[str] = None):
        """Insert document chunk with vector embedding"""
        
        query = """
            INSERT INTO document_chunks 
            (source_file, source_type, chunk_index, total_chunks, chunk_text,
             metadata, crops_mentioned, states_mentioned, topics_covered, embedding)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (source_file, chunk_index) DO UPDATE SET
            embedding = EXCLUDED.embedding,
            metadata = EXCLUDED.metadata,
            crops_mentioned = EXCLUDED.crops_mentioned,
            states_mentioned = EXCLUDED.states_mentioned,
            topics_covered = EXCLUDED.topics_covered
            RETURNING id
        """
        
        async with self.get_connection() as conn:
            return await conn.fetchval(
                query,
                source_file,
                'pdf',  # source_type
                chunk_index,
                total_chunks,
                chunk_text,
                json.dumps(metadata),
                crops or [],
                states or [],
                topics or [],
                embedding
            )
    
    async def insert_agricultural_insight(self, insight_text: str, data_source: str,
                                        state_name: str, crop_type: str,
                                        topic_category: str, embedding: List[float],
                                        numerical_data: Dict = None,
                                        year_range: List[int] = None):
        """Insert agricultural insight with context"""
        
        query = """
            INSERT INTO agricultural_insights
            (insight_text, data_source, state_name, crop_type, topic_category,
             numerical_data, year_range, embedding)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT DO NOTHING
            RETURNING id
        """
        
        async with self.get_connection() as conn:
            return await conn.fetchval(
                query,
                insight_text,
                data_source,
                state_name,
                crop_type,
                topic_category,
                json.dumps(numerical_data or {}),
                year_range or [],
                embedding
            )
    
    async def semantic_search_chunks(self, query_embedding: List[float], 
                                   limit: int = 10, similarity_threshold: float = 0.7,
                                   state_filter: str = None, crop_filter: str = None):
        """Perform semantic search on document chunks"""
        
        base_query = """
            SELECT 
                chunk_text,
                source_file,
                chunk_index,
                crops_mentioned,
                states_mentioned,
                topics_covered,
                1 - (embedding <=> $1::vector) as similarity_score
            FROM document_chunks
            WHERE 1 - (embedding <=> $1::vector) > $2
        """
        
        params = [query_embedding, similarity_threshold]
        param_count = 2
        
        # Add filters
        if state_filter:
            param_count += 1
            base_query += f" AND $${param_count} = ANY(states_mentioned)"
            params.append(state_filter.lower())
        
        if crop_filter:
            param_count += 1
            base_query += f" AND $${param_count} = ANY(crops_mentioned)"
            params.append(crop_filter.lower())
        
        base_query += f"""
            ORDER BY embedding <=> $1::vector
            LIMIT ${param_count + 1}
        """
        params.append(limit)
        
        async with self.get_connection() as conn:
            return await conn.fetch(base_query, *params)
    
    async def semantic_search_insights(self, query_embedding: List[float],
                                     limit: int = 5, state_filter: str = None,
                                     topic_filter: str = None):
        """Perform semantic search on agricultural insights"""
        
        base_query = """
            SELECT 
                insight_text,
                data_source,
                state_name,
                crop_type,
                topic_category,
                numerical_data,
                1 - (embedding <=> $1::vector) as similarity_score
            FROM agricultural_insights
            WHERE 1 = 1
        """
        
        params = [query_embedding]
        param_count = 1
        
        # Add filters
        if state_filter:
            param_count += 1
            base_query += f" AND state_name ILIKE $${param_count}"
            params.append(f"%{state_filter}%")
        
        if topic_filter:
            param_count += 1
            base_query += f" AND topic_category = $${param_count}"
            params.append(topic_filter)
        
        base_query += f"""
            ORDER BY embedding <=> $1::vector
            LIMIT ${param_count + 1}
        """
        params.append(limit)
        
        async with self.get_connection() as conn:
            return await conn.fetch(base_query, *params)
    
    async def get_database_stats(self) -> Dict:
        """Get database statistics for monitoring"""
        
        stats_queries = {
            'document_chunks': "SELECT COUNT(*) FROM document_chunks",
            'agricultural_insights': "SELECT COUNT(*) FROM agricultural_insights",
            'crop_yield_data': "SELECT COUNT(*) FROM crop_yield_data",
            'weather_data': "SELECT COUNT(*) FROM weather_data",
            'market_prices': "SELECT COUNT(*) FROM market_prices",
        }
        
        stats = {}
        
        async with self.get_connection() as conn:
            for table, query in stats_queries.items():
                try:
                    count = await conn.fetchval(query)
                    stats[table] = count
                except Exception:
                    stats[table] = 0
        
        return stats
    
    async def cleanup_old_data(self, days_old: int = 30):
        """Cleanup old temporary data"""
        
        cleanup_query = """
            DELETE FROM document_chunks 
            WHERE source_type = 'temp' 
            AND created_at < NOW() - INTERVAL '{} days'
        """.format(days_old)
        
        async with self.get_connection() as conn:
            deleted_count = await conn.execute(cleanup_query)
            self.logger.info(f"Cleaned up {deleted_count} old temporary chunks")
            return deleted_count
