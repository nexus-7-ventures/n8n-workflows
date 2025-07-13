import time
import logging


class QAAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_history = []
        self.logger.info("QA Agent initialized")
    
    def validate_rating_comment(self, rating_result, comment):
        validation_result = {
            'valid': True,
            'issues': [],
            'reason': '',
            'severity_score': 0
        }
        
        # Check rating-comment consistency
        if rating_result.rating in ['excellent', 'good'] and comment:
            negative_words = ['poor', 'bad', 'terrible', 'awful']
            if any(word in comment.lower() for word in negative_words):
                validation_result['valid'] = False
                validation_result['issues'].append('rating_comment_mismatch')
                validation_result['reason'] = 'Positive rating with negative comment'
                validation_result['severity_score'] += 2
        
        # Store validation
        self.validation_history.append({
            'timestamp': time.time(),
            'rating': rating_result.rating,
            'comment': comment,
            'valid': validation_result['valid']
        })
        
        return validation_result
    
    def suggest_improvements(self, rating_result, comment):
        suggestions = []
        
        if rating_result.rating == 'excellent' and rating_result.confidence < 0.9:
            suggestions.append("Consider stronger justification for excellent rating")
        
        if not comment and rating_result.rating in ['poor', 'not_relevant']:
            suggestions.append("Add explanatory comment for low rating")
        
        return suggestions
