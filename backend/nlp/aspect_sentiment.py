# backend/nlp/aspect_sentiment.py
from transformers import pipeline

class AspectSentimentAnalyzer:
    def __init__(self):
        self.classifier = pipeline("text-classification", 
                                 model="yangheng/deberta-v3-base-absa-v1.1")
    
    def analyze_aspects(self, review_text):
        # Extract aspects like: battery life, screen quality, price, durability
        aspects = {
            'quality': ['quality', 'build', 'material', 'durable'],
            'price': ['price', 'cost', 'expensive', 'cheap', 'value'],
            'delivery': ['delivery', 'shipping', 'package', 'arrived'],
            'features': ['feature', 'function', 'performance', 'speed'],
            'design': ['design', 'look', 'style', 'color', 'size']
        }
        
        results = {}
        for aspect, keywords in aspects.items():
            # Check if aspect is mentioned
            if any(keyword in review_text.lower() for keyword in keywords):
                # Get sentiment for this aspect
                sentiment = self.classifier(f"{aspect}: {review_text}")
                results[aspect] = {
                    'sentiment': sentiment[0]['label'],
                    'score': sentiment[0]['score']
                }
        
        return results