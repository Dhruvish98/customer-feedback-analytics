# backend/nlp/insights_extractor.py
class InsightsExtractor:
    def extract_pain_points(self, reviews_df):
        negative_reviews = reviews_df[reviews_df['sentiment'] == 'negative']
        
        # Extract common complaints using topic modeling
        pain_points = []
        for topic in self.topic_model.get_topics():
            if topic['sentiment'] == 'negative':
                pain_points.append({
                    'issue': topic['keywords'],
                    'frequency': topic['count'],
                    'example_reviews': topic['examples'],
                    'suggested_action': self.generate_action_item(topic)
                })
        
        return pain_points
    
    def extract_delight_factors(self, reviews_df):
        positive_reviews = reviews_df[reviews_df['sentiment'] == 'positive']
        
        # What makes customers extremely happy?
        delight_factors = self.analyze_superlatives(positive_reviews)
        return delight_factors