# backend/nlp/topic_extraction.py

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.cluster import KMeans
import spacy
from collections import defaultdict
import re

class TopicExtractor:
    def __init__(self, n_topics=10):
        self.n_topics = n_topics
        # Initialize spaCy model
        self.nlp = spacy.load('en_core_web_sm')
        
        # Initialize vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        
        # Initialize topic models
        self.lda_model = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=100
        )
        
        self.nmf_model = NMF(
            n_components=n_topics,
            random_state=42,
            max_iter=200
        )
        
        # E-commerce specific aspects
        self.aspect_categories = {
            'quality': ['quality', 'durability', 'build', 'material', 'construction'],
            'performance': ['performance', 'speed', 'efficiency', 'power', 'functionality'],
            'design': ['design', 'look', 'appearance', 'style', 'aesthetic'],
            'price': ['price', 'cost', 'value', 'expensive', 'cheap', 'affordable'],
            'service': ['service', 'support', 'customer', 'help', 'assistance'],
            'delivery': ['delivery', 'shipping', 'arrived', 'packaging', 'fast'],
            'usability': ['easy', 'simple', 'user-friendly', 'interface', 'comfortable'],
            'reliability': ['reliable', 'trustworthy', 'consistent', 'stable', 'dependable']
        }
    
    def extract_topics(self, texts, method='lda'):
        """Extract topics from a collection of texts"""
        if not texts or len(texts) < 2:
            return {'topics': [], 'doc_topics': []}
        
        # Vectorize texts
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
        except ValueError:
            return {'topics': [], 'doc_topics': []}
        
        # Apply topic modeling
        if method == 'lda':
            topic_matrix = self.lda_model.fit_transform(tfidf_matrix)
            feature_names = self.vectorizer.get_feature_names_out()
            topics = self._get_lda_topics(feature_names)
        elif method == 'nmf':
            topic_matrix = self.nmf_model.fit_transform(tfidf_matrix)
            feature_names = self.vectorizer.get_feature_names_out()
            topics = self._get_nmf_topics(feature_names)
        else:
            return {'topics': [], 'doc_topics': []}
        
        return {
            'topics': topics,
            'doc_topics': topic_matrix.tolist(),
            'method': method
        }
    
    def extract_aspects(self, texts, category=None):
        """Extract product aspects from reviews"""
        aspects = defaultdict(list)
        
        for text in texts:
            if not text or not isinstance(text, str):
                continue
                
            # Use spaCy for aspect extraction
            doc = self.nlp(text.lower())
            
            # Extract aspect-opinion pairs
            aspect_opinions = self._extract_aspect_opinion_pairs(doc)
            
            # Categorize aspects
            for aspect, opinion in aspect_opinions:
                category = self._categorize_aspect(aspect)
                if category:
                    aspects[category].append({
                        'aspect': aspect,
                        'opinion': opinion,
                        'text': text
                    })
        
        return dict(aspects)
    
    def _extract_aspect_opinion_pairs(self, doc):
        """Extract aspect-opinion pairs using dependency parsing"""
        pairs = []
        
        for token in doc:
            # Look for adjective-noun patterns
            if token.pos_ == 'ADJ' and token.head.pos_ == 'NOUN':
                aspect = token.head.text
                opinion = token.text
                pairs.append((aspect, opinion))
            
            # Look for noun-adjective patterns
            elif token.pos_ == 'NOUN' and token.head.pos_ == 'ADJ':
                aspect = token.text
                opinion = token.head.text
                pairs.append((aspect, opinion))
        
        return pairs
    
    def _categorize_aspect(self, aspect):
        """Categorize an aspect into predefined categories"""
        aspect_lower = aspect.lower()
        
        for category, keywords in self.aspect_categories.items():
            if any(keyword in aspect_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def _get_lda_topics(self, feature_names):
        """Extract topics from LDA model"""
        topics = []
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topics.append({
                'topic_id': topic_idx,
                'words': top_words,
                'weights': topic[top_words_idx].tolist()
            })
        return topics
    
    def _get_nmf_topics(self, feature_names):
        """Extract topics from NMF model"""
        topics = []
        for topic_idx, topic in enumerate(self.nmf_model.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topics.append({
                'topic_id': topic_idx,
                'words': top_words,
                'weights': topic[top_words_idx].tolist()
            })
        return topics
    
    def get_topic_keywords(self, topic_id, n_words=10):
        """Get keywords for a specific topic"""
        if hasattr(self, 'lda_model') and hasattr(self.lda_model, 'components_'):
            feature_names = self.vectorizer.get_feature_names_out()
            topic = self.lda_model.components_[topic_id]
            top_words_idx = topic.argsort()[-n_words:][::-1]
            return [feature_names[i] for i in top_words_idx]
        return []
    
    def analyze_topic_evolution(self, texts, timestamps):
        """Analyze how topics evolve over time"""
        # This would involve time-series analysis of topics
        # For now, return a simple structure
        return {
            'timeline': timestamps,
            'topic_distributions': [],
            'trends': []
        }