// frontend/src/components/Analytics/AspectAnalysis.jsx - Complete version with product selector
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Radar, Bar } from 'react-chartjs-2';
import WordCloud from 'react-d3-cloud';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../../services/api';
import './AspectAnalysis.css';

const AspectAnalysis = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  
  // States
  const [products, setProducts] = useState([]);
  const [aspectData, setAspectData] = useState(null);
  const [selectedAspect, setSelectedAspect] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  useEffect(() => {
    if (productId) {
      fetchAspectData();
    } else {
      fetchProducts();
    }
  }, [productId, timeRange]);
  
  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/products/list');
      setProducts(response.data.products || []);
    } catch (error) {
      console.error('Error fetching products:', error);
      setError('Failed to load products');
    } finally {
      setLoading(false);
    }
  };
  
  const fetchAspectData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/analytics/aspects/${productId}?days=${timeRange}`);
      setAspectData(response.data);
    } catch (error) {
      console.error('Error fetching aspect data:', error);
      if (error.response?.status === 404) {
        setError('Product not found');
      } else {
        setError('Failed to load aspect analysis');
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Filter products based on search and category
  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.brand?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });
  
  // Get unique categories
  const categories = ['all', ...new Set(products.map(p => p.category).filter(Boolean))];
  
  // Product Selector View
  if (!productId) {
    return (
      <div className="aspect-analysis-container">
        <div className="product-selector-section">
          <div className="selector-header">
            <h1>Aspect-Based Sentiment Analysis</h1>
            <p>Select a product to analyze customer feedback by different aspects</p>
          </div>
          
          {loading ? (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Loading products...</p>
            </div>
          ) : error ? (
            <div className="error-container">
              <p>{error}</p>
              <button onClick={fetchProducts} className="retry-btn">
                Try Again
              </button>
            </div>
          ) : (
            <>
              <div className="selector-controls">
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="category-select"
                >
                  {categories.map(cat => (
                    <option key={cat} value={cat}>
                      {cat === 'all' ? 'All Categories' : cat}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="products-selector-grid">
                {filteredProducts.length === 0 ? (
                  <div className="no-products">
                    <p>No products found matching your criteria</p>
                  </div>
                ) : (
                  filteredProducts.map((product, idx) => (
                    <motion.div
                      key={product.id}
                      className="product-selector-card"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      onClick={() => navigate(`/analytics/aspects/${product.id}`)}
                      whileHover={{ scale: 1.03 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="product-info">
                        <h3>{product.name}</h3>
                        <p className="product-brand">{product.brand}</p>
                        <p className="product-category">{product.category}</p>
                      </div>
                      <div className="product-stats">
                        <div className="stat">
                          <span className="stat-value">{product.review_count || 0}</span>
                          <span className="stat-label">Reviews</span>
                        </div>
                        <div className="stat">
                          <span className="stat-value">
                            {product.average_rating ? product.average_rating.toFixed(1) : 'N/A'} ⭐
                          </span>
                          <span className="stat-label">Rating</span>
                        </div>
                      </div>
                      <div className="select-indicator">
                        <span>Analyze →</span>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>
            </>
          )}
        </div>
      </div>
    );
  }
  
  // Loading state for aspect analysis
  if (loading) {
    return (
      <div className="aspect-analysis-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading aspect analysis...</p>
        </div>
      </div>
    );
  }
  
  // Error state
  if (error) {
    return (
      <div className="aspect-analysis-container">
        <div className="error-container">
          <h2>Error Loading Analysis</h2>
          <p>{error}</p>
          <div className="error-actions">
            <button onClick={() => navigate('/analytics/aspects')} className="btn btn-secondary">
              Select Another Product
            </button>
            <button onClick={fetchAspectData} className="btn btn-primary">
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  // No data state
  if (!aspectData || !aspectData.aspects || Object.keys(aspectData.aspects).length === 0) {
    return (
      <div className="aspect-analysis-container">
        <div className="no-data-container">
          <h2>No Aspect Data Available</h2>
          <p>Not enough reviews to generate aspect analysis for this product.</p>
          <button 
            onClick={() => navigate('/analytics/aspects')} 
            className="btn btn-primary"
          >
            Select Another Product
          </button>
        </div>
      </div>
    );
  }
  
  // Prepare radar chart data
  const radarData = {
    labels: Object.keys(aspectData.aspects),
    datasets: [
      {
        label: 'Positive Sentiment',
        data: Object.values(aspectData.aspects).map(a => a.positive_ratio * 100),
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        borderColor: '#10b981',
        pointBackgroundColor: '#10b981',
      },
      {
        label: 'Mention Frequency',
        data: Object.values(aspectData.aspects).map(a => a.mention_frequency * 100),
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: '#3b82f6',
        pointBackgroundColor: '#3b82f6',
      }
    ]
  };
  
  // Word cloud data for selected aspect
  const getWordCloudData = (aspect) => {
    if (!aspect || !aspectData.aspects[aspect]) return [];
    
    return aspectData.aspects[aspect].keywords.map(kw => ({
      text: kw.word,
      value: kw.frequency * 100
    }));
  };
  
  // Main aspect analysis view
  return (
    <div className="aspect-analysis">
      <div className="analysis-header">
        <div>
          <h2>Aspect-Based Sentiment Analysis</h2>
          <p className="product-name">
            Analyzing: {aspectData.product_name || `Product ${productId}`}
          </p>
        </div>
        <div className="header-controls">
          <button 
            onClick={() => navigate('/analytics/aspects')}
            className="change-product-btn"
          >
            Change Product
          </button>
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-select"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
      </div>
      
      <div className="analysis-summary">
        <div className="summary-stat">
          <span className="stat-label">Total Reviews Analyzed</span>
          <span className="stat-value">{aspectData.total_reviews}</span>
        </div>
        <div className="summary-stat">
          <span className="stat-label">Analysis Period</span>
          <span className="stat-value">{aspectData.analysis_period} days</span>
        </div>
        <div className="summary-stat">
          <span className="stat-label">Aspects Identified</span>
          <span className="stat-value">{Object.keys(aspectData.aspects).length}</span>
        </div>
      </div>
      
      <div className="analysis-grid">
        {/* Radar Chart */}
        <div className="chart-card">
          <h3>Aspect Overview</h3>
          <div className="radar-container">
            <Radar data={radarData} options={{
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                r: {
                  beginAtZero: true,
                  max: 100
                }
              }
            }} />
          </div>
        </div>
        
        {/* Aspect Cards */}
        <div className="aspects-grid">
          {Object.entries(aspectData.aspects).map(([aspect, data]) => (
            <motion.div
              key={aspect}
              className={`aspect-card ${selectedAspect === aspect ? 'selected' : ''}`}
              onClick={() => setSelectedAspect(aspect)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="aspect-header">
                <h4>{aspect}</h4>
                <span className={`sentiment-indicator ${data.primary_sentiment}`}>
                  {data.primary_sentiment}
                </span>
              </div>
              
              <div className="aspect-metrics">
                <div className="metric">
                  <span className="label">Mentions</span>
                  <span className="value">{data.mention_count}</span>
                </div>
                <div className="metric">
                  <span className="label">Positive</span>
                  <span className="value positive">
                    {(data.positive_ratio * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="metric">
                  <span className="label">Impact</span>
                  <span className="value">
                    {data.impact_score.toFixed(2)}
                  </span>
                </div>
              </div>
              
              <div className="aspect-issues">
                {data.top_issues && data.top_issues.slice(0, 2).map((issue, idx) => (
                  <span key={idx} className="issue-tag">
                    {issue}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
        
        {/* Detailed View for Selected Aspect */}
        <AnimatePresence>
          {selectedAspect && aspectData.aspects[selectedAspect] && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="aspect-detail"
            >
              <h3>{selectedAspect} Deep Dive</h3>
              
              <div className="detail-grid">
                {/* Sentiment Distribution */}
                <div className="detail-card">
                  <h4>Sentiment Distribution</h4>
                  <Bar data={{
                    labels: ['Positive', 'Neutral', 'Negative'],
                    datasets: [{
                      data: [
                        aspectData.aspects[selectedAspect].sentiment_distribution.positive,
                        aspectData.aspects[selectedAspect].sentiment_distribution.neutral,
                        aspectData.aspects[selectedAspect].sentiment_distribution.negative
                      ],
                      backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
                    }]
                  }} options={{
                    indexAxis: 'y',
                    plugins: { legend: { display: false } }
                  }} />
                </div>
                
                {/* Word Cloud */}
                <div className="detail-card">
                  <h4>Associated Keywords</h4>
                  <div className="wordcloud-container">
                    {getWordCloudData(selectedAspect).length > 0 ? (
                      <WordCloud
                        data={getWordCloudData(selectedAspect)}
                        width={400}
                        height={300}
                        font="Arial"
                        fontStyle="normal"
                        fontWeight="bold"
                        fontSize={(word) => Math.log2(word.value) * 10}
                        rotate={() => 0}
                        padding={5}
                      />
                    ) : (
                      <p className="no-keywords">No keywords available</p>
                    )}
                  </div>
                </div>
                
                {/* Example Reviews */}
                <div className="detail-card example-reviews">
                  <h4>Example Reviews</h4>
                  <div className="reviews-list">
                    {aspectData.aspects[selectedAspect].example_reviews.map((review, idx) => (
                      <div key={idx} className={`example-review ${review.sentiment}`}>
                        <p>"{review.text}"</p>
                        <div className="review-info">
                          <span>⭐ {review.rating}</span>
                          <span>{review.date}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Recommendations */}
                <div className="detail-card recommendations">
                  <h4>AI Recommendations</h4>
                  <ul className="recommendations-list">
                    {aspectData.aspects[selectedAspect].recommendations.map((rec, idx) => (
                      <li key={idx} className={`recommendation ${rec.priority}`}>
                        <span className="rec-icon">
                          {rec.priority === 'high' ? '🔴' : rec.priority === 'medium' ? '🟡' : '🟢'}
                        </span>
                        <div className="rec-content">
                          <p className="rec-title">{rec.title}</p>
                          <p className="rec-description">{rec.description}</p>
                          <div className="rec-impact">
                            <span>Potential Impact: {rec.impact}</span>
                            <span>Effort: {rec.effort}</span>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default AspectAnalysis;