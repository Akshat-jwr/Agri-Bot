"""Jina AI embeddings service for agricultural text - FIXED VERSION"""
import asyncio
import aiohttp
import json
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass


@dataclass
class EmbeddingResult:
    text: str
    embedding: List[float]
    success: bool
    error: Optional[str] = None


class JinaEmbeddingService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.jina.ai/v1/embeddings"
        self.model = "jina-embeddings-v2-base-en"  # 1024 dimensions
        self.logger = logging.getLogger(__name__)
        
    async def embed_single_text(self, text: str) -> EmbeddingResult:
        """Embed single text using Jina API - FIXED VERSION"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # ✅ FIXED: Only send required parameters - no extra fields!
        payload = {
            "model": self.model,
            "input": [text]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url, 
                    headers=headers, 
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        embedding = result["data"][0]["embedding"]
                        
                        return EmbeddingResult(
                            text=text,
                            embedding=embedding,
                            success=True
                        )
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Jina API error {response.status}: {error_text}")
                        
                        return EmbeddingResult(
                            text=text,
                            embedding=[],
                            success=False,
                            error=f"API error {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            self.logger.error(f"Embedding error for text: {str(e)}")
            return EmbeddingResult(
                text=text,
                embedding=[],
                success=False,
                error=str(e)
            )
    
    async def embed_batch_texts(self, texts: List[str], batch_size: int = 10) -> List[EmbeddingResult]:
        """Embed multiple texts in batches - FIXED VERSION"""
        
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            self.logger.info(f"Processing embedding batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            # Process batch concurrently
            batch_tasks = [self.embed_single_text(text) for text in batch]
            batch_results = await asyncio.gather(*batch_tasks)
            
            results.extend(batch_results)
            
            # Rate limiting - small delay between batches
            if i + batch_size < len(texts):
                await asyncio.sleep(1)
        
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"Embedding completed: {successful}/{len(texts)} successful")
        
        return results
