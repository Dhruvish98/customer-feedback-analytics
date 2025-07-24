# backend/nlp/sentiment_analysis.py

import torch
import spacy
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    pipeline
)
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

class SentimentAnalyzer:
    def __init__(self, model_type='transformer'):
        self.model_type = model_type
        
        # Initialize spaCy model
        self.nlp = spacy.load('en_core_web_sm')
        
        if model_type == 'transformer':
            # Use pre-trained BERT for sentiment analysis
            self.model_name = 'nlptown/bert-base-multilingual-uncased-sentiment'
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.sentiment_pipeline = pipeline(
                'sentiment-analysis', 
                model=self.model, 
                tokenizer=self.tokenizer
            )
        else:
            # Load traditional ML model if needed
            self.model = None
            
    def predict_sentiment(self, text):
        """Predict sentiment for a single text"""
        if self.model_type == 'transformer':
            # Get prediction
            result = self.sentiment_pipeline(text[:512])[0]  # Truncate for BERT
            
            # Convert 5-star rating to sentiment
            stars = int(result['label'].split()[0])
            if stars >= 4:
                sentiment = 'positive'
                confidence = result['score']
            elif stars <= 2:
                sentiment = 'negative'
                confidence = result['score']
            else:
                sentiment = 'neutral'
                confidence = result['score']
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'raw_score': stars,
                'details': result
            }
    
    def predict_batch(self, texts):
        """Predict sentiment for multiple texts"""
        results = []
        for text in texts:
            results.append(self.predict_sentiment(text))
        return results
    
    def fine_tune_model(self, texts, labels):
        """Fine-tune the model on domain-specific data"""
        # This would involve fine-tuning the transformer model
        # For demonstration, we'll use a simplified approach
        pass
    
    def get_sentiment_explanations(self, text):
        """Get explanations for sentiment prediction"""
        # Use attention weights or LIME/SHAP for explanations
        doc = self.nlp(text)
        
        # Simple keyword-based explanation
        positive_words = {'excellent', 'amazing', 'love', 'perfect', 'great'}
        negative_words = {'terrible', 'awful', 'hate', 'disappointed', 'poor'}
        
        found_positive = [token.text for token in doc if token.text in positive_words]
        found_negative = [token.text for token in doc if token.text in negative_words]
        
        explanation = {
            'positive_indicators': found_positive,
            'negative_indicators': found_negative,
            'key_phrases': self._extract_key_phrases(text)
        }
        
        return explanation
    
    def _extract_key_phrases(self, text):
        """Extract key phrases that influence sentiment"""
        doc = self.nlp(text)
        phrases = []
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            phrases.append(chunk.text)
        
        return phrases