// src/components/Analytics/ProductAnalytics.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import './Analytics.css';

const ProductAnalytics = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    fetchProductAnalytics();
  }, [productId, timeRange]);

  const fetchProductAnalytics = async () => {
    try {
      const response = await api.get(`/analytics/product/${productId}?days=${timeRange}`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching product analytics:', error);
      if (error.response?.status === 404) {
        navigate('/dashboard');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading product analytics...</p>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="error-container">
        <h2>Product not found</h2>
        <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
          Back to Dashboard
        </button>
      </div>
    );
  }

  const sentimentData = analytics.sentiment_distribution || {};
  const totalReviews = analytics.total_reviews || 0;

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <div>
          <h1>{analytics.product_name}</h1>
          <p className="product-meta">
            <span>Category: {analytics.category}</span>
            <span>•</span>
            <span>Brand: {analytics.brand}</span>
          </p>
        </div>
        <div className="time-selector">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-select"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </select>
        </div>
      </div>

      <div className="metrics-overview">
        <div className="metric-card primary">
          <h3>Average Rating</h3>
          <div className="rating-display">
            <span className="rating-value">{analytics.average_rating?.toFixed(1) || 'N/A'}</span>
            <div className="stars">
              {[1, 2, 3, 4, 5].map(star => (
                <span 
                  key={star} 
                  className={`star ${star <= Math.round(analytics.average_rating) ? 'filled' : ''}`}
                >
                  ★
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="metric-card">
          <h3>Total Reviews</h3>
          <p className="metric-value">{totalReviews}</p>
        </div>

        <div className="metric-card">
          <h3>Sentiment Score</h3>
          <p className="metric-value">
            {sentimentData.positive > 0 
              ? `${Math.round((sentimentData.positive / totalReviews) * 100)}%` 
              : 'N/A'}
          </p>
          <p className="metric-label">Positive</p>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="chart-section">
          <h2>Sentiment Distribution</h2>
          <div className="sentiment-chart">
            <div className="sentiment-bars">
              <div className="sentiment-bar">
                <div className="bar-label">Positive</div>
                <div className="bar-container">
                  <div 
                    className="bar-fill positive"
                    style={{ width: `${(sentimentData.positive / totalReviews) * 100}%` }}
                  ></div>
                </div>
                <div className="bar-value">{sentimentData.positive || 0}</div>
              </div>
              <div className="sentiment-bar">
                <div className="bar-label">Neutral</div>
                <div className="bar-container">
                  <div 
                    className="bar-fill neutral"
                    style={{ width: `${(sentimentData.neutral / totalReviews) * 100}%` }}
                  ></div>
                </div>
                <div className="bar-value">{sentimentData.neutral || 0}</div>
              </div>
              <div className="sentiment-bar">
                <div className="bar-label">Negative</div>
                <div className="bar-container">
                  <div 
                    className="bar-fill negative"
                    style={{ width: `${(sentimentData.negative / totalReviews) * 100}%` }}
                  ></div>
                </div>
                <div className="bar-value">{sentimentData.negative || 0}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="chart-section">
          <h2>Rating Distribution</h2>
          <div className="rating-chart">
            {[5, 4, 3, 2, 1].map(rating => {
              const count = analytics.rating_distribution?.[rating] || 0;
              const percentage = totalReviews > 0 ? (count / totalReviews) * 100 : 0;
              return (
                <div key={rating} className="rating-row">
                  <div className="rating-label">{rating} ★</div>
                  <div className="rating-bar-container">
                    <div 
                      className="rating-bar-fill"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <div className="rating-count">{count}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="insights-section">
        <h2>Key Insights</h2>
        <div className="insights-grid">
          <div className="insight-card">
            <h3>Most Common Sentiment</h3>
            <p className={`insight-value ${analytics.most_common_sentiment}`}>
              {analytics.most_common_sentiment || 'N/A'}
            </p>
          </div>
          <div className="insight-card">
            <h3>Trend</h3>
            <p className="insight-value">
              {analytics.trend > 0 ? '📈 Improving' : analytics.trend < 0 ? '📉 Declining' : '➡️ Stable'}
            </p>
          </div>
          <div className="insight-card">
            <h3>Review Velocity</h3>
            <p className="insight-value">
              {analytics.reviews_per_day?.toFixed(1) || 0} reviews/day
            </p>
          </div>
        </div>
      </div>

      {analytics.top_topics && analytics.top_topics.length > 0 && (
        <div className="topics-section">
          <h2>Frequently Mentioned Topics</h2>
          <div className="topics-cloud">
            {analytics.top_topics.map((topic, index) => (
              <span 
                key={index} 
                className="topic-tag"
                style={{ fontSize: `${1 + (topic.count / 10)}rem` }}
              >
                {topic.name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductAnalytics;