# backend/nlp/competitor_analysis.py
class CompetitorAnalyzer:
    def __init__(self):
        self.competitors = ['Samsung', 'Apple', 'Sony', 'LG']  # Configurable
    
    def analyze_competitor_mentions(self, review_text):
        mentions = []
        for competitor in self.competitors:
            if competitor.lower() in review_text.lower():
                # Extract comparison context
                context = self.extract_comparison_context(review_text, competitor)
                sentiment = self.analyze_comparison_sentiment(context)
                mentions.append({
                    'competitor': competitor,
                    'context': context,
                    'favorable_to_us': sentiment > 0
                })
        return mentions