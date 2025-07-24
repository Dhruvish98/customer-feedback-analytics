# backend/nlp/review_quality.py
class ReviewQualityAnalyzer:
    def calculate_quality_score(self, review):
        factors = {
            'length': len(review.review_text.split()) > 20,
            'specificity': self.has_specific_details(review.review_text),
            'emotional_balance': self.check_emotional_balance(review.review_text),
            'verified_purchase': review.verified_purchase,
            'helpful_ratio': review.helpful_count / (review.total_votes + 1)
        }
        
        # ML model to detect fake reviews
        authenticity_score = self.fake_review_detector.predict(review.review_text)
        
        return {
            'quality_score': sum(factors.values()) / len(factors),
            'authenticity_score': authenticity_score,
            'factors': factors
        }