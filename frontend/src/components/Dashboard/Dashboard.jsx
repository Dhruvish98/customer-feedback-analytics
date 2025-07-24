// frontend/src/components/Dashboard/Dashboard.jsx - Enhanced version
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom'; 
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { motion } from 'framer-motion';
import api from '../../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate(); 
  const [stats, setStats] = useState(null);
  const [timeRange, setTimeRange] = useState(30);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [insightsScope, setInsightsScope] = useState('all');
  const [selectedScopeValue, setSelectedScopeValue] = useState('');
  const [insights, setInsights] = useState([]);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null); 

  useEffect(() => {
    if (stats?.top_products?.length > 0 && !selectedProduct) {
      setSelectedProduct(stats.top_products[0]);
    }
  }, [stats]);

  useEffect(() => {
    fetchDashboardStats();
  }, [timeRange]);

  // Fetch scope options
  useEffect(() => {
    fetchScopeOptions();
  }, []);

  // Fetch insights when scope changes
  useEffect(() => {
    if (insightsScope === 'all' || selectedScopeValue) {
      fetchInsights();
    }
  }, [insightsScope, selectedScopeValue, timeRange]);

  const fetchScopeOptions = async () => {
    try {
      // Fetch categories
      const catResponse = await api.get('/products/categories');
      setCategories(catResponse.data.categories || []);
      
      // Fetch brands
      const brandResponse = await api.get('/products/brands');
      setBrands(brandResponse.data.brands || []);
      
      // Fetch products
      const prodResponse = await api.get('/products/list?limit=50');
      setProducts(prodResponse.data.products || []);
    } catch (error) {
      console.error('Error fetching scope options:', error);
    }
  };
  
  const fetchInsights = async () => {
    try {
      const params = {
        scope: insightsScope,
        value: selectedScopeValue,
        days: timeRange
      };
      
      const response = await api.get('/insights/generate', { params });
      setInsights(response.data.insights || []);
    } catch (error) {
      console.error('Error fetching insights:', error);
    }
  };
  
  const fetchDashboardStats = async () => {
    try {
      const response = await api.get(`/analytics/dashboard-stats?days=${timeRange}`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading analytics...</p>
      </div>
    );
  }
  
  const sentimentData = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [{
      data: [
        stats?.sentiment_distribution?.positive || 0,
        stats?.sentiment_distribution?.neutral || 0,
        stats?.sentiment_distribution?.negative || 0
      ],
      backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
      borderWidth: 0
    }]
  };
  
  const categoryData = {
    labels: Object.keys(stats?.categories || {}),
    datasets: [{
      label: 'Reviews by Category',
      data: Object.values(stats?.categories || {}),
      backgroundColor: [
        '#667eea', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'
      ]
    }]
  };
  
  return (
    <div className="enhanced-dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Analytics Dashboard</h1>
          <p>Real-time insights and business intelligence</p>
        </div>
        <div className="header-controls">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-select"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last year</option>
          </select>
          <Link to="/monitor" className="btn btn-primary">
            <span>📡</span> Live Monitor
          </Link>
        </div>
      </div>
      
      <div className="dashboard-tabs">
        {['overview', 'products', 'insights', 'alerts'].map(tab => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>
      
      {activeTab === 'overview' && (
        <div className="overview-section">
          <div className="metrics-row">
            <motion.div 
              className="metric-card primary"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className="metric-icon">📊</div>
              <div className="metric-content">
                <h3>Total Reviews</h3>
                <p className="metric-value">{stats?.total_reviews || 0}</p>
                <span className="metric-change positive">+12% from last period</span>
              </div>
            </motion.div>
            
            <motion.div 
              className="metric-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="metric-icon">⭐</div>
              <div className="metric-content">
                <h3>Average Rating</h3>
                <p className="metric-value">{stats?.average_rating?.toFixed(2) || 'N/A'}</p>
                <div className="rating-stars">
                  {[1, 2, 3, 4, 5].map(star => (
                    <span 
                      key={star} 
                      className={star <= Math.round(stats?.average_rating) ? 'filled' : ''}
                    >
                      ★
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
            
            <motion.div 
              className="metric-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="metric-icon">😊</div>
              <div className="metric-content">
                <h3>Sentiment Score</h3>
                <p className="metric-value">
                  {stats?.sentiment_distribution?.positive ? 
                    `${Math.round((stats.sentiment_distribution.positive / stats.total_reviews) * 100)}%` : 
                    'N/A'
                  }
                </p>
                <span className="metric-label">Positive Reviews</span>
              </div>
            </motion.div>
          </div>
          
          <div className="charts-row">
            <div className="chart-card">
              <h3>Sentiment Distribution</h3>
              <div className="chart-container">
                <Doughnut data={sentimentData} options={{
                  cutout: '70%',
                  plugins: {
                    legend: { position: 'bottom' }
                  }
                }} />
              </div>
            </div>
            
            <div className="chart-card">
              <h3>Category Performance</h3>
              <div className="chart-container">
                <Bar data={categoryData} options={{
                  indexAxis: 'y',
                  plugins: {
                    legend: { display: false }
                  }
                }} />
              </div>
              <div className="category-links">
                {Object.keys(stats?.categories || {}).map(category => (
                  <Link 
                    key={category}
                    to={`/analytics/category/${category}`}
                    className="category-link"
                  >
                    {category} →
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {activeTab === 'products' && (
        <div className="products-section">
          <div className="section-header">
            <h2>Top Products</h2>
            <div className="view-options">
              <button className="view-btn active">Top Rated</button>
              <button className="view-btn">Most Reviewed</button>
              <button className="view-btn">Trending</button>
            </div>
          </div>
          
          <div className="products-grid">
            {stats?.top_products?.map((product, idx) => (
              <motion.div
                key={idx}
                className="product-card"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.1 }}
              >
                <div className="product-header">
                  <h4>{product.name}</h4>
                  <span className="product-rating">
                    ⭐ {product.avg_rating.toFixed(1)}
                  </span>
                </div>
                
                <div className="product-metrics">
                  <div className="metric">
                    <span className="label">Reviews</span>
                    <span className="value">{product.review_count}</span>
                  </div>
                  <div className="metric">
                    <span className="label">Positive</span>
                    <span className="value positive">
                      {(product.positive_ratio * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                
                <div className="product-actions">
                  <Link 
                    to={`/analytics/product/${product.id}`}
                    className="action-link"
                  >
                    View Analytics
                  </Link>
                  <Link 
                    to={`/analytics/predictions/${product.id}`}  // Add this
                    className="action-link"
                  >
                    View Predictions
                  </Link>
                  <Link 
                    to={`/analytics/aspects/${product.id}`}
                    className="action-link"
                  >
                    Aspect Analysis
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
      
      {activeTab === 'insights' && (
        <div className="insights-section">
          <div className="insights-header">
            <h2>AI-Powered Insights</h2>
            <div className="insights-controls">
              <select 
                value={insightsScope}
                onChange={(e) => {
                  setInsightsScope(e.target.value);
                  setSelectedScopeValue('');
                }}
                className="scope-select"
              >
                <option value="all">All Products</option>
                <option value="category">By Category</option>
                <option value="brand">By Brand</option>
                <option value="product">By Product</option>
              </select>
              
              {insightsScope === 'category' && (
                <select 
                  value={selectedScopeValue}
                  onChange={(e) => setSelectedScopeValue(e.target.value)}
                  className="value-select"
                >
                  <option value="">Select Category</option>
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              )}
              
              {insightsScope === 'brand' && (
                <select 
                  value={selectedScopeValue}
                  onChange={(e) => setSelectedScopeValue(e.target.value)}
                  className="value-select"
                >
                  <option value="">Select Brand</option>
                  {brands.map(brand => (
                    <option key={brand} value={brand}>{brand}</option>
                  ))}
                </select>
              )}
              
              {insightsScope === 'product' && (
                <select 
                  value={selectedScopeValue}
                  onChange={(e) => setSelectedScopeValue(e.target.value)}
                  className="value-select"
                >
                  <option value="">Select Product</option>
                  {products.map(prod => (
                    <option key={prod.id} value={prod.id}>
                      {prod.name}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>
          
          <div className="insights-grid">
            {insights.length > 0 ? (
              insights.map((insight, idx) => (
                <motion.div 
                  key={idx}
                  className={`insight-card ${insight.type}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <div className="insight-icon">
                    {insight.type === 'opportunity' && '💡'}
                    {insight.type === 'warning' && '⚠️'}
                    {insight.type === 'trend' && '📈'}
                    {insight.type === 'info' && 'ℹ️'}
                  </div>
                  <h3>{insight.title}</h3>
                  <p>{insight.description}</p>
                  {insight.metrics && (
                    <div className="insight-metrics">
                      {Object.entries(insight.metrics).map(([key, value]) => (
                        <span key={key} className="metric">
                          {key}: {typeof value === 'number' ? value.toFixed(1) : value}
                        </span>
                      ))}
                    </div>
                  )}
                  <button 
                    className="insight-action"
                    onClick={() => navigate(insight.action_url)}
                  >
                    {insight.action === 'explore_category' && 'Explore Category'}
                    {insight.action === 'view_products' && 'View Products'}
                    {insight.action === 'view_trends' && 'View Trends'}
                    {insight.action === 'view_competitors' && 'View Analysis'}
                  </button>
                </motion.div>
              ))
            ) : (
              <div className="no-insights">
                <p>No insights available for the selected scope.</p>
                <p>Try selecting a different category, brand, or product.</p>
              </div>
            )}
          </div>
        </div>
      )}
      
      {activeTab === 'alerts' && (
        <div className="alerts-section">
          <h2>Active Alerts & Notifications</h2>
          <div className="alerts-list">
            <div className="alert-item critical">
              <div className="alert-icon">🔴</div>
              <div className="alert-content">
                <h4>Critical: Negative Review Spike</h4>
                <p>Product "TechPro Smartphone 5" received 10 negative reviews in the last hour</p>
                <span className="alert-time">5 minutes ago</span>
              </div>
              <button className="alert-action">Investigate</button>
            </div>
            
            <div className="alert-item warning">
              <div className="alert-icon">🟡</div>
              <div className="alert-content">
                <h4>Warning: Competitor Mentions Increasing</h4>
                <p>25% increase in competitor comparisons this week</p>
                <span className="alert-time">1 hour ago</span>
              </div>
              <button className="alert-action">View Analysis</button>
            </div>
          </div>
        </div>
      )}
      
      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="actions-grid">
          <div 
            className="action-card"
            onClick={() => {
              if (selectedProduct) {
                navigate(`/analytics/predictions/${selectedProduct.id}`);
              } else {
                alert('Please select a product first');
              }
            }}
          >
            <span className="action-icon">🔮</span>
            <span>View Predictions</span>
          </div>
          
          <div 
            className="action-card"
            onClick={() => {
              if (selectedProduct) {
                navigate(`/analytics/competitors/${selectedProduct.id}`);
              } else {
                alert('Please select a product first');
              }
            }}
          >
            <span className="action-icon">🏆</span>
            <span>Competitor Analysis</span>
          </div>
          
          <Link to="/submit-review" className="action-card">
            <span className="action-icon">✍️</span>
            <span>Submit Review</span>
          </Link>
          
          <Link to="/admin" className="action-card">
            <span className="action-icon">⚙️</span>
            <span>System Settings</span>
          </Link>
        </div>
        
        {/* Add product selector for quick actions */}
        {stats?.top_products?.length > 0 && (
          <div className="product-selector">
            <label>Selected Product for Analysis:</label>
            <select 
              value={selectedProduct?.id || ''} 
              onChange={(e) => {
                const product = stats.top_products.find(p => p.id === e.target.value);
                setSelectedProduct(product);
              }}
            >
              {stats.top_products.map(product => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;