# backend/nlp/entity_recognition.py

import spacy
from collections import defaultdict

class EntityRecognizer:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        
        # Custom patterns for e-commerce entities
        self.product_patterns = [
            'phone', 'laptop', 'tablet', 'watch', 'headphones',
            'shirt', 'dress', 'shoes', 'jeans', 'jacket',
            'refrigerator', 'microwave', 'washing machine',
            'cream', 'shampoo', 'perfume'
        ]
        
        self.brand_patterns = [
            'TechPro', 'ElectroMax', 'SmartLife', 'DigiWorld',
            'StyleHub', 'TrendyWear', 'UrbanFit'
        ]
    
    def extract_entities(self, text):
        """Extract named entities from text"""
        doc = self.nlp(text)
        
        entities = {
            'products': [],
            'brands': [],
            'money': [],
            'dates': [],
            'features': []
        }
        
        # Extract standard NER entities
        for ent in doc.ents:
            if ent.label_ == 'MONEY':
                entities['money'].append({
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            elif ent.label_ == 'DATE':
                entities['dates'].append({
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
        
        # Extract custom entities
        text_lower = text.lower()
        
        # Products
        for product in self.product_patterns:
            if product in text_lower:
                entities['products'].append(product)
        
        # Brands
        for brand in self.brand_patterns:
            if brand.lower() in text_lower:
                entities['brands'].append(brand)
        
        # Feature extraction (adjective + noun patterns)
        for token in doc:
            if token.pos_ == 'ADJ' and token.head.pos_ == 'NOUN':
                feature = f"{token.text} {token.head.text}"
                entities['features'].append(feature)
        
        return entities