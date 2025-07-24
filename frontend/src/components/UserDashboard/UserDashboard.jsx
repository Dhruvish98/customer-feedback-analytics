// frontend/src/components/UserDashboard/UserDashboard.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import { motion } from 'framer-motion';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import './UserDashboard.css';

const UserDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchUserStats();
    fetchRecentActivity();
    fetchPersonalizedInsights();
  }, []);
  
  const fetchUserStats = async () => {
    try {
      const response = await api.get('/users/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching user stats:', error);
    }
  };
  
  const fetchRecentActivity = async () => {
    try {
      const response = await api.get('/users/activity');
      setRecentActivity(response.data.activities);
    } catch (error) {
      console.error('Error fetching activity:', error);
    }
  };
  
  const fetchPersonalizedInsights = async () => {
    try {
      const response = await api.get('/users/insights');
      setInsights(response.data.insights);
    } catch (error) {
      console.error('Error fetching insights:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <div className="loading">Loading your dashboard...</div>;
  }
  
  const sentimentTrendData = {
    labels: stats?.sentiment_trend?.labels || [],
    datasets: [
      {
        label: 'Your Review Sentiment',
        data: stats?.sentiment_trend?.values || [],
        borderColor: '#667eea',
        backgroundColor: '#667eea20',
        tension: 0.4
      }
    ]
  };
  
  const categoryDistribution = {
    labels: Object.keys(stats?.category_distribution || {}),
    datasets: [{
      data: Object.values(stats?.category_distribution || {}),
      backgroundColor: [
        '#667eea', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'
      ]
    }]
  };
  
  return (
    <div className="user-dashboard">
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>Welcome back, {user.name}!</h1>
          <p>Here's your review activity and personalized insights</p>
        </div>
        <div className="header-actions">
          <Link to="/submit-review" className="btn btn-primary">
            <span>✍️</span> Write a Review
          </Link>
          <Link to="/review-history" className="btn btn-secondary">
            <span>📜</span> View History
          </Link>
        </div>
      </div>
      
      <div className="stats-overview">
        <motion.div 
          className="stat-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="stat-icon">📝</div>
          <div className="stat-content">
            <h3>Total Reviews</h3>
            <p className="stat-value">{stats?.total_reviews || 0}</p>
            <span className="stat-trend">
              +{stats?.reviews_this_month || 0} this month
            </span>
          </div>
        </motion.div>
        
        <motion.div 
          className="stat-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <h3>Average Rating Given</h3>
            <p className="stat-value">{stats?.avg_rating_given?.toFixed(1) || 'N/A'}</p>
            <div className="mini-stars">
              {'★'.repeat(Math.round(stats?.avg_rating_given || 0))}
            </div>
          </div>
        </motion.div>
        
        <motion.div 
          className="stat-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="stat-icon">👍</div>
          <div className="stat-content">
            <h3>Helpful Votes</h3>
            <p className="stat-value">{stats?.total_helpful_votes || 0}</p>
            <span className="stat-label">
              on your reviews
            </span>
          </div>
        </motion.div>
        
        <motion.div 
          className="stat-card premium"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="stat-icon">🏆</div>
          <div className="stat-content">
            <h3>Reviewer Level</h3>
            <p className="stat-value">{stats?.reviewer_level || 'Novice'}</p>
            <div className="level-progress">
              <div 
                className="level-fill"
                style={{ width: `${stats?.level_progress || 0}%` }}
              />
            </div>
          </div>
        </motion.div>
      </div>
      
      <div className="dashboard-content">
        <div className="content-left">
          <div className="chart-section">
            <h2>Your Review Sentiment Trend</h2>
            <div className="chart-container">
              <Line data={sentimentTrendData} options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { display: false }
                }
              }} />
            </div>
          </div>
          
          <div className="activity-section">
            <h2>Recent Activity</h2>
            <div className="activity-list">
              {recentActivity.map((activity, idx) => (
                <motion.div
                  key={idx}
                  className="activity-item"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  // frontend/src/components/UserDashboard/UserDashboard.jsx (continued)
                  <div className="activity-icon">
                    {activity.type === 'review' ? '📝' :
                     activity.type === 'helpful' ? '👍' :
                     activity.type === 'achievement' ? '🏆' : '📊'}
                  </div>
                  <div className="activity-content">
                    <p>{activity.description}</p>
                    <span className="activity-time">{activity.time_ago}</span>
                  </div>
                  {activity.link && (
                    <Link to={activity.link} className="activity-link">
                      View →
                    </Link>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="content-right">
          <div className="categories-section">
            <h2>Your Review Categories</h2>
            <div className="chart-container">
              <Doughnut data={categoryDistribution} options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { position: 'bottom' }
                }
              }} />
            </div>
          </div>
          
          <div className="insights-section">
            <h2>Personalized Insights</h2>
            <div className="insights-list">
              {insights.map((insight, idx) => (
                <div key={idx} className={`insight-card ${insight.type}`}>
                  <div className="insight-icon">{insight.icon}</div>
                  <div className="insight-content">
                    <h4>{insight.title}</h4>
                    <p>{insight.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="achievements-section">
            <h2>Your Achievements</h2>
            <div className="achievements-grid">
              {stats?.achievements?.map((achievement, idx) => (
                <div 
                  key={idx} 
                  className={`achievement-badge ${achievement.unlocked ? 'unlocked' : 'locked'}`}
                  title={achievement.description}
                >
                  <span className="achievement-icon">{achievement.icon}</span>
                  <span className="achievement-name">{achievement.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;