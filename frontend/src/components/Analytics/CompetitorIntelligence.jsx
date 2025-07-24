// frontend/src/components/Analytics/CompetitorIntelligence.jsx - Updated complete version
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Line, Scatter, Bar } from 'react-chartjs-2';
import { motion } from 'framer-motion';
import api from '../../services/api';
import './CompetitorIntelligence.css';

const CompetitorIntelligence = () => {
  // Get productId from URL params instead of props
  const { productId } = useParams();
  const navigate = useNavigate();
  
  // States
  const [products, setProducts] = useState([]);
  const [competitorData, setCompetitorData] = useState(null);
  const [selectedCompetitor, setSelectedCompetitor] = useState(null);
  const [viewMode, setViewMode] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  useEffect(() => {
    if (productId) {
      fetchCompetitorData();
    } else {
      fetchProducts();
    }
  }, [productId]);
  
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
  
  const fetchCompetitorData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get product details first to get category
      const productResponse = await api.get(`/products/${productId}`);
      const product = productResponse.data;
      
      // Then get competitor intelligence
      const response = await api.get('/analytics/competitor-intelligence', {
        params: { productId, category: product.category }
      });
      
      setCompetitorData(response.data);
    } catch (error) {
      console.error('Error fetching competitor data:', error);
      if (error.response?.status === 404) {
        setError('Competitor data not available');
      } else {
        setError('Failed to load competitor intelligence');
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Filter products for selector
  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.brand?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });
  
  const categories = ['all', ...new Set(products.map(p => p.category).filter(Boolean))];
  
  // Product Selector View
  if (!productId) {
    return (
      <div className="competitor-intelligence-container">
        <div className="product-selector-section">
          <div className="selector-header">
            <h1>Competitor Intelligence Analysis</h1>
            <p>Select a product to analyze competitive landscape and market position</p>
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
                      onClick={() => navigate(`/analytics/competitors/${product.id}`)}
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
  
  // Loading state
  if (loading) {
    return (
      <div className="competitor-intelligence-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading competitor analysis...</p>
        </div>
      </div>
    );
  }
  
  // Error state
  if (error || !competitorData) {
    return (
      <div className="competitor-intelligence-container">
        <div className="error-container">
          <h2>Unable to Load Analysis</h2>
          <p>{error || 'No competitor data available'}</p>
          <div className="error-actions">
            <button onClick={() => navigate('/analytics/competitors')} className="btn btn-secondary">
              Select Another Product
            </button>
            <button onClick={fetchCompetitorData} className="btn btn-primary">
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  // Safe data extraction with defaults
  const ourProducts = competitorData.our_products || [];
  const competitors = competitorData.competitors || [];
  const advantages = competitorData.competitive_advantages || [];
  const featureComparison = competitorData.feature_comparison || [];
  const mentionContexts = competitorData.mention_contexts || [];
  const mentionTimeline = competitorData.mention_timeline || { labels: [], data: {} };
  
  // Market positioning scatter plot data
  const positioningData = {
    datasets: [
      {
        label: 'Our Products',
        data: ourProducts.map(p => ({
          x: p.price_index || 1,
          y: p.quality_index || 1,
          r: Math.sqrt(p.market_share || 0.1) * 20
        })),
        backgroundColor: 'rgba(102, 126, 234, 0.6)',
        borderColor: '#667eea'
      },
      {
        label: 'Competitors',
        data: competitors.map(c => ({
          x: c.price_index || 1,
          y: c.quality_index || 1,
          r: Math.sqrt(c.market_share || 0.1) * 20
        })),
        backgroundColor: 'rgba(239, 68, 68, 0.6)',
        borderColor: '#ef4444'
      }
    ]
  };
  
  return (
    <div className="competitor-intelligence">
      <div className="intelligence-header">
        <div>
          <h2>Competitor Intelligence</h2>
          <p className="product-name">
            Analyzing: {ourProducts[0]?.name || `Product ${productId}`}
          </p>
        </div>
        <div className="header-controls">
          <button 
            onClick={() => navigate('/analytics/competitors')}
            className="change-product-btn"
          >
            Change Product
          </button>
          <div className="view-controls">
            {['overview', 'comparison', 'mentions'].map(mode => (
              <button
                key={mode}
                className={`view-btn ${viewMode === mode ? 'active' : ''}`}
                onClick={() => setViewMode(mode)}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {viewMode === 'overview' && (
        <div className="overview-section">
          {/* Market Positioning Matrix */}
          <div className="positioning-matrix">
            <h3>Market Positioning</h3>
            <div className="matrix-container">
              <Scatter 
                data={positioningData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    x: {
                      title: { display: true, text: 'Price Index' },
                      min: 0.5,
                      max: 1.5
                    },
                    y: {
                      title: { display: true, text: 'Quality Index' },
                      min: 0.5,
                      max: 1.5
                    }
                  }
                }}
              />
              <div className="quadrant-labels">
                <span className="label premium">Premium Leaders</span>
                <span className="label value">Value Champions</span>
                <span className="label budget">Budget Options</span>
                <span className="label overpriced">Overpriced</span>
              </div>
            </div>
          </div>
          
          {/* Competitive Advantages */}
          <div className="advantages-card">
            <h3>Competitive Advantages</h3>
            <div className="advantages-list">
              {advantages.length > 0 ? advantages.map((adv, idx) => (
                <motion.div
                  key={idx}
                  className="advantage-item"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <div className="advantage-icon">{adv.icon}</div>
                  <div className="advantage-content">
                    <h4>{adv.title}</h4>
                    <p>{adv.description}</p>
                    <div className="advantage-score">
                      <div className="score-bar">
                        <div 
                          className="score-fill"
                          style={{ width: `${(adv.score || 0) * 100}%` }}
                        />
                      </div>
                      <span>{((adv.score || 0) * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </motion.div>
              )) : (
                <p className="no-data">No competitive advantages identified yet</p>
              )}
            </div>
          </div>
        </div>
      )}
      
      {viewMode === 'comparison' && (
        <div className="comparison-section">
          {/* Competitor Selection */}
          <div className="competitor-selector">
            <h3>Select Competitors to Compare</h3>
            <div className="competitor-chips">
              {competitors.length > 0 ? competitors.map(comp => (
                <div
                  key={comp.id}
                  className={`competitor-chip ${
                    selectedCompetitor?.id === comp.id ? 'selected' : ''
                  }`}
                  onClick={() => setSelectedCompetitor(comp)}
                >
                  <span>{comp.name}</span>
                  <span className="market-share">{(comp.market_share || 0).toFixed(1)}%</span>
                </div>
              )) : (
                <p className="no-data">No competitor data available</p>
              )}
            </div>
          </div>
          
          {selectedCompetitor && (
            <div className="comparison-charts">
              {/* Rating Comparison */}
              <div className="comparison-card">
                <h4>Rating Comparison</h4>
                <Bar data={{
                  labels: ['Overall', 'Quality', 'Value', 'Service', 'Delivery'],
                  datasets: [
                    {
                      label: ourProducts[0]?.name || 'Our Product',
                      data: competitorData.our_ratings || [4, 4, 4, 4, 4],
                      backgroundColor: '#667eea'
                    },
                    {
                      label: selectedCompetitor.name,
                      data: selectedCompetitor.ratings?.trend || [
                        selectedCompetitor.average_rating || 3.5,
                        selectedCompetitor.average_rating || 3.5,
                        selectedCompetitor.average_rating || 3.5,
                        selectedCompetitor.average_rating || 3.5,
                        selectedCompetitor.average_rating || 3.5
                      ],
                      backgroundColor: '#ef4444'
                    }
                  ]
                }} options={{
                  indexAxis: 'y',
                  scales: { x: { max: 5 } }
                }} />
              </div>
              
              {/* Competitor Details */}
              <div className="comparison-card">
                <h4>Competitor Profile: {selectedCompetitor.name}</h4>
                <div className="competitor-details">
                  <div className="detail-row">
                    <span className="label">Brand:</span>
                    <span className="value">{selectedCompetitor.brand}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Price:</span>
                    <span className="value">${selectedCompetitor.price?.toFixed(2) || 'N/A'}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Average Rating:</span>
                    <span className="value">{selectedCompetitor.average_rating?.toFixed(1) || 'N/A'} ⭐</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Total Reviews:</span>
                    <span className="value">{selectedCompetitor.total_reviews?.toLocaleString() || 'N/A'}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Market Share:</span>
                    <span className="value">{(selectedCompetitor.market_share * 100).toFixed(1)}%</span>
                  </div>
                </div>
                
                {/* Strengths and Weaknesses */}
                <div className="strengths-weaknesses">
                  <div className="strengths">
                    <h5>Strengths</h5>
                    <ul>
                      {selectedCompetitor.strengths?.map((strength, idx) => (
                        <li key={idx}>{strength}</li>
                      )) || <li>No data available</li>}
                    </ul>
                  </div>
                  <div className="weaknesses">
                    <h5>Weaknesses</h5>
                    <ul>
                      {selectedCompetitor.weaknesses?.map((weakness, idx) => (
                        <li key={idx}>{weakness}</li>
                      )) || <li>No data available</li>}
                    </ul>
                  </div>
                </div>
              </div>
              
              {/* Feature Comparison */}
              <div className="comparison-card">
                <h4>Feature Comparison</h4>
                <div className="feature-comparison">
                  {featureComparison.length > 0 ? featureComparison.map((feature, idx) => (
                    <div key={idx} className="feature-row">
                      <span className="feature-name">{feature.name}</span>
                      <div className="comparison-indicators">
                        <span className={`indicator ${feature.our_status}`}>
                          {feature.our_status === 'better' ? '✓' : 
                          feature.our_status === 'same' ? '=' : '✗'}
                        </span>
                        <span className="vs">vs</span>
                        <span className={`indicator ${feature.their_status}`}>
                          {feature.their_status === 'better' ? '✓' : 
                          feature.their_status === 'same' ? '=' : '✗'}
                        </span>
                      </div>
                    </div>
                  )) : (
                    <p className="no-data">No feature comparison data available</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      
      {viewMode === 'mentions' && (
        <div className="mentions-section">
          <h3>Competitor Mentions in Reviews</h3>
          
          {/* Mention Trends */}
          <div className="mention-trends">
            <Line data={{
              labels: mentionTimeline.labels || [],
              datasets: competitors.slice(0, 5).map((comp, idx) => ({
                label: comp.name,
                data: Object.values(mentionTimeline.data || {}).map(monthData => 
                  monthData[comp.name] || 0
                ),
                borderColor: `hsl(${idx * 60}, 70%, 50%)`,
                backgroundColor: `hsla(${idx * 60}, 70%, 50%, 0.1)`,
                tension: 0.4
              }))
            }} options={{
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  text: 'Competitor Mention Trends'
                }
              }
            }} />
          </div>
          
          {/* Mention Context Analysis */}
          <div className="mention-context">
            <h4>Recent Mention Contexts</h4>
            <div className="context-cards">
              {mentionContexts.length > 0 ? mentionContexts.slice(0, 10).map((context, idx) => (
                <div key={idx} className="context-card">
                  <div className="context-header">
                    <span className="competitor-name">{context.competitor}</span>
                    <span className={`context-sentiment ${context.sentiment ? 'positive' : 'negative'}`}>
                      {context.sentiment ? 'Favorable' : 'Unfavorable'}
                    </span>
                  </div>
                  <p className="context-quote">"{context.context || 'No context available'}"</p>
                  <div className="context-date">{context.date}</div>
                </div>
              )) : (
                <p className="no-data">No competitor mentions found in recent reviews</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CompetitorIntelligence;