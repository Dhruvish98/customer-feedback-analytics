# backend/nlp/advanced_pipeline.py - Complete updated version with emoji processing
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    pipeline
)
from sentence_transformers import SentenceTransformer
import spacy
from bertopic import BERTopic
from textblob import TextBlob
import yake
from collections import defaultdict
import numpy as np
import logging
from .emoji_processor import EmojiProcessor  # Import our regex-based emoji processor
import sys
import os
# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now the import should work
from config.competitors import get_competitors_for_product


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedNLPPipeline:
    def __init__(self):
        logger.info("Initializing Advanced NLP Pipeline...")
        
        # Initialize emoji processor
        self.emoji_processor = EmojiProcessor()
        
        # Load models
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Sentiment Analysis - Using DistilBERT for efficiency
        self.sentiment_tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
            'distilbert-base-uncased-finetuned-sst-2-english'
        ).to(self.device)
        
        # Aspect-Based Sentiment Analysis
        self.absa_pipeline = pipeline(
            "text-classification",
            model="yangheng/deberta-v3-base-absa-v1.1",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Entity Recognition
        self.ner_pipeline = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Topic Modeling
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.topic_model = BERTopic(
            embedding_model=self.sentence_model,
            nr_topics='auto',
            min_topic_size=10
        )
        
        # Load spaCy for advanced text processing
        self.nlp = spacy.load("en_core_web_sm")
        
        # Keyword Extraction
        self.kw_extractor = yake.KeywordExtractor(
            lan="en",
            n=3,  # max ngram size
            dedupLim=0.7,
            top=10
        )
        
        # Emotion Detection
        self.emotion_pipeline = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Zero-shot Classification for flexible aspect detection
        self.zero_shot = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )
        
        logger.info("Advanced NLP Pipeline initialized successfully!")
    
    def process_review(self, review_text, product_info=None):
        """Complete NLP processing for a single review"""
        # First, analyze emojis
        emoji_analysis = self.emoji_processor.analyze_emoji_sentiment(review_text)
        
        # Process text with emojis handled
        processed_text_with_emojis = self.emoji_processor.replace_emojis_with_text(review_text)
        processed_text_clean = self.preprocess_text(processed_text_with_emojis)
        
        results = {
            'original_text': review_text,
            'processed_text': processed_text_clean,
            'emoji_analysis': emoji_analysis,
            'sentiment_analysis': self.analyze_sentiment_with_emojis(review_text, emoji_analysis),
            'aspect_sentiments': self.analyze_aspects(processed_text_with_emojis, product_info),
            'entities': self.extract_entities(processed_text_with_emojis),
            'emotions': self.detect_emotions_with_emojis(review_text, emoji_analysis),
            'keywords': self.extract_keywords(processed_text_with_emojis),
            'quality_metrics': self.assess_review_quality_with_emojis(review_text, emoji_analysis),
            'competitor_mentions': self.detect_competitor_mentions(review_text),
            'topics': []  # Will be filled by batch topic modeling
        }
        
        return results
    
    def preprocess_text(self, text):
        """Advanced text preprocessing"""
        doc = self.nlp(text)
        
        # Remove noise while preserving meaning
        tokens = []
        for token in doc:
            if not token.is_stop and not token.is_punct and not token.like_num:
                tokens.append(token.lemma_.lower())
        
        return " ".join(tokens)
    
    def analyze_sentiment(self, text):
        """Original sentiment analysis method (kept for backward compatibility)"""
        # Basic sentiment
        inputs = self.sentiment_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.sentiment_model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Get sentiment scores
        sentiment_scores = {
            'negative': float(probs[0][0]),
            'positive': float(probs[0][1])
        }
        sentiment_scores['neutral'] = 1 - (sentiment_scores['positive'] + sentiment_scores['negative'])
        
        # Determine primary sentiment
        primary_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        
        # Calculate subjectivity using TextBlob
        blob = TextBlob(text)
        subjectivity = blob.sentiment.subjectivity
        
        return {
            'primary_sentiment': primary_sentiment,
            'sentiment_scores': sentiment_scores,
            'confidence': float(max(probs[0])),
            'subjectivity': subjectivity
        }
    
    def analyze_sentiment_with_emojis(self, text, emoji_analysis):
        """Analyze sentiment considering both text and emojis"""
        # Get text-based sentiment
        text_without_emojis = self.emoji_processor.remove_emojis(text)
        
        if text_without_emojis.strip():
            # Analyze text sentiment
            inputs = self.sentiment_tokenizer(text_without_emojis, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.sentiment_model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get sentiment scores
            sentiment_scores = {
                'negative': float(probs[0][0]),
                'positive': float(probs[0][1])
            }
        else:
            # If only emojis, use neutral baseline
            sentiment_scores = {
                'negative': 0.33,
                'positive': 0.33
            }
        
        # Adjust scores based on emoji sentiment
        if emoji_analysis['has_emojis']:
            emoji_weight = min(0.3, emoji_analysis['emoji_count'] * 0.05)  # Cap emoji influence at 30%
            
            if emoji_analysis['emoji_sentiment'] == 'positive':
                sentiment_scores['positive'] += emoji_weight
                sentiment_scores['negative'] -= emoji_weight * 0.5
            elif emoji_analysis['emoji_sentiment'] == 'negative':
                sentiment_scores['negative'] += emoji_weight
                sentiment_scores['positive'] -= emoji_weight * 0.5
        
        # Normalize scores
        sentiment_scores = {k: max(0, v) for k, v in sentiment_scores.items()}
        sentiment_scores['neutral'] = max(0, 1 - sentiment_scores['positive'] - sentiment_scores['negative'])
        
        # Re-normalize to ensure sum is 1
        total = sum(sentiment_scores.values())
        if total > 0:
            sentiment_scores = {k: v/total for k, v in sentiment_scores.items()}
        
        # Determine primary sentiment
        primary_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        
        # Calculate subjectivity using TextBlob
        blob = TextBlob(text_without_emojis)
        subjectivity = blob.sentiment.subjectivity
        
        return {
            'primary_sentiment': primary_sentiment,
            'sentiment_scores': sentiment_scores,
            'confidence': float(max(sentiment_scores.values())),
            'subjectivity': subjectivity,
            'emoji_influence': emoji_analysis['emoji_sentiment_score'] if emoji_analysis['has_emojis'] else 0
        }
    
    def analyze_aspects(self, text, product_info=None):
        """Advanced aspect-based sentiment analysis"""
        # Define aspects based on product category
        default_aspects = ['quality', 'price', 'delivery', 'service', 'packaging']
        
        if product_info and 'category' in product_info:
            category_aspects = {
                'Electronics': ['battery', 'screen', 'performance', 'camera', 'build quality'],
                'Fashion': ['fit', 'material', 'style', 'comfort', 'color'],
                'Beauty': ['effectiveness', 'texture', 'scent', 'packaging', 'ingredients'],
                'Home': ['durability', 'design', 'functionality', 'assembly', 'size']
            }
            aspects = category_aspects.get(product_info['category'], default_aspects)
        else:
            aspects = default_aspects
        
        # Zero-shot classification for aspect detection
        aspect_results = {}
        
        # Split text into sentences for better aspect detection
        doc = self.nlp(text)
        sentences = [sent.text for sent in doc.sents]
        
        for aspect in aspects:
            aspect_sentences = []
            aspect_sentiments = []
            
            for sentence in sentences:
                # Check if aspect is mentioned in sentence
                if aspect.lower() in sentence.lower():
                    aspect_sentences.append(sentence)
                    # Get sentiment for this specific sentence
                    sent_result = self.absa_pipeline(f"{aspect}: {sentence}")
                    aspect_sentiments.append(sent_result[0])
            
            if aspect_sentences:
                # Aggregate sentiments for this aspect
                avg_score = np.mean([s['score'] for s in aspect_sentiments])
                primary_label = max(aspect_sentiments, key=lambda x: x['score'])['label']
                
                aspect_results[aspect] = {
                    'mentioned': True,
                    'sentiment': primary_label,
                    'confidence': float(avg_score),
                    'sentences': aspect_sentences[:3]  # Top 3 relevant sentences
                }
            else:
                aspect_results[aspect] = {
                    'mentioned': False,
                    'sentiment': None,
                    'confidence': 0.0,
                    'sentences': []
                }
        
        return aspect_results
    
    def extract_entities(self, text):
        """Advanced entity extraction"""
        # SpaCy NER
        doc = self.nlp(text)
        spacy_entities = {
            'brands': [],
            'products': [],
            'features': [],
            'locations': []
        }
        
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT']:
                spacy_entities['brands'].append(ent.text)
            elif ent.label_ in ['GPE', 'LOC']:
                spacy_entities['locations'].append(ent.text)
        
        # BERT NER for additional entities
        bert_entities = self.ner_pipeline(text)
        
        # Combine and deduplicate
        all_entities = defaultdict(list)
        for entity in bert_entities:
            entity_type = entity['entity'].split('-')[-1]
            all_entities[entity_type].append(entity['word'])
        
        # Merge results
        final_entities = {
            'brands': list(set(spacy_entities['brands'] + all_entities.get('ORG', []))),
            'locations': list(set(spacy_entities['locations'] + all_entities.get('LOC', []))),
            'persons': list(set(all_entities.get('PER', []))),
            'miscellaneous': list(set(all_entities.get('MISC', [])))
        }
        
        return final_entities
    
    def detect_emotions(self, text):
        """Original emotion detection (kept for backward compatibility)"""
        emotions = self.emotion_pipeline(text)
        
        # Create emotion dictionary
        emotion_scores = {}
        for emotion in emotions:
            emotion_scores[emotion['label']] = emotion['score']
        
        # Get primary emotion
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        
        return {
            'primary_emotion': primary_emotion,
            'emotion_scores': emotion_scores,
            'emotional_intensity': self.calculate_emotional_intensity(text)
        }
    
    def detect_emotions_with_emojis(self, text, emoji_analysis):
        """Detect emotions considering emojis"""
        # Remove emojis for text-based emotion detection
        text_without_emojis = self.emoji_processor.remove_emojis(text)
        
        if text_without_emojis.strip():
            emotions = self.emotion_pipeline(text_without_emojis)
        else:
            # Default neutral emotions if only emojis
            emotions = [{'label': 'neutral', 'score': 1.0}]
        
        # Create emotion dictionary
        emotion_scores = {}
        for emotion in emotions:
            emotion_scores[emotion['label']] = emotion['score']
        
        # Adjust based on emoji emotions
        if emoji_analysis['has_emojis']:
            # Map emoji sentiment to emotions
            if emoji_analysis['emoji_sentiment'] == 'positive':
                # Boost positive emotions
                for emotion in ['joy', 'love', 'surprise']:
                    if emotion in emotion_scores:
                        emotion_scores[emotion] *= 1.2
                    else:
                        emotion_scores[emotion] = 0.2
            elif emoji_analysis['emoji_sentiment'] == 'negative':
                # Boost negative emotions
                for emotion in ['sadness', 'anger', 'fear']:
                    if emotion in emotion_scores:
                        emotion_scores[emotion] *= 1.2
                    else:
                        emotion_scores[emotion] = 0.2
        
        # Normalize scores
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {k: v/total for k, v in emotion_scores.items()}
        
        # Get primary emotion
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        
        return {
            'primary_emotion': primary_emotion,
            'emotion_scores': emotion_scores,
            'emotional_intensity': self.calculate_emotional_intensity_with_emojis(text, emoji_analysis)
        }
    
    def calculate_emotional_intensity(self, text):
        """Calculate emotional intensity based on various factors"""
        # Count exclamation marks, capital letters, emotion words
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        # Emotion word lists
        strong_positive = ['amazing', 'excellent', 'fantastic', 'love', 'perfect']
        strong_negative = ['terrible', 'horrible', 'awful', 'hate', 'worst']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in strong_positive if word in text_lower)
        negative_count = sum(1 for word in strong_negative if word in text_lower)
        
        intensity = min(1.0, (exclamation_count * 0.2 + caps_ratio * 2 + 
                            (positive_count + negative_count) * 0.3))
        
        return float(intensity)
    
    def calculate_emotional_intensity_with_emojis(self, text, emoji_analysis):
        """Calculate emotional intensity including emoji contribution"""
        base_intensity = self.calculate_emotional_intensity(text)
        
        # Add emoji contribution
        emoji_intensity = 0
        if emoji_analysis['has_emojis']:
            # More emojis = higher intensity
            emoji_intensity = min(0.3, emoji_analysis['emoji_count'] * 0.05)
            
            # Extreme emoji sentiment adds to intensity
            if abs(emoji_analysis['emoji_sentiment_score']) > 0.5:
                emoji_intensity += 0.1
        
        total_intensity = min(1.0, base_intensity + emoji_intensity)
        return float(total_intensity)
    
    def extract_keywords(self, text):
        """Extract keywords and key phrases"""
        keywords = self.kw_extractor.extract_keywords(text)
        
        # Format keywords with scores
        formatted_keywords = []
        for kw, score in keywords:
            formatted_keywords.append({
                'keyword': kw,
                'score': float(score),
                'word_count': len(kw.split())
            })
        
        return formatted_keywords
    
    def assess_review_quality(self, text):
        """Original quality assessment (kept for backward compatibility)"""
        quality_factors = {}
        
        # Length check
        word_count = len(text.split())
        quality_factors['word_count'] = word_count
        quality_factors['has_min_length'] = word_count >= 10
        
        # Specificity check
        doc = self.nlp(text)
        
        # Count specific details (numbers, proper nouns, technical terms)
        specific_details = 0
        for token in doc:
            if token.pos_ in ['PROPN', 'NUM'] or token.ent_type_:
                specific_details += 1
        
        quality_factors['specificity_score'] = min(1.0, specific_details / 10)
        
        # Check for generic phrases (potential fake review indicators)
        generic_phrases = [
            'great product', 'good quality', 'fast delivery',
            'highly recommend', 'five stars', 'worth the money'
        ]
        
        generic_count = sum(1 for phrase in generic_phrases if phrase in text.lower())
        quality_factors['generic_phrase_count'] = generic_count
        
        # Calculate overall quality score
        quality_score = (
            0.3 * min(1.0, word_count / 50) +  # Length factor
            0.4 * quality_factors['specificity_score'] +  # Specificity
            0.3 * max(0, 1 - generic_count / 3)  # Originality
        )
        
        # Authenticity indicators
        authenticity_factors = {
            'has_pros_and_cons': self.check_balanced_review(text),
            'personal_experience': self.check_personal_experience(text),
            'verified_language_patterns': self.check_language_patterns(text)
        }
        
        authenticity_score = sum(authenticity_factors.values()) / len(authenticity_factors)
        
        return {
            'quality_score': float(quality_score),
            'authenticity_score': float(authenticity_score),
            'quality_factors': quality_factors,
            'authenticity_factors': authenticity_factors,
            'is_likely_fake': authenticity_score < 0.3
        }
    
    def assess_review_quality_with_emojis(self, text, emoji_analysis):
        """Assess review quality considering emoji usage"""
        # Remove emojis for clean text analysis
        text_clean = self.emoji_processor.remove_emojis(text)
        
        quality_factors = {}
        
        # Length check (on clean text)
        word_count = len(text_clean.split())
        quality_factors['word_count'] = word_count
        quality_factors['has_min_length'] = word_count >= 10
        
        # Emoji usage analysis
        quality_factors['emoji_count'] = emoji_analysis['emoji_count']
        quality_factors['excessive_emojis'] = emoji_analysis['emoji_count'] > 10
        quality_factors['emoji_to_word_ratio'] = emoji_analysis['emoji_count'] / max(word_count, 1)
        
        # Specificity check
        doc = self.nlp(text_clean)
        
        # Count specific details (numbers, proper nouns, technical terms)
        specific_details = 0
        for token in doc:
            if token.pos_ in ['PROPN', 'NUM'] or token.ent_type_:
                specific_details += 1
        
        quality_factors['specificity_score'] = min(1.0, specific_details / 10)
        
        # Check for generic phrases (potential fake review indicators)
        generic_phrases = [
            'great product', 'good quality', 'fast delivery',
            'highly recommend', 'five stars', 'worth the money'
        ]
        
        generic_count = sum(1 for phrase in generic_phrases if phrase in text_clean.lower())
        quality_factors['generic_phrase_count'] = generic_count
        
        # Calculate overall quality score
        quality_score = (
            0.3 * min(1.0, word_count / 50) +  # Length factor
            0.3 * quality_factors['specificity_score'] +  # Specificity
            0.2 * max(0, 1 - generic_count / 3) +  # Originality
            0.2 * (0 if quality_factors['excessive_emojis'] else 1)  # Emoji penalty
        )
        
        # Authenticity indicators
        authenticity_factors = {
            'has_pros_and_cons': self.check_balanced_review(text_clean),
            'personal_experience': self.check_personal_experience(text_clean),
            'verified_language_patterns': self.check_language_patterns(text_clean),
            'reasonable_emoji_usage': not quality_factors['excessive_emojis'] and quality_factors['emoji_to_word_ratio'] < 0.5
        }
        
        authenticity_score = sum(authenticity_factors.values()) / len(authenticity_factors)
        
        return {
            'quality_score': float(quality_score),
            'authenticity_score': float(authenticity_score),
            'quality_factors': quality_factors,
            'authenticity_factors': authenticity_factors,
            'is_likely_fake': authenticity_score < 0.3,
            'emoji_usage_appropriate': quality_factors['emoji_to_word_ratio'] < 0.3
        }
    
    def check_balanced_review(self, text):
        """Check if review mentions both pros and cons"""
        positive_indicators = ['good', 'great', 'love', 'excellent', 'pro', 'advantage']
        negative_indicators = ['bad', 'poor', 'hate', 'terrible', 'con', 'disadvantage', 'but', 'however']
        
        has_positive = any(word in text.lower() for word in positive_indicators)
        has_negative = any(word in text.lower() for word in negative_indicators)
        
        return has_positive and has_negative
    
    def check_personal_experience(self, text):
        """Check for personal experience indicators"""
        personal_pronouns = ['i', 'my', 'me', 'we', 'our']
        experience_verbs = ['bought', 'purchased', 'used', 'tried', 'tested']
        
        text_lower = text.lower()
        has_pronouns = any(pronoun in text_lower.split() for pronoun in personal_pronouns)
        has_experience = any(verb in text_lower for verb in experience_verbs)
        
        return has_pronouns and has_experience
    
    def check_language_patterns(self, text):
        """Check for natural language patterns"""
        doc = self.nlp(text)
        
        # Check sentence variety
        sentence_lengths = [len(sent.text.split()) for sent in doc.sents]
        length_variance = np.var(sentence_lengths) if len(sentence_lengths) > 1 else 0
        
        # Check vocabulary diversity
        words = [token.text.lower() for token in doc if token.is_alpha]
        vocabulary_diversity = len(set(words)) / len(words) if words else 0
        
        return length_variance > 5 and vocabulary_diversity > 0.5
    
    def detect_competitor_mentions(self, text, product_category=None, product_subcategory=None):
        """Detect and analyze competitor mentions with category context"""
        # Import competitor configuration
        from config.competitors import get_competitors_for_product
        
        # Common competitor indicators
        competitor_keywords = [
            'compared to', 'versus', 'vs', 'better than', 'worse than',
            'switched from', 'unlike', 'alternative to', 'instead of',
            'prefer', 'chose over', 'replaced'
        ]
        
        # Get category-specific competitors
        known_competitors = get_competitors_for_product(product_category, product_subcategory)
        
        mentions = []
        text_lower = text.lower()
        
        # Check for competitor keywords
        for keyword in competitor_keywords:
            if keyword in text_lower:
                # Extract context around keyword
                keyword_pos = text_lower.find(keyword)
                start = max(0, keyword_pos - 100)
                end = min(len(text), keyword_pos + len(keyword) + 100)
                context = text[start:end]
                
                # Check for brand mentions in context
                for competitor in known_competitors:
                    if competitor.lower() in context.lower():
                        # Analyze sentiment of comparison
                        comparison_sentiment = self.analyze_sentiment(context)
                        
                        # Determine if favorable based on keyword and sentiment
                        favorable = self._is_comparison_favorable(keyword, comparison_sentiment['primary_sentiment'])
                        
                        mentions.append({
                            'competitor': competitor,
                            'context': context.strip(),
                            'comparison_type': keyword,
                            'favorable_to_us': favorable
                        })
        
        # Also check for direct mentions without comparison keywords
        for competitor in known_competitors:
            if competitor.lower() in text_lower and not any(m['competitor'] == competitor for m in mentions):
                # Find all occurrences
                import re
                pattern = re.compile(r'\b' + re.escape(competitor) + r'\b', re.IGNORECASE)
                
                for match in pattern.finditer(text):
                    pos = match.start()
                    start = max(0, pos - 100)
                    end = min(len(text), pos + len(competitor) + 100)
                    context = text[start:end].strip()
                    
                    sentiment = self.analyze_sentiment(context)
                    
                    mentions.append({
                        'competitor': competitor,
                        'context': context,
                        'comparison_type': 'direct_mention',
                        'favorable_to_us': sentiment['primary_sentiment'] != 'positive'
                    })
                    break  # Only take first mention of each competitor
        
        return mentions[:5]  # Limit to 5 mentions to avoid overwhelming

        def _is_comparison_favorable(self, keyword, sentiment):
            """Determine if a comparison is favorable to us based on keyword and sentiment"""
            negative_comparisons = ['better than', 'prefer', 'chose over', 'replaced']
            positive_comparisons = ['worse than', 'switched from', 'unlike']
            
            if any(neg in keyword for neg in negative_comparisons):
                # If they say competitor is "better than" us, it's unfavorable
                return sentiment == 'negative'  # Unless the overall sentiment is negative
            elif any(pos in keyword for pos in positive_comparisons):
                # If they say competitor is "worse than" us, it's favorable
                return True
            else:
                # For neutral keywords like "versus", "compared to"
                return sentiment == 'positive'
    
    def batch_process_topics(self, reviews):
        """Process topics for a batch of reviews"""
        if not reviews:
            return {}
        
        # Extract texts
        texts = [r['processed_text'] for r in reviews]
        
        # Fit topic model
        topics, probs = self.topic_model.fit_transform(texts)
        
        # Get topic info
        topic_info = self.topic_model.get_topic_info()
        
        # Assign topics back to reviews
        for i, review in enumerate(reviews):
            topic_id = topics[i]
            if topic_id != -1:  # -1 is outlier topic
                topic_words = self.topic_model.get_topic(topic_id)
                review['topics'] = {
                    'topic_id': int(topic_id),
                    'topic_words': [word for word, _ in topic_words[:5]],
                    'probability': float(probs[i])
                }
            else:
                review['topics'] = {
                    'topic_id': -1,
                    'topic_words': [],
                    'probability': 0.0
                }
        
        return {
            'topic_info': topic_info.to_dict(),
            'num_topics': len(set(topics)) - 1  # Exclude outlier topic
        }