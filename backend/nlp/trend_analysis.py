# backend/nlp/trend_analysis.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

class TrendAnalyzer:
    def __init__(self):
        self.time_windows = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30,
            'quarterly': 90
        }
    
    def analyze_sentiment_trends(self, reviews_df, time_window='weekly'):
        """Analyze sentiment trends over time"""
        reviews_df['review_date'] = pd.to_datetime(reviews_df['review_date'])
        
        # Group by time window
        window_days = self.time_windows.get(time_window, 7)
        reviews_df['time_bucket'] = reviews_df['review_date'].dt.to_period('W')
        
        # Calculate sentiment distribution per time bucket
        sentiment_trends = reviews_df.groupby(['time_bucket', 'sentiment']).size().unstack(fill_value=0)
        sentiment_percentages = sentiment_trends.div(sentiment_trends.sum(axis=1), axis=0) * 100
        
        # Calculate trend direction
        trend_analysis = {
            'sentiment_distribution': sentiment_percentages.to_dict(),
            'trend_direction': self._calculate_trend_direction(sentiment_percentages),
            'volatility': self._calculate_volatility(sentiment_percentages)
        }
        
        return trend_analysis
    
    def analyze_topic_trends(self, reviews_df, topics_df, time_window='monthly'):
        """Analyze how topics trend over time"""
        reviews_df['review_date'] = pd.to_datetime(reviews_df['review_date'])
        
        # Merge reviews with topics
        merged_df = pd.merge(reviews_df, topics_df, on='review_id')
        
        # Group by time and topic
        topic_trends = merged_df.groupby([
            pd.Grouper(key='review_date', freq=time_window[0].upper()),
            'topic'
        ]).size().unstack(fill_value=0)
        
        # Identify emerging and declining topics
        emerging_topics = self._identify_emerging_topics(topic_trends)
        declining_topics = self._identify_declining_topics(topic_trends)
        
        return {
            'topic_timeline': topic_trends.to_dict(),
            'emerging_topics': emerging_topics,
            'declining_topics': declining_topics
        }
    
    def analyze_brand_performance(self, reviews_df):
        """Analyze brand performance over time"""
        brand_stats = reviews_df.groupby('brand').agg({
            'rating': ['mean', 'std', 'count'],
            'sentiment': lambda x: (x == 'positive').mean()
        }).round(2)
        
        brand_stats.columns = ['avg_rating', 'rating_std', 'review_count', 'positive_ratio']
        
        # Calculate brand health score
        brand_stats['health_score'] = (
            brand_stats['avg_rating'] * 20 +
            brand_stats['positive_ratio'] * 80
        ).round(2)
        
        return brand_stats.to_dict()
    
    def _calculate_trend_direction(self, time_series):
        """Calculate if trend is increasing or decreasing"""
        if 'positive' not in time_series.columns:
            return 'neutral'
        
        positive_values = time_series['positive'].values
        x = np.arange(len(positive_values)).reshape(-1, 1)
        y = positive_values.reshape(-1, 1)
        
        model = LinearRegression()
        model.fit(x, y)
        
        slope = model.coef_[0][0]
        
        if slope > 0.5:
            return 'improving'
        elif slope < -0.5:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_volatility(self, time_series):
        """Calculate sentiment volatility"""
        if 'positive' in time_series.columns:
            return time_series['positive'].std()
        return 0
    
    def _identify_emerging_topics(self, topic_trends, threshold=0.3):
        """Identify topics that are gaining traction"""
        emerging = []
        
        for topic in topic_trends.columns:
            values = topic_trends[topic].values
            if len(values) > 3:
                recent_avg = values[-3:].mean()
                older_avg = values[:-3].mean()
                
                if older_avg > 0 and (recent_avg - older_avg) / older_avg > threshold:
                    emerging.append({
                        'topic': topic,
                        'growth_rate': ((recent_avg - older_avg) / older_avg * 100)
                    })
        
        return sorted(emerging, key=lambda x: x['growth_rate'], reverse=True)
    
    def _identify_declining_topics(self, topic_trends, threshold=-0.3):
        """Identify topics that are declining"""
        declining = []
        
        for topic in topic_trends.columns:
            values = topic_trends[topic].values
            if len(values) > 3:
                recent_avg = values[-3:].mean()
                older_avg = values[:-3].mean()
                
                if older_avg > 0 and (recent_avg - older_avg) / older_avg < threshold:
                    declining.append({
                        'topic': topic,
                        'decline_rate': ((recent_avg - older_avg) / older_avg * 100)
                    })
        
        return sorted(declining, key=lambda x: x['decline_rate'])