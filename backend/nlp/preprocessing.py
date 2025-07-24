# backend/nlp/preprocessing.py

import re
import string
import contractions
import emoji
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class TextPreprocessor:
    def __init__(self):
        # Initialize spaCy model
        self.nlp = spacy.load('en_core_web_sm')
        
        # Initialize NLTK components
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Custom stop words for e-commerce
        self.custom_stop_words = {
            'product', 'item', 'thing', 'stuff', 'purchase', 'buy', 'bought',
            'order', 'ordered', 'delivery', 'shipping', 'price', 'cost',
            'money', 'dollar', 'dollars', 'cheap', 'expensive', 'worth'
        }
        self.stop_words.update(self.custom_stop_words)
        
        # Compile regex patterns
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.number_pattern = re.compile(r'\b\d+\b')
        
    def preprocess(self, text, extract_features=True):
        """Main preprocessing function"""
        if not text or not isinstance(text, str):
            return {
                'cleaned': '',
                'processed': '',
                'tokens': [],
                'features': {}
            }
        
        # Convert to string and normalize
        text = str(text).strip()
        
        # Stage 1: Basic cleaning
        cleaned = self._basic_cleaning(text)
        
        # Stage 2: Advanced cleaning
        processed = self._advanced_cleaning(cleaned)
        
        # Stage 3: Tokenization
        tokens = self._tokenize(processed)
        
        # Stage 4: Feature extraction (optional)
        features = {}
        if extract_features:
            features = self._extract_features(text, tokens)
        
        return {
            'cleaned': cleaned,
            'processed': processed,
            'tokens': tokens,
            'features': features
        }
    
    def _basic_cleaning(self, text):
        """Basic text cleaning"""
        text = text.lower()
        text = self.url_pattern.sub('', text)
        text = self.email_pattern.sub('', text)
        # Remove emojis using Unicode regex (best effort)
        import re
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002700-\U000027BF"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)
        text = contractions.fix(text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _advanced_cleaning(self, text):
        """Advanced text cleaning with spaCy"""
        doc = self.nlp(text)
        
        # Remove punctuation and stop words
        cleaned_tokens = []
        for token in doc:
            if not token.is_punct and not token.is_stop and not token.is_space:
                # Lemmatize the token
                cleaned_tokens.append(token.lemma_)
        
        return ' '.join(cleaned_tokens)
    
    def _tokenize(self, text):
        """Tokenize the processed text"""
        if not text:
            return []
        
        # Use NLTK tokenizer
        tokens = word_tokenize(text)
        
        # Remove stop words and short tokens
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        return tokens
    
    def _extract_features(self, original_text, tokens):
        """Extract text features"""
        features = {
            'length': len(original_text),
            'word_count': len(tokens),
            'avg_word_length': sum(len(token) for token in tokens) / len(tokens) if tokens else 0,
            'has_numbers': bool(re.search(r'\d', original_text)),
            'has_uppercase': bool(re.search(r'[A-Z]', original_text)),
            'has_punctuation': bool(re.search(r'[^\w\s]', original_text)),
            'sentiment_indicators': self._extract_sentiment_indicators(original_text)
        }
        
        return features
    
    def _extract_sentiment_indicators(self, text):
        """Extract sentiment-related indicators"""
        positive_words = {'excellent', 'amazing', 'love', 'perfect', 'great', 'good', 'nice', 'wonderful'}
        negative_words = {'terrible', 'awful', 'hate', 'disappointed', 'poor', 'bad', 'worst', 'horrible'}
        
        text_lower = text.lower()
        words = set(text_lower.split())
        
        return {
            'positive_count': len(words.intersection(positive_words)),
            'negative_count': len(words.intersection(negative_words)),
            'positive_words': list(words.intersection(positive_words)),
            'negative_words': list(words.intersection(negative_words))
        }