# backend/nlp/pipeline.py

from datetime import datetime
import pandas as pd
import json
from .preprocessing import TextPreprocessor
from .sentiment_analysis import SentimentAnalyzer
from .topic_extraction import TopicExtractor
from .entity_recognition import EntityRecognizer
from .trend_analysis import TrendAnalyzer

class NLPPipeline:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_extractor = TopicExtractor()
        self.entity_recognizer = EntityRecognizer()
        self.trend_analyzer = TrendAnalyzer()
        
        # Store processing history
        self.processing_history = []
    
    def process_single_review(self, review_data, verbose=True):
        """Process a single review through the entire pipeline"""
        start_time = datetime.now()
        
        # Initialize processing record
        processing_record = {
            'review_id': review_data.get('review_id', 'NEW'),
            'timestamp': start_time.isoformat(),
            'stages': {}
        }
        
        try:
            # Stage 1: Preprocessing
            if verbose:
                print("Stage 1: Preprocessing...")
            preprocess_result = self.preprocessor.preprocess(
                review_data['review_text'], 
                extract_features=True
            )
            processing_record['stages']['preprocessing'] = {
                'status': 'completed',
                'cleaned_text': preprocess_result['cleaned'],
                'token_count': len(preprocess_result['tokens']),
                'features': preprocess_result['features']
            }
            
            # Stage 2: Sentiment Analysis
            if verbose:
                print("Stage 2: Analyzing sentiment...")
            sentiment_result = self.sentiment_analyzer.predict_sentiment(
                preprocess_result['cleaned']
            )
            sentiment_explanation = self.sentiment_analyzer.get_sentiment_explanations(
                preprocess_result['cleaned']
            )
            processing_record['stages']['sentiment_analysis'] = {
                'status': 'completed',
                'sentiment': sentiment_result['sentiment'],
                'confidence': sentiment_result['confidence'],
                'explanation': sentiment_explanation
            }
            
            # Stage 3: Entity Recognition
            if verbose:
                print("Stage 3: Extracting entities...")
            entities = self.entity_recognizer.extract_entities(
                preprocess_result['cleaned']
            )
            processing_record['stages']['entity_recognition'] = {
                'status': 'completed',
                'entities': entities
            }
            
            # Stage 4: Topic/Aspect Extraction
            if verbose:
                print("Stage 4: Extracting topics and aspects...")
            # backend/nlp/pipeline.py (continued)

            aspects = self.topic_extractor.extract_aspects(
                [preprocess_result['cleaned']], 
                category=review_data.get('category')
            )
            processing_record['stages']['aspect_extraction'] = {
                'status': 'completed',
                'aspects': {k: len(v) for k, v in aspects.items() if v}
            }
            
            # Stage 5: Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Compile final result
            result = {
                'review_id': review_data.get('review_id', 'NEW'),
                'original_text': review_data['review_text'],
                'processed_text': preprocess_result['processed'],
                'sentiment': sentiment_result['sentiment'],
                'sentiment_confidence': sentiment_result['confidence'],
                'entities': entities,
                'aspects': aspects,
                'processing_time': processing_time,
                'processing_details': processing_record
            }
            
            # Store in history
            self.processing_history.append(processing_record)
            
            if verbose:
                print(f"Processing completed in {processing_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            processing_record['error'] = str(e)
            self.processing_history.append(processing_record)
            raise e
    
    def process_batch(self, reviews_df, batch_size=100):
        """Process multiple reviews in batches"""
        results = []
        total_reviews = len(reviews_df)
        
        for i in range(0, total_reviews, batch_size):
            batch = reviews_df.iloc[i:i+batch_size]
            batch_results = []
            
            print(f"Processing batch {i//batch_size + 1} of {total_reviews//batch_size + 1}")
            
            for _, review in batch.iterrows():
                try:
                    result = self.process_single_review(review.to_dict(), verbose=False)
                    batch_results.append(result)
                except Exception as e:
                    print(f"Error processing review {review.get('review_id', 'Unknown')}: {str(e)}")
                    continue
            
            results.extend(batch_results)
        
        return pd.DataFrame(results)
    
    def get_processing_stats(self):
        """Get statistics about processing history"""
        if not self.processing_history:
            return {}
        
        stats = {
            'total_processed': len(self.processing_history),
            'successful': len([h for h in self.processing_history if 'error' not in h]),
            'failed': len([h for h in self.processing_history if 'error' in h]),
            'average_processing_time': np.mean([
                h.get('processing_time', 0) 
                for h in self.processing_history 
                if 'processing_time' in h
            ])
        }
        
        return stats