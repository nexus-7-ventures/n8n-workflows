#!/usr/bin/env python3
"""
Comment Generator for Maps Search Evaluation
Generates natural, valid comments based on rating results and examples.
"""

import random
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from rating_engine import RatingResult


class CommentGenerator:
    """Natural comment generator for Maps Search Evaluation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Load comment examples
        self.comment_examples = self.load_comment_examples()
        
        # Template comments for different situations
        self.comment_templates = {
            'excellent': [
                "Perfect match for user intent, highly relevant.",
                "Excellent result that directly addresses the query.",
                "Top-quality match with accurate information.",
                "Exceptional relevance and data accuracy.",
                "Outstanding result that fully satisfies user needs."
            ],
            'good': [
                "Good result with minor issues that don't affect relevance.",
                "Solid match with mostly accurate information.",
                "Relevant result with good data quality.",
                "Strong match for the user's search intent.",
                "Good result with acceptable proximity and data."
            ],
            'fair': [
                "Somewhat relevant but has notable limitations.",
                "Adequate result with some concerns about accuracy.",
                "Moderate relevance with distance or data issues.",
                "Acceptable match but not ideal for user intent.",
                "Fair result with room for improvement."
            ],
            'poor': [
                "Limited relevance with significant issues.",
                "Poor match due to distance or data problems.",
                "Barely relevant with multiple concerns.",
                "Weak result that doesn't serve user well.",
                "Poor quality result with accuracy issues."
            ],
            'not_relevant': [
                "Not relevant to the search query.",
                "Fails to match user intent or location needs.",
                "Irrelevant result that doesn't help users.",
                "No connection to the search query.",
                "Not useful for the user's search intent."
            ]
        }
        
        # Specific comment patterns for common issues
        self.issue_comments = {
            'distance': [
                "Result is too far from user location.",
                "Distance makes this result less useful.",
                "Location is not conveniently accessible.",
                "Too far to be practically relevant.",
                "Geographic distance reduces relevance."
            ],
            'closed': [
                "Business appears to be permanently closed.",
                "Closed business reduces result usefulness.",
                "No longer operational according to information.",
                "Business closure affects relevance negatively.",
                "Closed status makes result not helpful."
            ],
            'data_accuracy': [
                "Data accuracy issues affect result quality.",
                "Information appears outdated or incorrect.",
                "Data inconsistencies noted in the result.",
                "Accuracy concerns with business information.",
                "Data quality issues impact usefulness."
            ],
            'low_rating': [
                "Low customer rating affects result quality.",
                "Rating suggests potential quality issues.",
                "Customer feedback indicates concerns.",
                "Rating reflects mixed user experiences.",
                "Low rating may indicate service issues."
            ],
            'few_reviews': [
                "Limited review data available.",
                "Few customer reviews to assess quality.",
                "Insufficient feedback for quality evaluation.",
                "Limited review information available.",
                "Sparse review data noted."
            ]
        }
        
        # Intent-specific comments
        self.intent_comments = {
            'navigational': [
                "Strong match for specific business search.",
                "Exactly what user was looking for.",
                "Perfect navigational result.",
                "Direct match for named business query.",
                "Precise match for navigation intent."
            ],
            'local': [
                "Good local search result.",
                "Relevant for local area search.",
                "Appropriate for location-based query.",
                "Suitable for nearby business search.",
                "Good local area match."
            ],
            'informational': [
                "Provides useful information for query.",
                "Informative result for user's question.",
                "Good information source for query.",
                "Helpful informational content.",
                "Useful information for user's needs."
            ],
            'transactional': [
                "Supports user's transaction intent.",
                "Good for completing desired action.",
                "Facilitates user's business needs.",
                "Appropriate for transaction purpose.",
                "Supports user's commercial intent."
            ]
        }
        
        self.logger.info("Comment generator initialized")
    
    def load_comment_examples(self) -> List[str]:
        """Load comment examples from file"""
        examples = []
        
        comment_file = Path("comments_examples.txt")
        if comment_file.exists():
            try:
                with open(comment_file, 'r', encoding='utf-8') as f:
                    examples = [line.strip() for line in f if line.strip()]
                self.logger.info(f"Loaded {len(examples)} comment examples")
            except Exception as e:
                self.logger.error(f"Failed to load comment examples: {e}")
        
        return examples
    
    def generate_comment(self, rating_result: RatingResult) -> str:
        """Generate appropriate comment based on rating result"""
        self.logger.info(f"Generating comment for rating: {rating_result.rating}")
        
        # Check if we should generate a comment (not always required)
        if random.random() < 0.3:  # 30% chance of no comment
            return ""
        
        # Choose comment generation strategy
        strategies = [
            self._generate_template_comment,
            self._generate_issue_based_comment,
            self._generate_intent_based_comment,
            self._generate_example_based_comment
        ]
        
        # Weight strategies based on rating and available data
        weights = self._calculate_strategy_weights(rating_result)
        
        # Choose strategy
        strategy = random.choices(strategies, weights=weights)[0]
        
        # Generate comment
        comment = strategy(rating_result)
        
        # Post-process comment
        comment = self._post_process_comment(comment, rating_result)
        
        self.logger.info(f"Generated comment: {comment[:50]}...")
        return comment
    
    def _calculate_strategy_weights(self, rating_result: RatingResult) -> List[float]:
        """Calculate weights for different comment generation strategies"""
        weights = [1.0, 1.0, 1.0, 1.0]  # Base weights
        
        # Increase issue-based weight if there are issues
        if rating_result.demotion_reason or rating_result.data_issues:
            weights[1] += 2.0
        
        # Increase intent-based weight if intent is clear
        if rating_result.user_intent_match:
            weights[2] += 1.0
        
        # Increase example-based weight if we have examples
        if self.comment_examples:
            weights[3] += 1.0
        
        return weights
    
    def _generate_template_comment(self, rating_result: RatingResult) -> str:
        """Generate comment using templates"""
        rating = rating_result.rating
        
        if rating in self.comment_templates:
            return random.choice(self.comment_templates[rating])
        
        return "Standard result evaluation completed."
    
    def _generate_issue_based_comment(self, rating_result: RatingResult) -> str:
        """Generate comment based on specific issues"""
        comment_parts = []
        
        # Add base rating comment
        if rating_result.rating in self.comment_templates:
            comment_parts.append(random.choice(self.comment_templates[rating_result.rating]))
        
        # Add issue-specific comments
        if rating_result.demotion_reason:
            issue_type = self._classify_issue_type(rating_result.demotion_reason)
            if issue_type in self.issue_comments:
                comment_parts.append(random.choice(self.issue_comments[issue_type]))
        
        # Add data issue comments
        if rating_result.data_issues:
            comment_parts.append(random.choice(self.issue_comments['data_accuracy']))
        
        return " ".join(comment_parts)
    
    def _generate_intent_based_comment(self, rating_result: RatingResult) -> str:
        """Generate comment based on user intent"""
        comment_parts = []
        
        # Add intent-specific comment
        if rating_result.user_intent_match and rating_result.user_intent_match in self.intent_comments:
            comment_parts.append(random.choice(self.intent_comments[rating_result.user_intent_match]))
        
        # Add rating context
        if rating_result.rating in self.comment_templates:
            comment_parts.append(random.choice(self.comment_templates[rating_result.rating]))
        
        return " ".join(comment_parts)
    
    def _generate_example_based_comment(self, rating_result: RatingResult) -> str:
        """Generate comment based on loaded examples"""
        if not self.comment_examples:
            return self._generate_template_comment(rating_result)
        
        # Filter examples by rating if possible
        rating_examples = []
        for example in self.comment_examples:
            if self._matches_rating_tone(example, rating_result.rating):
                rating_examples.append(example)
        
        if rating_examples:
            return random.choice(rating_examples)
        else:
            return random.choice(self.comment_examples)
    
    def _classify_issue_type(self, demotion_reason: str) -> str:
        """Classify issue type from demotion reason"""
        reason_lower = demotion_reason.lower()
        
        if 'distance' in reason_lower or 'miles' in reason_lower or 'far' in reason_lower:
            return 'distance'
        elif 'closed' in reason_lower or 'closure' in reason_lower:
            return 'closed'
        elif 'rating' in reason_lower and 'low' in reason_lower:
            return 'low_rating'
        elif 'review' in reason_lower and ('few' in reason_lower or 'limited' in reason_lower):
            return 'few_reviews'
        else:
            return 'data_accuracy'
    
    def _matches_rating_tone(self, comment: str, rating: str) -> bool:
        """Check if comment matches the tone of the rating"""
        comment_lower = comment.lower()
        
        positive_words = ['excellent', 'great', 'perfect', 'outstanding', 'good']
        negative_words = ['poor', 'bad', 'terrible', 'inadequate', 'not relevant']
        neutral_words = ['fair', 'adequate', 'acceptable', 'moderate']
        
        if rating in ['excellent', 'good']:
            return any(word in comment_lower for word in positive_words)
        elif rating in ['poor', 'not_relevant']:
            return any(word in comment_lower for word in negative_words)
        elif rating == 'fair':
            return any(word in comment_lower for word in neutral_words)
        
        return True  # Default to match
    
    def _post_process_comment(self, comment: str, rating_result: RatingResult) -> str:
        """Post-process comment for consistency and quality"""
        # Ensure comment is not too long
        if len(comment) > 200:
            sentences = comment.split('.')
            comment = '. '.join(sentences[:2]) + '.'
        
        # Ensure comment is not too short
        if len(comment) < 20:
            comment += " " + random.choice(self.comment_templates.get(rating_result.rating, ["Standard evaluation."]))
        
        # Capitalize first letter
        comment = comment.strip()
        if comment:
            comment = comment[0].upper() + comment[1:]
        
        # Ensure proper ending
        if not comment.endswith('.'):
            comment += '.'
        
        return comment
    
    def generate_contextual_comment(self, rating_result: RatingResult, context: Dict[str, Any]) -> str:
        """Generate comment with additional context"""
        comment_parts = []
        
        # Add query context
        if 'query' in context:
            query = context['query']
            if 'restaurant' in query.lower():
                comment_parts.append("Restaurant search result evaluated.")
            elif 'gas' in query.lower():
                comment_parts.append("Gas station search result evaluated.")
            elif 'hotel' in query.lower():
                comment_parts.append("Hotel search result evaluated.")
        
        # Add location context
        if 'user_location' in context:
            comment_parts.append(f"Evaluated for {context['user_location']} area.")
        
        # Add standard comment
        standard_comment = self.generate_comment(rating_result)
        if standard_comment:
            comment_parts.append(standard_comment)
        
        return " ".join(comment_parts)
    
    def generate_demotion_comment(self, demotion_reason: str, severity: str = 'minor') -> str:
        """Generate specific comment for demotion reason"""
        self.logger.info(f"Generating demotion comment: {demotion_reason}")
        
        # Classify the issue type
        issue_type = self._classify_issue_type(demotion_reason)
        
        # Get appropriate comments
        if issue_type in self.issue_comments:
            base_comment = random.choice(self.issue_comments[issue_type])
        else:
            base_comment = "Result has issues that affect relevance."
        
        # Add severity context
        if severity == 'major':
            base_comment = "Significant issue: " + base_comment
        elif severity == 'critical':
            base_comment = "Critical issue: " + base_comment
        
        return base_comment
    
    def validate_comment(self, comment: str, rating: str) -> Dict[str, Any]:
        """Validate comment appropriateness for rating"""
        validation = {
            'valid': True,
            'issues': [],
            'suggestions': []
        }
        
        comment_lower = comment.lower()
        
        # Check for tone consistency
        if rating in ['excellent', 'good']:
            if any(word in comment_lower for word in ['poor', 'bad', 'terrible']):
                validation['valid'] = False
                validation['issues'].append('Negative tone for positive rating')
        
        elif rating in ['poor', 'not_relevant']:
            if any(word in comment_lower for word in ['excellent', 'great', 'perfect']):
                validation['valid'] = False
                validation['issues'].append('Positive tone for negative rating')
        
        # Check length
        if len(comment) < 10:
            validation['issues'].append('Comment too short')
        elif len(comment) > 300:
            validation['issues'].append('Comment too long')
        
        # Check for completeness
        if not comment.strip():
            validation['valid'] = False
            validation['issues'].append('Empty comment')
        
        return validation
    
    def get_comment_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated comments"""
        return {
            'total_examples': len(self.comment_examples),
            'template_categories': len(self.comment_templates),
            'issue_categories': len(self.issue_comments),
            'intent_categories': len(self.intent_comments)
        }
    
    def add_comment_example(self, comment: str, rating: str):
        """Add new comment example to the collection"""
        self.comment_examples.append(comment)
        self.logger.info(f"Added new comment example for {rating}")
    
    def save_comment_examples(self):
        """Save current comment examples to file"""
        try:
            with open("comments_examples.txt", 'w', encoding='utf-8') as f:
                for example in self.comment_examples:
                    f.write(example + '\n')
            self.logger.info("Comment examples saved to file")
        except Exception as e:
            self.logger.error(f"Failed to save comment examples: {e}")
    
    def generate_batch_comments(self, rating_results: List[RatingResult]) -> List[str]:
        """Generate comments for multiple rating results"""
        comments = []
        
        for rating_result in rating_results:
            comment = self.generate_comment(rating_result)
            comments.append(comment)
        
        return comments