// src/components/Analytics/CategoryAnalytics.jsx - Updated error handling
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../services/api';
import './Analytics.css';

const CategoryAnalytics = () => {
  const { category } = useParams();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('rating');

  useEffect(() => {
    fetchCategoryAnalytics();
  }, [category]);

  const fetchCategoryAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log(`Fetching analytics for category: ${category}`);
      
      const response = await api.get(`/analytics/category/${category}`);
      console.log('Category analytics response:', response.data);
      
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching category analytics:', error);
      setError(error.response?.data?.error || 'Failed to load category analytics');
    } finally {
      setLoading(false);
    }
  };

  const sortProducts = (products) => {
    if (!products || !Array.isArray(products)) return [];
    
    return [...products].sort((a, b) => {
      switch (sortBy) {
        case 'rating':
          return (b.average_rating || 0) - (a.average_rating || 0);
        case 'reviews':
          return (b.review_count || 0) - (a.review_count || 0);
        case 'sentiment':
          return (b.positive_percentage || 0) - (a.positive_percentage || 0);
        default:
          return 0;
      }
    });
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading category analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error Loading Analytics</h2>
        <p>{error}</p>
        <Link to="/dashboard" className="btn btn-primary">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="error-container">
        <h2>No Data Available</h2>
        <p>No analytics data found for {category} category</p>
        <Link to="/dashboard" className="btn btn-primary">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const sortedProducts = sortProducts(analytics.products);

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <div>
          <h1>{category} Analytics</h1>
          <p>Performance overview of all products in this category</p>
        </div>
        <Link to="/dashboard" className="btn btn-secondary">
          ← Back to Dashboard
        </Link>
      </div>

      <div className="category-overview">
        <div className="overview-card">
          <h3>Total Products</h3>
          <p className="overview-value">{analytics.total_products || 0}</p>
        </div>
        <div className="overview-card">
          <h3>Total Reviews</h3>
          <p className="overview-value">{analytics.total_reviews || 0}</p>
        </div>
        <div className="overview-card">
          <h3>Average Rating</h3>
          <p className="overview-value">
            {analytics.average_rating ? analytics.average_rating.toFixed(1) : 'N/A'}
          </p>
        </div>
        <div className="overview-card">
          <h3>Top Brand</h3>
          <p className="overview-value">{analytics.top_brand || 'N/A'}</p>
        </div>
      </div>

      {sortedProducts.length > 0 ? (
        <div className="products-section">
          <div className="section-header">
            <h2>Products Performance</h2>
            <div className="sort-controls">
              <label>Sort by:</label>
              <select 
                value={sortBy} 
                onChange={(e) => setSortBy(e.target.value)}
                className="sort-select"
              >
                <option value="rating">Rating</option>
                <option value="reviews">Review Count</option>
                <option value="sentiment">Sentiment Score</option>
              </select>
            </div>
          </div>

          <div className="products-table">
            <div className="table-header">
              <div className="th-product">Product</div>
              <div className="th-brand">Brand</div>
              <div className="th-rating">Rating</div>
              <div className="th-reviews">Reviews</div>
              <div className="th-sentiment">Sentiment</div>
              <div className="th-action">Action</div>
            </div>
            
            {sortedProducts.map(product => (
              <div key={product.product_id} className="table-row">
                <div className="td-product">{product.product_name}</div>
                <div className="td-brand">{product.brand}</div>
                <div className="td-rating">
                  <span className="rating-badge">
                    {product.average_rating ? product.average_rating.toFixed(1) : 'N/A'} ★
                  </span>
                </div>
                <div className="td-reviews">{product.review_count || 0}</div>
                <div className="td-sentiment">
                  {product.review_count > 0 ? (
                    <>
                      <div className="sentiment-indicator">
                        <div 
                          className="sentiment-bar positive"
                          style={{ width: `${product.positive_percentage || 0}%` }}
                        ></div>
                      </div>
                      <span className="sentiment-text">
                        {(product.positive_percentage || 0).toFixed(0)}% positive
                      </span>
                    </>
                  ) : (
                    <span className="sentiment-text">No reviews</span>
                  )}
                </div>
                <div className="td-action">
                  <Link 
                    to={`/analytics/product/${product.product_id}`}
                    className="view-link"
                  >
                    View Details →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="no-products">
          <p>No products found in this category</p>
        </div>
      )}

      {analytics.brand_comparison && Object.keys(analytics.brand_comparison).length > 0 && (
        <div className="comparison-section">
          <h2>Brand Comparison</h2>
          <div className="brand-comparison-chart">
            {Object.entries(analytics.brand_comparison).map(([brand, data]) => (
              <div key={brand} className="brand-item">
                <div className="brand-name">{brand}</div>
                <div className="brand-metrics">
                  <div className="metric">
                    <span className="metric-label">Avg Rating:</span>
                    <span className="metric-value">
                      {data.avg_rating ? data.avg_rating.toFixed(1) : 'N/A'}
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Reviews:</span>
                    <span className="metric-value">{data.review_count || 0}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Positive:</span>
                    <span className="metric-value">
                      {data.positive_percentage ? `${data.positive_percentage.toFixed(0)}%` : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CategoryAnalytics;