// frontend/src/components/ReviewForm/ReviewForm.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import './ReviewForm.css';

const ReviewForm = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    category: '',
    brand: '',
    product_id: '',
    rating: 5,
    review_title: '',
    review_text: '',
    verified_purchase: false
  });
  
  // Dropdown data
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [products, setProducts] = useState([]);
  
  // Loading states
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [loadingBrands, setLoadingBrands] = useState(false);
  const [loadingProducts, setLoadingProducts] = useState(false);
  
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [nlpResults, setNlpResults] = useState(null);
  const [showForm, setShowForm] = useState(true); // Control form visibility

  // Fetch categories on component mount
  useEffect(() => {
    fetchCategories();
  }, []);

  // Fetch brands when category changes
  useEffect(() => {
    if (formData.category) {
      fetchBrands(formData.category);
    } else {
      setBrands([]);
      setFormData(prev => ({ ...prev, brand: '', product_id: '' }));
    }
  }, [formData.category]);

  // Fetch products when brand changes
  useEffect(() => {
    if (formData.category && formData.brand) {
      fetchProducts(formData.category, formData.brand);
    } else {
      setProducts([]);
      setFormData(prev => ({ ...prev, product_id: '' }));
    }
  }, [formData.category, formData.brand]);

  const fetchCategories = async () => {
    try {
      setLoadingCategories(true);
      const response = await api.get('/products/categories');
      setCategories(response.data.categories || []);
    } catch (err) {
      console.error('Error fetching categories:', err);
      setError('Failed to load categories');
    } finally {
      setLoadingCategories(false);
    }
  };

  const fetchBrands = async (category) => {
    try {
      setLoadingBrands(true);
      const response = await api.get(`/products/brands?category=${encodeURIComponent(category)}`);
      setBrands(response.data.brands || []);
    } catch (err) {
      console.error('Error fetching brands:', err);
      setError('Failed to load brands');
    } finally {
      setLoadingBrands(false);
    }
  };

  const fetchProducts = async (category, brand) => {
    try {
      setLoadingProducts(true);
      const response = await api.get(`/products/list?category=${encodeURIComponent(category)}&brand=${encodeURIComponent(brand)}`);
      setProducts(response.data.products || []);
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('Failed to load products');
    } finally {
      setLoadingProducts(false);
    }
  };

  const handleProductSelect = (productId) => {
    const product = products.find(p => p.id === productId);
    setSelectedProduct(product);
    setFormData({ ...formData, product_id: productId });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    
    if (!formData.product_id) {
      setError('Please select a product');
      return;
    }
    
    if (!formData.review_text || formData.review_text.length < 10) {
      setError('Review must be at least 10 characters long');
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await api.post('/reviews/submit', {
        product_id: formData.product_id,
        rating: formData.rating,
        review_title: formData.review_title,
        review_text: formData.review_text,
        verified_purchase: formData.verified_purchase
      });
      
      setSuccess(true);
      setNlpResults(response.data.nlp_analysis);
      setShowForm(false); // Hide form after successful submission
      
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit review');
    } finally {
      setLoading(false);
    }
  };

  const handleNewReview = () => {
    // Reset everything for a new review
    setFormData({
      category: '',
      brand: '',
      product_id: '',
      rating: 5,
      review_title: '',
      review_text: '',
      verified_purchase: false
    });
    setSelectedProduct(null);
    setSuccess(false);
    setNlpResults(null);
    setShowForm(true);
    setError('');
  };

  const renderStars = () => {
    return [1, 2, 3, 4, 5].map((star) => (
      <span
        key={star}
        className={`star ${formData.rating >= star ? 'filled' : ''}`}
        onClick={() => setFormData({ ...formData, rating: star })}
      >
        ★
      </span>
    ));
  };

  const getRatingText = (rating) => {
    const texts = {
      1: 'Poor',
      2: 'Fair',
      3: 'Good',
      4: 'Very Good',
      5: 'Excellent'
    };
    return texts[rating] || '';
  };

  return (
    <div className="review-form-container">
      <h2>Submit a Review</h2>
      <p className="subtitle">Share your experience and see AI-powered analysis in real-time</p>
      
      {error && showForm && (
        <div className="alert alert-error">
          {error}
        </div>
      )}
      
      {success && !showForm && (
        <div className="submission-success">
          <h3>✅ Review Submitted Successfully!</h3>
          <p>Your review has been submitted and analyzed. See the detailed AI analysis below.</p>
        </div>
      )}
      
      {showForm ? (
        <form onSubmit={handleSubmit} className="review-form">
          {/* Category Dropdown */}
          <div className="form-group">
            <label htmlFor="category">Category *</label>
            <select
              id="category"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              disabled={loadingCategories}
              required
            >
              <option value="">Select a category...</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          {/* Brand Dropdown */}
          <div className="form-group">
            <label htmlFor="brand">Brand *</label>
            <select
              id="brand"
              value={formData.brand}
              onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
              disabled={!formData.category || loadingBrands}
              required
            >
              <option value="">
                {formData.category ? 'Select a brand...' : 'Select category first'}
              </option>
              {brands.map((brand) => (
                <option key={brand} value={brand}>
                  {brand}
                </option>
              ))}
            </select>
          </div>

          {/* Product Dropdown */}
          <div className="form-group">
            <label htmlFor="product">Product *</label>
            <select
              id="product"
              value={formData.product_id}
              onChange={(e) => handleProductSelect(e.target.value)}
              disabled={!formData.brand || loadingProducts}
              required
            >
              <option value="">
                {formData.brand ? 'Select a product...' : 'Select brand first'}
              </option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name} - ${product.price}
                </option>
              ))}
            </select>
            
            {selectedProduct && (
              <div className="product-info">
                <small>
                  {selectedProduct.review_count} reviews • 
                  {selectedProduct.avg_rating > 0 && ` ${selectedProduct.avg_rating.toFixed(1)} ★`}
                </small>
              </div>
            )}
          </div>
          
          {/* Rating */}
          <div className="form-group">
            <label>Rating</label>
            <div className="rating-container">
              <div className="stars">
                {renderStars()}
              </div>
              <span className="rating-text">{getRatingText(formData.rating)}</span>
            </div>
          </div>
          
          {/* Review Title */}
          <div className="form-group">
            <label htmlFor="review_title">Review Title</label>
            <input
              type="text"
              id="review_title"
              value={formData.review_title}
              onChange={(e) => setFormData({ ...formData, review_title: e.target.value })}
              placeholder="Summarize your experience..."
              maxLength={100}
            />
          </div>
          
          {/* Review Text */}
          <div className="form-group">
            <label htmlFor="review_text">Your Review *</label>
            <textarea
              id="review_text"
              value={formData.review_text}
              onChange={(e) => setFormData({ ...formData, review_text: e.target.value })}
              placeholder="Tell us about your experience with this product..."
              rows={6}
              required
              minLength={10}
            />
            <small className="char-count">{formData.review_text.length} characters</small>
          </div>
          
          {/* Verified Purchase */}
          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={formData.verified_purchase}
                onChange={(e) => setFormData({ ...formData, verified_purchase: e.target.checked })}
              />
              This is a verified purchase
            </label>
          </div>
          
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Analyzing...' : 'Submit Review'}
          </button>
        </form>
      ) : null}
      
      {/* Enhanced NLP Results - Persistent Display */}
      {nlpResults && !showForm && (
        <div className="nlp-results-detailed">
          <h3>🤖 AI-Powered Analysis Results</h3>
          
          <div className="review-summary">
            <h4>Your Review:</h4>
            <p className="review-text-display">{formData.review_text}</p>
            <div className="review-meta">
              <span>Rating: {'★'.repeat(formData.rating)}{'☆'.repeat(5 - formData.rating)}</span>
              {formData.verified_purchase && <span className="verified">✓ Verified Purchase</span>}
            </div>
          </div>
          
          {/* Sentiment Analysis Section */}
          <div className="analysis-section sentiment-section">
            <h4>📊 Sentiment Analysis</h4>
            <div className="sentiment-main">
              <div className={`sentiment-badge large ${nlpResults.sentiment.primary_sentiment}`}>
                {nlpResults.sentiment.primary_sentiment.toUpperCase()}
              </div>
              <div className="confidence-display">
                <span className="label">Confidence Score:</span>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill"
                    style={{ width: `${(nlpResults.sentiment.confidence * 100)}%` }}
                  />
                  <span className="confidence-text">
                    {(nlpResults.sentiment.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
            
            <div className="sentiment-breakdown">
              <h5>Detailed Sentiment Scores:</h5>
              <div className="scores-grid">
                {Object.entries(nlpResults.sentiment.sentiment_scores || {}).map(([sentiment, score]) => (
                  <div key={sentiment} className="score-item">
                    <div className="score-header">
                      <span className={`sentiment-label ${sentiment}`}>{sentiment}</span>
                      <span className="score-percent">{(score * 100).toFixed(1)}%</span>
                    </div>
                    <div className="score-bar">
                      <div 
                        className={`score-fill ${sentiment}`}
                        style={{ width: `${(score * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Aspect-Based Sentiment */}
          {nlpResults.aspects && Object.keys(nlpResults.aspects).length > 0 && (
            <div className="analysis-section aspects-section">
              <h4>🎯 Aspect-Based Analysis</h4>
              <div className="aspects-grid">
                {Object.entries(nlpResults.aspects).map(([aspect, data]) => {
                  if (!data.mentioned) return null;
                  return (
                    <div key={aspect} className="aspect-card">
                      <div className="aspect-header">
                        <h5>{aspect.charAt(0).toUpperCase() + aspect.slice(1)}</h5>
                        <span className={`aspect-sentiment ${data.sentiment}`}>
                          {data.sentiment}
                        </span>
                      </div>
                      <div className="aspect-confidence">
                        <div className="confidence-mini">
                          <span>Confidence:</span>
                          <div className="confidence-bar-mini">
                            <div 
                              className="confidence-fill-mini"
                              style={{ width: `${(data.confidence * 100)}%` }}
                            />
                          </div>
                          <span>{(data.confidence * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Emotions Analysis */}
          {nlpResults.emotions && nlpResults.emotions.emotion_scores && (
            <div className="analysis-section emotions-section">
              <h4>😊 Emotion Detection</h4>
              <div className="emotions-analysis">
                {Object.entries(nlpResults.emotions.emotion_scores)
                  .sort(([,a], [,b]) => b - a)
                  .map(([emotion, score]) => (
                    <div key={emotion} className="emotion-item">
                      <div className="emotion-header">
                        <span className="emotion-name">{emotion}</span>
                        <span className="emotion-value">{(score * 100).toFixed(0)}%</span>
                      </div>
                      <div className="emotion-bar">
                        <div 
                          className={`emotion-fill ${emotion}`}
                          style={{ width: `${(score * 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Quality Metrics */}
          {nlpResults.quality && (
            <div className="analysis-section quality-section">
              <h4>✨ Review Quality Assessment</h4>
              <div className="quality-metrics">
                <div className="metric">
                  <div className="metric-header">
                    <span className="metric-name">Quality Score</span>
                    <span className="metric-value">
                      {(nlpResults.quality.quality_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="metric-bar">
                    <div 
                      className="metric-fill quality"
                      style={{ width: `${nlpResults.quality.quality_score * 100}%` }}
                    />
                  </div>
                </div>
                
                <div className="metric">
                  <div className="metric-header">
                    <span className="metric-name">Authenticity Score</span>
                    <span className="metric-value">
                      {(nlpResults.quality.authenticity_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="metric-bar">
                    <div 
                      className="metric-fill authenticity"
                      style={{ width: `${nlpResults.quality.authenticity_score * 100}%` }}
                    />
                  </div>
                </div>
              </div>
              
              {nlpResults.quality.quality_factors && (
                <div className="quality-factors">
                  <h5>Quality Factors:</h5>
                  <ul>
                    {Object.entries(nlpResults.quality.quality_factors).map(([factor, value]) => (
                      <li key={factor}>
                        {factor.replace(/_/g, ' ')}: {String(value)}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
          
          <div className="nlp-actions">
            <button onClick={handleNewReview} className="new-review-btn">
              Submit Another Review
            </button>
            <button 
              onClick={() => window.location.href = '/review-history'} 
              className="view-history-btn"
            >
              View Review History
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReviewForm;