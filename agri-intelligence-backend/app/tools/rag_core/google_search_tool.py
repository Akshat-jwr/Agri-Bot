"""
Google Search API Integration for Real-Time Information

Provides live web search grounding for agricultural queries

File: app/tools/rag_core/google_search_tool.py
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
import os
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class GoogleSearchTool:
    """
    Google Custom Search API integration for agricultural intelligence
    Provides real-time web information grounding
    """
    
    def __init__(self):
        self.api_key = settings.google_search_api_key
        self.search_engine_id = settings.google_search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        # Agricultural search domains for better results
        self.trusted_domains = [
            'icar.org.in',
            'farmer.gov.in',
            'agmarknet.gov.in',
            'pmkisan.gov.in',
            'agricoop.gov.in',
            'krishi.icar.gov.in',
            'extension.org',
            'fao.org'
        ]
        
        if not self.api_key:
            logger.warning("google_search_api_key not set in .env. Search functionality will be limited.")

    async def search_agricultural_info(self, 
                                     query: str, 
                                     location: Optional[str] = None,
                                     num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search for agricultural information with location context
        """
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Search API not configured. Using fallback search.")
            return self._fallback_search(query)
        
        try:
            # Enhance query with agricultural context
            enhanced_query = self._enhance_agricultural_query(query, location)
            
            async with aiohttp.ClientSession() as session:
                params = {
                    'key': self.api_key,
                    'cx': self.search_engine_id,
                    'q': enhanced_query,
                    'num': num_results,
                    'dateRestrict': 'y1',  # Results from last year
                    'lr': 'lang_en',
                    'safe': 'active'
                }
                
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_search_results(data)
                    else:
                        logger.error(f"Google Search API error: {response.status}")
                        return self._fallback_search(query)
                        
        except Exception as e:
            logger.error(f"Google Search error: {e}")
            return self._fallback_search(query)

    async def search_government_schemes(self, scheme_type: str, state: str = None) -> List[Dict[str, str]]:
        """
        Search for government agricultural schemes
        """
        query = f"agricultural {scheme_type} scheme India government"
        if state:
            query += f" {state}"
        
        return await self.search_agricultural_info(query, state)

    async def search_crop_diseases(self, crop: str, symptoms: str) -> List[Dict[str, str]]:
        """
        Search for crop disease information
        """
        query = f"{crop} crop disease {symptoms} treatment management"
        return await self.search_agricultural_info(query)

    async def search_market_news(self, commodity: str, state: str = None) -> List[Dict[str, str]]:
        """
        Search for market news and price updates
        """
        query = f"{commodity} market price news agriculture India"
        if state:
            query += f" {state}"
        
        return await self.search_agricultural_info(query, state)

    def _enhance_agricultural_query(self, query: str, location: Optional[str]) -> str:
        """
        Enhance search query with agricultural and location context
        """
        enhanced_query = f"agriculture farming {query}"
        
        # Add location context
        if location:
            enhanced_query += f" {location} India"
        else:
            enhanced_query += " India"
        
        # Add site restrictions for trusted sources
        if len(self.trusted_domains) > 0:
            site_restriction = " OR ".join([f"site:{domain}" for domain in self.trusted_domains[:3]])
            enhanced_query += f" ({site_restriction})"
        
        return enhanced_query

    def _process_search_results(self, search_data: Dict) -> List[Dict[str, str]]:
        """
        Process Google Search API response
        """
        results = []
        
        for item in search_data.get('items', []):
            result = {
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'source': self._extract_domain(item.get('link', '')),
                'relevance_score': self._calculate_relevance(item),
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)
        
        return results

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return 'unknown'

    def _calculate_relevance(self, item: Dict) -> float:
        """Calculate relevance score for search result"""
        score = 0.5  # Base score
        
        # Boost trusted agricultural domains
        domain = self._extract_domain(item.get('link', ''))
        if any(trusted in domain for trusted in self.trusted_domains):
            score += 0.3
        
        # Boost recent content
        title = item.get('title', '').lower()
        snippet = item.get('snippet', '').lower()
        
        # Agricultural relevance keywords
        agri_keywords = ['farming', 'crop', 'agriculture', 'farmer', 'cultivation', 'harvest']
        keyword_count = sum(1 for keyword in agri_keywords if keyword in title or keyword in snippet)
        score += keyword_count * 0.05
        
        return min(score, 1.0)

    def _fallback_search(self, query: str) -> List[Dict[str, str]]:
        """
        Fallback search results when API is not available
        """
        return [
            {
                'title': f'Agricultural Information: {query}',
                'url': 'https://farmer.gov.in',
                'snippet': f'Search results for agricultural query: {query}. Please consult local agricultural experts for specific advice.',
                'source': 'farmer.gov.in',
                'relevance_score': 0.7,
                'timestamp': datetime.now().isoformat(),
                'note': 'Fallback result - configure Google Search API for live results'
            }
        ]

# Global search tool instance
google_search_tool = GoogleSearchTool()
