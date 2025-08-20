"""
Agricultural Query Classifier with NLP

Maps farmer queries to 11 agricultural categories and extracts context

File: app/tools/rag_core/query_classifier.py
"""

import re
import asyncio
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class QueryClassification:
    """Structured query classification result"""
    primary_category: str
    secondary_categories: List[str]
    confidence: float
    extracted_entities: Dict[str, any]
    intent: str
    urgency: str
    location_context: Optional[Dict[str, str]] = None

class AgriculturalQueryClassifier:
    """
    NLP-based query classifier for agricultural intelligence
    Routes farmer questions to appropriate tools and extracts context
    """
    
    def __init__(self):
        self.category_keywords = {
            'weather_impact': {
                'keywords': ['weather', 'rain', 'temperature', 'climate', 'monsoon', 'drought', 'flood', 'storm', 'humidity', 'wind'],
                'priority': 0.9,
                'tools': ['real_weather_apis', 'semantic_search']
            },
            'irrigation_planning': {
                'keywords': ['irrigation', 'water', 'drip', 'sprinkler', 'watering', 'moisture', 'drought', 'canal', 'tubewell'],
                'priority': 0.8,
                'tools': ['real_weather_apis', 'sql_queries', 'real_yield_prediction']
            },
            'market_price_forecasting': {
                'keywords': ['price', 'sell', 'market', 'mandi', 'profit', 'cost', 'trading', 'commodity', 'futures'],
                'priority': 0.9,
                'tools': ['real_market_apis', 'price_prediction', 'semantic_search']
            },
            'crop_selection': {
                'keywords': ['crop', 'variety', 'seed', 'planting', 'sowing', 'cultivation', 'farming', 'recommend'],
                'priority': 0.8,
                'tools': ['real_yield_prediction', 'sql_queries', 'semantic_search']
            },
            'yield_prediction': {
                'keywords': ['yield', 'production', 'harvest', 'output', 'productivity', 'forecast', 'predict'],
                'priority': 0.9,
                'tools': ['real_yield_prediction', 'real_weather_apis', 'sql_queries']
            },
            'pest_disease_management': {
                'keywords': ['pest', 'disease', 'insect', 'fungus', 'infection', 'spray', 'pesticide', 'treatment'],
                'priority': 0.8,
                'tools': ['semantic_search', 'real_weather_apis', 'google_search']
            },
            'fertilizer_optimization': {
                'keywords': ['fertilizer', 'fertiliser', 'nutrient', 'nitrogen', 'phosphate', 'potash', 'urea', 'soil', 'manure', 'npk', 'organic', 'compost', 'apply', 'application', 'dose', 'quantity', 'how much', 'when to apply'],
                'priority': 0.9,
                'tools': ['sql_queries', 'semantic_search', 'real_yield_prediction']
            },
            'government_schemes': {
                'keywords': ['scheme', 'subsidy', 'government', 'pmkisan', 'insurance', 'loan', 'benefit', 'policy'],
                'priority': 0.9,
                'tools': ['government_apis', 'semantic_search', 'google_search']
            },
            'financial_planning': {
                'keywords': ['loan', 'credit', 'insurance', 'investment', 'finance', 'bank', 'money', 'cost'],
                'priority': 0.7,
                'tools': ['government_apis', 'real_market_apis', 'semantic_search']
            },
            'seasonal_planning': {
                'keywords': ['season', 'calendar', 'timing', 'schedule', 'kharif', 'rabi', 'summer', 'winter'],
                'priority': 0.8,
                'tools': ['real_weather_apis', 'semantic_search', 'sql_queries']
            },
            'soil_health': {
                'keywords': ['soil', 'health', 'ph', 'organic', 'fertility', 'erosion', 'nutrients', 'testing'],
                'priority': 0.7,
                'tools': ['semantic_search', 'sql_queries', 'google_search']
            }
        }
        
        # Common agricultural entities
        self.crop_patterns = [
            r'\b(wheat|rice|cotton|maize|sugarcane|soybean|groundnut|jowar|bajra|ragi)\b',
            r'\b(paddy|gahun|kapas|makka|gehun)\b'  # Hindi terms
        ]
        
        self.location_patterns = [
            r'\b(punjab|haryana|uttar pradesh|maharashtra|karnataka|gujarat|rajasthan|madhya pradesh|bihar|west bengal)\b',
            r'\b([A-Z][a-z]+pur|[A-Z][a-z]+bad|[A-Z][a-z]+nagar)\b'  # City patterns
        ]
        
        self.urgency_indicators = {
            'high': ['urgent', 'emergency', 'immediately', 'asap', 'crisis', 'disaster', 'dying', 'failing'],
            'medium': ['soon', 'quickly', 'this week', 'planning', 'prepare'],
            'low': ['future', 'next season', 'thinking', 'considering', 'general']
        }

    async def classify_query(self, query: str, farmer_context: Optional[Dict] = None) -> QueryClassification:
        """
        Classify farmer query into agricultural categories with confidence scoring
        """
        try:
            query_lower = query.lower()
            
            # Extract entities
            entities = self._extract_entities(query_lower)
            
            # Calculate category scores
            category_scores = {}
            for category, config in self.category_keywords.items():
                score = self._calculate_category_score(query_lower, config['keywords'])
                if score > 0:
                    category_scores[category] = score * config['priority']
            
            # Determine primary and secondary categories with scaling to avoid ultra-low confidences
            if not category_scores:
                primary_category = 'general_farming'
                secondary_categories = []
                confidence = 0.5
            else:
                max_raw = max(category_scores.values())
                scale = 1.0
                if 0 < max_raw < 0.6:
                    scale = 0.6 / max_raw
                scaled = {k: min(v * scale, 1.0) for k, v in category_scores.items()}
                sorted_categories = sorted(scaled.items(), key=lambda x: x[1], reverse=True)
                primary_category = sorted_categories[0][0]
                confidence = sorted_categories[0][1]
                secondary_categories = [cat for cat, score in sorted_categories[1:3] if score >= 0.35]
            
            # Determine intent and urgency
            intent = self._determine_intent(query_lower)
            urgency = self._determine_urgency(query_lower)
            
            # Add farmer context if available
            location_context = self._extract_location_context(query_lower, farmer_context)
            
            return QueryClassification(
                primary_category=primary_category,
                secondary_categories=secondary_categories,
                confidence=min(confidence, 1.0),
                extracted_entities=entities,
                intent=intent,
                urgency=urgency,
                location_context=location_context
            )
            
        except Exception as e:
            logger.error(f"Query classification error: {e}")
            return QueryClassification(
                primary_category='general_farming',
                secondary_categories=[],
                confidence=0.3,
                extracted_entities={},
                intent='information',
                urgency='low'
            )

    def _calculate_category_score(self, query: str, keywords: List[str]) -> float:
        """Improved relevance score (no harsh length normalization)."""
        score = 0.0
        for keyword in keywords:
            occ = query.count(keyword)
            if occ:
                score += 0.35 + (occ - 1) * 0.05
        return min(score, 3.0)

    def _extract_entities(self, query: str) -> Dict[str, any]:
        """Extract agricultural entities from query"""
        entities = {
            'crops': [],
            'locations': [],
            'numbers': [],
            'dates': []
        }
        
        # Extract crops
        for pattern in self.crop_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities['crops'].extend(matches)
        
        # Extract locations
        for pattern in self.location_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities['locations'].extend(matches)
        
        # Extract numbers (area, quantity, etc.)
        number_matches = re.findall(r'\d+(?:\.\d+)?', query)
        entities['numbers'] = [float(n) for n in number_matches]
        
        # Extract time references
        time_patterns = [
            r'\b(today|tomorrow|next week|this month|next season)\b',
            r'\b(\d{1,2}/\d{1,2}|\d{1,2}-\d{1,2})\b'
        ]
        for pattern in time_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities['dates'].extend(matches)
        
        return entities

    def _determine_intent(self, query: str) -> str:
        """Determine user intent from query"""
        intent_patterns = {
            'question': ['what', 'when', 'where', 'why', 'how', 'which', '?'],
            'request': ['please', 'can you', 'could you', 'help me', 'i need'],
            'information': ['tell me', 'explain', 'show me', 'information about'],
            'prediction': ['predict', 'forecast', 'will', 'expect', 'future'],
            'recommendation': ['recommend', 'suggest', 'advise', 'best', 'should'],
            'comparison': ['compare', 'difference', 'better', 'vs', 'versus']
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in query for pattern in patterns):
                return intent
        
        return 'information'  # Default

    def _determine_urgency(self, query: str) -> str:
        """Determine urgency level from query"""
        for urgency_level, indicators in self.urgency_indicators.items():
            if any(indicator in query for indicator in indicators):
                return urgency_level
        return 'medium'  # Default

    def _extract_location_context(self, query: str, farmer_context: Optional[Dict]) -> Optional[Dict]:
        """Extract or use location context"""
        location_context = {}
        
        # Extract from query
        for pattern in self.location_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                location_context['state'] = matches[0].title()
        
        # Use farmer context if available
        if farmer_context:
            if 'state' in farmer_context:
                location_context['state'] = farmer_context['state']
            if 'district' in farmer_context:
                location_context['district'] = farmer_context['district']
        
        return location_context if location_context else None

# Global classifier instance
query_classifier = AgriculturalQueryClassifier()
