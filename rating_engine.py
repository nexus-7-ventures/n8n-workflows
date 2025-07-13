#!/usr/bin/env python3
"""
Rating Engine for Maps Search Evaluation
Implements logic from guidelines.txt for rating search results based on relevance, user intent, and data accuracy.
"""

import re
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from ocr_reader import QueryInfo, MapResult
from pathlib import Path


@dataclass
class RatingResult:
    """Result of rating evaluation"""
    rating: str
    confidence: float
    reasoning: str
    demotion_reason: Optional[str] = None
    data_issues: List[str] = None
    user_intent_match: Optional[str] = None
    

class RatingEngine:
    """Maps Search Evaluation Rating Engine"""
    
    def __init__(self, guidelines_content: str):
        self.logger = logging.getLogger(__name__)
        self.guidelines_content = guidelines_content
        
        # Parse guidelines content
        self.parse_guidelines()
        
        # Load supporting files
        self.load_supporting_files()
        
        self.logger.info("Rating engine initialized")
    
    def parse_guidelines(self):
        """Parse guidelines.txt to extract rating criteria"""
        self.logger.info("Parsing guidelines content")
        
        # Extract relevance levels
        self.relevance_levels = {
            'navigational': {'score': 5, 'description': 'Perfect match for user intent'},
            'excellent': {'score': 4, 'description': 'Highly relevant and useful'},
            'good': {'score': 3, 'description': 'Relevant with minor issues'},
            'fair': {'score': 2, 'description': 'Somewhat relevant'},
            'poor': {'score': 1, 'description': 'Barely relevant'},
            'not_relevant': {'score': 0, 'description': 'Not relevant to query'}
        }
        
        # Extract user intent patterns from guidelines
        self.user_intent_patterns = {
            'navigational': [
                r'specific\s+business\s+name',
                r'exact\s+location',
                r'known\s+establishment'
            ],
            'informational': [
                r'what\s+is',
                r'how\s+to',
                r'information\s+about'
            ],
            'transactional': [
                r'buy',
                r'purchase',
                r'order',
                r'book',
                r'reserve'
            ],
            'local': [
                r'near\s+me',
                r'nearby',
                r'closest',
                r'in\s+my\s+area'
            ]
        }
        
        # Extract demotion criteria
        self.demotion_criteria = {
            'distance': {
                'threshold_miles': 50,
                'severity': 'major'
            },
            'prominence': {
                'factors': ['rating', 'review_count', 'business_size'],
                'weight': 0.3
            },
            'data_accuracy': {
                'name_mismatch': 'critical',
                'address_issues': 'major',
                'phone_incorrect': 'minor',
                'hours_outdated': 'minor'
            },
            'closure': {
                'permanently_closed': 'critical',
                'temporarily_closed': 'major',
                'suspicious_closure': 'major'
            }
        }
        
        # Extract viewport handling rules
        self.viewport_rules = {
            'age_threshold_days': 180,
            'update_frequency': 'monthly',
            'accuracy_standards': 'high'
        }
        
        self.logger.info("Guidelines parsed successfully")
    
    def load_supporting_files(self):
        """Load supporting files for rating decisions"""
        self.memory_data = {}
        self.query_samples = []
        self.comment_examples = []
        
        # Load memory.md if exists
        memory_file = Path("memory.md")
        if memory_file.exists():
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.memory_data = self.parse_memory_content(content)
                    self.logger.info("Memory file loaded")
            except Exception as e:
                self.logger.error(f"Failed to load memory file: {e}")
        
        # Load query samples if exists
        query_file = Path("query_samples.txt")
        if query_file.exists():
            try:
                with open(query_file, 'r', encoding='utf-8') as f:
                    self.query_samples = [line.strip() for line in f if line.strip()]
                    self.logger.info(f"Loaded {len(self.query_samples)} query samples")
            except Exception as e:
                self.logger.error(f"Failed to load query samples: {e}")
        
        # Load comment examples if exists
        comment_file = Path("comments_examples.txt")
        if comment_file.exists():
            try:
                with open(comment_file, 'r', encoding='utf-8') as f:
                    self.comment_examples = [line.strip() for line in f if line.strip()]
                    self.logger.info(f"Loaded {len(self.comment_examples)} comment examples")
            except Exception as e:
                self.logger.error(f"Failed to load comment examples: {e}")
    
    def parse_memory_content(self, content: str) -> Dict[str, Any]:
        """Parse memory.md content into structured data"""
        sections = {
            'relevance_ratings': [],
            'demotion_reasons': [],
            'data_accuracy_logic': [],
            'viewport_interpretation': [],
            'edge_cases': [],
            'closure_handling': []
        }
        
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('## '):
                section_name = line[3:].lower().replace(' ', '_')
                if section_name in sections:
                    current_section = section_name
            elif current_section and line and not line.startswith('#'):
                sections[current_section].append(line)
        
        return sections
    
    def evaluate_results(self, query_info: QueryInfo, map_results: List[MapResult]) -> RatingResult:
        """Evaluate search results and return rating"""
        self.logger.info(f"Evaluating results for query: {query_info.query}")
        
        if not map_results:
            return RatingResult(
                rating='not_relevant',
                confidence=0.9,
                reasoning='No results found',
                demotion_reason='No results'
            )
        
        # Analyze user intent
        user_intent = self.analyze_user_intent(query_info)
        
        # Evaluate top result (most important)
        top_result = map_results[0]
        
        # Check for data accuracy issues
        data_issues = self.check_data_accuracy(top_result, query_info)
        
        # Check for demotion factors
        demotion_factors = self.check_demotion_factors(top_result, query_info)
        
        # Calculate base rating
        base_rating = self.calculate_base_rating(top_result, query_info, user_intent)
        
        # Apply demotions
        final_rating = self.apply_demotions(base_rating, demotion_factors, data_issues)
        
        # Generate reasoning
        reasoning = self.generate_reasoning(query_info, top_result, user_intent, demotion_factors)
        
        # Determine demotion reason
        demotion_reason = self.determine_demotion_reason(demotion_factors, data_issues)
        
        return RatingResult(
            rating=final_rating,
            confidence=self.calculate_confidence(final_rating, demotion_factors),
            reasoning=reasoning,
            demotion_reason=demotion_reason,
            data_issues=data_issues,
            user_intent_match=user_intent
        )
    
    def analyze_user_intent(self, query_info: QueryInfo) -> str:
        """Analyze user intent from query"""
        query_lower = query_info.query.lower()
        
        # Check for navigational intent
        if any(pattern in query_lower for pattern in ['specific', 'exact', 'named']):
            return 'navigational'
        
        # Check for local intent
        if any(word in query_lower for word in ['near', 'nearby', 'closest', 'around']):
            return 'local'
        
        # Check for transactional intent
        if any(word in query_lower for word in ['buy', 'purchase', 'order', 'book']):
            return 'transactional'
        
        # Check for informational intent
        if any(word in query_lower for word in ['what', 'how', 'why', 'when']):
            return 'informational'
        
        # Default to local for most map searches
        return 'local'
    
    def check_data_accuracy(self, result: MapResult, query_info: QueryInfo) -> List[str]:
        """Check for data accuracy issues"""
        issues = []
        
        # Check name accuracy
        if not result.name or result.name.lower() == 'unknown':
            issues.append('Missing or unclear business name')
        
        # Check address accuracy
        if not result.address or len(result.address) < 10:
            issues.append('Incomplete or missing address')
        
        # Check for suspicious data
        if result.rating and (result.rating < 1.0 or result.rating > 5.0):
            issues.append('Invalid rating value')
        
        # Check for outdated information indicators
        if 'permanently closed' in str(result.name).lower():
            issues.append('Business appears permanently closed')
        
        return issues
    
    def check_demotion_factors(self, result: MapResult, query_info: QueryInfo) -> List[Dict[str, Any]]:
        """Check for factors that should demote the rating"""
        factors = []
        
        # Distance-based demotion
        if result.distance:
            distance_match = re.search(r'(\d+\.?\d*)\s*mi', result.distance)
            if distance_match:
                distance_miles = float(distance_match.group(1))
                if distance_miles > self.demotion_criteria['distance']['threshold_miles']:
                    factors.append({
                        'type': 'distance',
                        'severity': 'major',
                        'value': distance_miles,
                        'description': f'Result is {distance_miles} miles away'
                    })
        
        # Prominence-based demotion
        if result.rating and result.rating < 3.0:
            factors.append({
                'type': 'low_rating',
                'severity': 'minor',
                'value': result.rating,
                'description': f'Low rating: {result.rating}'
            })
        
        # Review count demotion
        if result.reviews_count and result.reviews_count < 5:
            factors.append({
                'type': 'low_reviews',
                'severity': 'minor',
                'value': result.reviews_count,
                'description': f'Very few reviews: {result.reviews_count}'
            })
        
        return factors
    
    def calculate_base_rating(self, result: MapResult, query_info: QueryInfo, user_intent: str) -> str:
        """Calculate base rating before applying demotions"""
        
        # For navigational queries, exact matches should be excellent
        if user_intent == 'navigational':
            if self.is_exact_match(result.name, query_info.query):
                return 'excellent'
            else:
                return 'good'
        
        # For local queries, proximity and relevance matter
        if user_intent == 'local':
            if result.distance and 'mi' in result.distance:
                distance_match = re.search(r'(\d+\.?\d*)\s*mi', result.distance)
                if distance_match:
                    distance = float(distance_match.group(1))
                    if distance <= 5:
                        return 'good'
                    elif distance <= 15:
                        return 'fair'
                    else:
                        return 'poor'
        
        # Default rating based on general relevance
        if self.is_category_match(result, query_info):
            return 'good'
        else:
            return 'fair'
    
    def is_exact_match(self, result_name: str, query: str) -> bool:
        """Check if result name exactly matches query"""
        if not result_name or not query:
            return False
        
        # Normalize both strings
        result_clean = re.sub(r'[^\w\s]', '', result_name.lower())
        query_clean = re.sub(r'[^\w\s]', '', query.lower())
        
        return result_clean == query_clean
    
    def is_category_match(self, result: MapResult, query_info: QueryInfo) -> bool:
        """Check if result matches query category"""
        query_lower = query_info.query.lower()
        
        # Simple category matching
        if 'restaurant' in query_lower or 'food' in query_lower:
            return any(word in result.name.lower() for word in ['restaurant', 'cafe', 'diner', 'grill'])
        
        if 'gas' in query_lower or 'fuel' in query_lower:
            return any(word in result.name.lower() for word in ['gas', 'fuel', 'station', 'shell', 'bp'])
        
        if 'hotel' in query_lower or 'accommodation' in query_lower:
            return any(word in result.name.lower() for word in ['hotel', 'inn', 'motel', 'lodge'])
        
        return True  # Default to match for ambiguous queries
    
    def apply_demotions(self, base_rating: str, demotion_factors: List[Dict], data_issues: List[str]) -> str:
        """Apply demotions to base rating"""
        rating_scores = {
            'excellent': 4,
            'good': 3,
            'fair': 2,
            'poor': 1,
            'not_relevant': 0
        }
        
        score_to_rating = {v: k for k, v in rating_scores.items()}
        
        current_score = rating_scores.get(base_rating, 2)
        
        # Apply demotion factors
        for factor in demotion_factors:
            if factor['severity'] == 'major':
                current_score -= 2
            elif factor['severity'] == 'minor':
                current_score -= 1
        
        # Apply data issue demotions
        for issue in data_issues:
            if 'closed' in issue.lower():
                current_score -= 3  # Major demotion for closed businesses
            else:
                current_score -= 1
        
        # Ensure score is within bounds
        current_score = max(0, min(4, current_score))
        
        return score_to_rating.get(current_score, 'fair')
    
    def generate_reasoning(self, query_info: QueryInfo, result: MapResult, user_intent: str, demotion_factors: List[Dict]) -> str:
        """Generate reasoning for the rating decision"""
        reasoning_parts = []
        
        reasoning_parts.append(f"Query: '{query_info.query}' - {user_intent} intent")
        reasoning_parts.append(f"Top result: {result.name}")
        
        if result.address:
            reasoning_parts.append(f"Address: {result.address}")
        
        if result.rating:
            reasoning_parts.append(f"Rating: {result.rating}/5")
        
        if result.distance:
            reasoning_parts.append(f"Distance: {result.distance}")
        
        if demotion_factors:
            reasoning_parts.append("Demotion factors:")
            for factor in demotion_factors:
                reasoning_parts.append(f"- {factor['description']}")
        
        return " | ".join(reasoning_parts)
    
    def determine_demotion_reason(self, demotion_factors: List[Dict], data_issues: List[str]) -> Optional[str]:
        """Determine primary demotion reason"""
        if not demotion_factors and not data_issues:
            return None
        
        # Prioritize critical issues
        for issue in data_issues:
            if 'closed' in issue.lower():
                return 'Business permanently closed'
        
        # Check for major demotion factors
        for factor in demotion_factors:
            if factor['severity'] == 'major':
                return factor['description']
        
        # Return first minor issue
        if demotion_factors:
            return demotion_factors[0]['description']
        
        if data_issues:
            return data_issues[0]
        
        return None
    
    def calculate_confidence(self, rating: str, demotion_factors: List[Dict]) -> float:
        """Calculate confidence score for the rating"""
        base_confidence = 0.8
        
        # Reduce confidence for ambiguous ratings
        if rating == 'fair':
            base_confidence -= 0.2
        elif rating == 'poor':
            base_confidence -= 0.1
        
        # Reduce confidence if many demotion factors
        if len(demotion_factors) > 2:
            base_confidence -= 0.1
        
        return max(0.1, min(1.0, base_confidence))
    
    def correct_rating(self, rating_result: RatingResult, validation_feedback: Dict) -> RatingResult:
        """Correct rating based on QA feedback"""
        self.logger.info(f"Correcting rating based on feedback: {validation_feedback}")
        
        # Apply corrections based on feedback
        if 'rating_too_high' in validation_feedback.get('issues', []):
            # Demote rating by one level
            rating_order = ['excellent', 'good', 'fair', 'poor', 'not_relevant']
            current_index = rating_order.index(rating_result.rating)
            if current_index < len(rating_order) - 1:
                rating_result.rating = rating_order[current_index + 1]
        
        if 'rating_too_low' in validation_feedback.get('issues', []):
            # Promote rating by one level
            rating_order = ['not_relevant', 'poor', 'fair', 'good', 'excellent']
            current_index = rating_order.index(rating_result.rating)
            if current_index < len(rating_order) - 1:
                rating_result.rating = rating_order[current_index + 1]
        
        # Adjust confidence based on correction
        rating_result.confidence *= 0.8
        
        # Update reasoning to reflect correction
        rating_result.reasoning += f" | Corrected based on QA feedback: {validation_feedback.get('reason', 'Unknown')}"
        
        return rating_result
    
    def get_rating_statistics(self) -> Dict[str, Any]:
        """Get statistics about ratings given"""
        # This would track rating distribution over time
        return {
            'total_ratings': 0,
            'rating_distribution': {},
            'common_demotion_reasons': [],
            'average_confidence': 0.0
        }
    
    def update_guidelines(self, new_guidelines: str):
        """Update guidelines and reparse"""
        self.guidelines_content = new_guidelines
        self.parse_guidelines()
        self.logger.info("Guidelines updated and reparsed")
    
    def debug_rating_decision(self, query_info: QueryInfo, map_results: List[MapResult]) -> Dict[str, Any]:
        """Debug rating decision process"""
        debug_info = {
            'query_analysis': self.analyze_user_intent(query_info),
            'data_accuracy_issues': [],
            'demotion_factors': [],
            'base_rating_logic': {},
            'final_decision_path': []
        }
        
        if map_results:
            top_result = map_results[0]
            debug_info['data_accuracy_issues'] = self.check_data_accuracy(top_result, query_info)
            debug_info['demotion_factors'] = self.check_demotion_factors(top_result, query_info)
        
        return debug_info