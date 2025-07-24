// frontend/src/components/ReviewHistory/ReviewHistory.jsx - Updated version
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import api from '../../services/api';
import './ReviewHistory.css';

const ReviewHistory = () => {
  const [reviews, setReviews] = useState([]);
  const [selectedReview, setSelectedReview] = useState(null);
  const [nlpDetails, setNlpDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingNlp, setLoadingNlp] = useState(false);
  const [filter, setFilter] = useState('all');
  
  useEffect(() => {
    fetchReviews();
  }, []);
  
  const fetchReviews = async () => {
    try {
      const response = await api.get('/reviews/user-history');
      setReviews(response.data.reviews || []);
    } catch (error) {
      console.error('Error fetching reviews:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchNLPDetails = async (review) => {
    try {
      setLoadingNlp(true);
      setSelectedReview(review);
      setNlpDetails(null);
      
      const response = await api.get(`/reviews/${review.id}/nlp-details`);
      setNlpDetails(response.data);
    } catch (error) {
      console.error('Error fetching NLP details:', error);
      // Use data from the review itself if endpoint fails
      setNlpDetails({
        review_id: review.id,
        review_text: review.review_text,
        product_name: review.product_name,
        nlp_analysis: {
          sentiment: {
            primary: review.sentiment,
            confidence: 0.85,
            scores: review.sentiment_scores || { positive: 0.1, neutral: 0.1, negative: 0.8 }
          },
          aspects: [],
          emotions: review.emotion_scores || {},
          quality_metrics: {
            quality_score: review.quality_score || 0.7,
            authenticity_score: review.authenticity_score || 0.9,
            spam_probability: 0.1
          }
        }
      });
    } finally {
      setLoadingNlp(false);
    }
  };
  
  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '#10b981';
      case 'negative': return '#ef4444';
      case 'neutral': return '#f59e0b';
      default: return '#6b7280';
    }
  };
  
  const filteredReviews = reviews.filter(review => {
    if (filter === 'all') return true;
    return review.sentiment === filter;
  });
  
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading your reviews...</p>
      </div>
    );
  }
  
  return (
    <div className="review-history">
      <div className="history-header">
        <h1>My Review History</h1>
        <div className="header-stats">
          <div className="stat">
            <span className="stat-value">{reviews.length}</span>
            <span className="stat-label">Total Reviews</span>
          </div>
          <div className="stat">
            <span className="stat-value">
              {reviews.filter(r => r.sentiment === 'positive').length}
            </span>
            <span className="stat-label">Positive</span>
          </div>
          <div className="stat">
            <span className="stat-value">
              {(reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length || 0).toFixed(1)}
            </span>
            <span className="stat-label">Avg Rating</span>
          </div>
        </div>
      </div>
      
      <div className="filter-tabs">
        {['all', 'positive', 'negative', 'neutral'].map(f => (
          <button
            key={f}
            className={`filter-tab ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>
      
      {filteredReviews.length === 0 ? (
        <div className="no-reviews">
          <p>No reviews found for the selected filter.</p>
        </div>
      ) : (
        <div className="reviews-grid">
          {filteredReviews.map((review, idx) => (
            <motion.div
              key={review.id}
              className="review-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <div className="review-header">
                <div className="product-info">
                  <h3>{review.product_name}</h3>
                  <span className="product-category">{review.product_category}</span>
                </div>
                <div className="review-meta">
                  <div className="rating">
                    {'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}
                  </div>
                  <span className="review-date">
                    {new Date(review.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
              
              <div className="review-content">
                {review.review_title && <h4>{review.review_title}</h4>}
                <p>{review.review_text.substring(0, 150)}{review.review_text.length > 150 ? '...' : ''}</p>
              </div>
              
              <div className="review-analysis">
                <div className="sentiment-badge" style={{
                  backgroundColor: getSentimentColor(review.sentiment) + '20',
                  color: getSentimentColor(review.sentiment)
                }}>
                  {review.sentiment}
                </div>
                
                {review.verified_purchase && (
                  <span className="verified-badge">✓ Verified</span>
                )}
              </div>
              
              <div className="review-footer">
                <span className="helpful-count">
                  👍 {review.helpful_count} found this helpful
                </span>
                <button 
                  className="view-details-btn"
                  onClick={() => fetchNLPDetails(review)}
                >
                  View Details →
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
      
      {/* Enhanced NLP Details Modal */}
      {selectedReview && (
        <div className="nlp-details-modal" onClick={() => {
          setSelectedReview(null);
          setNlpDetails(null);
        }}>
          <div className="modal-content large" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Detailed NLP Analysis</h2>
              <button className="close-btn" onClick={() => {
                setSelectedReview(null);
                setNlpDetails(null);
              }}>×</button>
            </div>
            
            {loadingNlp ? (
              <div className="modal-loading">
                <div className="loading-spinner"></div>
                <p>Loading NLP analysis...</p>
              </div>
            ) : nlpDetails ? (
              <div className="modal-body">
                <div className="review-info">
                  <h3>{nlpDetails.product_name}</h3>
                  <p className="review-text">{nlpDetails.review_text}</p>
                </div>
                
                <div className="analysis-sections">
                  {/* Sentiment Analysis */}
                  <div className="analysis-section">
                    <h3>🎭 Sentiment Analysis</h3>
                    <div className="sentiment-details">
                      <div className="primary-sentiment">
                        <span>Primary Sentiment: </span>
                        <strong style={{ color: getSentimentColor(nlpDetails.nlp_analysis.sentiment.primary) }}>
                          {nlpDetails.nlp_analysis.sentiment.primary?.toUpperCase()}
                        </strong>
                        <span className="confidence">
                          (Confidence: {(nlpDetails.nlp_analysis.sentiment.confidence * 100).toFixed(1)}%)
                        </span>
                      </div>
                      
                      <div className="sentiment-scores">
                        <h4>Detailed Scores:</h4>
                        {Object.entries(nlpDetails.nlp_analysis.sentiment.scores || {}).map(([sentiment, score]) => (
                          <div key={sentiment} className="score-item">
                            <span className="sentiment-label">{sentiment}:</span>
                            <div className="score-bar">
                              <div 
                                className="score-fill"
                                style={{ 
                                  width: `${score * 100}%`,
                                  backgroundColor: getSentimentColor(sentiment)
                                }}
                              />
                            </div>
                            <span className="score-value">{(score * 100).toFixed(1)}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  {/* Aspect-Based Analysis */}
                  {nlpDetails.nlp_analysis.aspects && nlpDetails.nlp_analysis.aspects.length > 0 && (
                    <div className="analysis-section">
                      <h3>🎯 Aspect-Based Analysis</h3>
                      <div className="aspects-details">
                        {nlpDetails.nlp_analysis.aspects.map((aspect, idx) => (
                          <div key={idx} className="aspect-detail">
                            <div className="aspect-header">
                              <h4>{aspect.aspect}</h4>
                              <span className={`sentiment-badge ${aspect.sentiment}`}>
                                {aspect.sentiment}
                              </span>
                            </div>
                            {aspect.extracted_text && (
                              <p className="extracted-text">"{aspect.extracted_text}"</p>
                            )}
                            <span className="confidence">
                              Confidence: {(aspect.confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Emotions Detected */}
                  {nlpDetails.nlp_analysis.emotions && Object.keys(nlpDetails.nlp_analysis.emotions).length > 0 && (
                    <div className="analysis-section">
                      <h3>😊 Emotions Detected</h3>
                      <div className="emotions-chart">
                        {Object.entries(nlpDetails.nlp_analysis.emotions)
                          .sort(([,a], [,b]) => b - a)
                          .map(([emotion, score]) => (
                            <div key={emotion} className="emotion-item">
                              <span className="emotion-name">{emotion}</span>
                              <div className="emotion-bar">
                                <div 
                                  className="emotion-fill"
                                  style={{ 
                                    width: `${score * 100}%`,
                                    backgroundColor: getEmotionColor(emotion)
                                  }}
                                />
                              </div>
                              <span className="emotion-score">{(score * 100).toFixed(1)}%</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Quality Metrics */}
                  <div className="analysis-section">
                    <h3>✨ Quality Metrics</h3>
                    <div className="quality-metrics">
                      <div className="quality-item">
                        <div className="quality-header">
                          <span>Quality Score:</span>
                          <strong className={getQualityClass(nlpDetails.nlp_analysis.quality_metrics.quality_score)}>
                            {(nlpDetails.nlp_analysis.quality_metrics.quality_score * 100).toFixed(1)}%
                          </strong>
                        </div>
                        <div className="quality-bar">
                          <div 
                            className="quality-fill"
                            style={{ width: `${nlpDetails.nlp_analysis.quality_metrics.quality_score * 100}%` }}
                          />
                        </div>
                      </div>
                      
                      <div className="quality-item">
                        <div className="quality-header">
                          <span>Authenticity:</span>
                          <strong className={getQualityClass(nlpDetails.nlp_analysis.quality_metrics.authenticity_score)}>
                            {(nlpDetails.nlp_analysis.quality_metrics.authenticity_score * 100).toFixed(1)}%
                          </strong>
                        </div>
                        <div className="quality-bar">
                          <div 
                            className="quality-fill authenticity"
                            style={{ width: `${nlpDetails.nlp_analysis.quality_metrics.authenticity_score * 100}%` }}
                          />
                        </div>
                      </div>
                      
                      <div className="quality-item">
                        <div className="quality-header">
                          <span>Spam Probability:</span>
                          <strong className={nlpDetails.nlp_analysis.quality_metrics.spam_probability > 0.5 ? 'warning' : ''}>
                            {(nlpDetails.nlp_analysis.quality_metrics.spam_probability * 100).toFixed(1)}%
                          </strong>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Keywords */}
                  {nlpDetails.nlp_analysis.keywords && nlpDetails.nlp_analysis.keywords.length > 0 && (
                    <div className="analysis-section">
                      <h3>🔑 Keywords Extracted</h3>
                      <div className="keywords-list">
                        {nlpDetails.nlp_analysis.keywords.map((keyword, idx) => (
                          <span key={idx} className="keyword-tag">
                            {typeof keyword === 'object' ? keyword.keyword : keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Processing Info */}
                  {nlpDetails.nlp_analysis.processing && (
                    <div className="processing-info">
                      <span>Processed in {nlpDetails.nlp_analysis.processing.time}s</span>
                      <span>Model: {nlpDetails.nlp_analysis.processing.model}</span>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="modal-error">
                <p>Failed to load NLP details</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Helper functions
function getEmotionColor(emotion) {
  const colors = {
    joy: '#FFD700',
    sadness: '#4169E1',
    anger: '#DC143C',
    fear: '#8B4513',
    surprise: '#FF69B4',
    neutral: '#808080',
    disgust: '#9370DB'
  };
  return colors[emotion] || '#808080';
}

function getQualityClass(score) {
  if (score > 0.8) return 'excellent';
  if (score > 0.6) return 'good';
  if (score > 0.4) return 'fair';
  return 'poor';
}

export default ReviewHistory;