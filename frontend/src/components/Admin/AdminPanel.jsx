// src/components/Admin/AdminPanel.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './AdminPanel.css';

const AdminPanel = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role !== 'admin') {
      navigate('/dashboard');
      return;
    }
    fetchAdminStats();
  }, [user, navigate]);

  const fetchAdminStats = async () => {
    try {
      const [health, queue] = await Promise.all([
        api.get('/admin/system-health'),
        api.get('/admin/processing-queue')
      ]);
      
      setStats({
        health: health.data,
        queue: queue.data
      });
    } catch (error) {
      console.error('Error fetching admin stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRetrain = async () => {
    if (window.confirm('Are you sure you want to retrain the models?')) {
      try {
        await api.post('/admin/retrain-models');
        alert('Model retraining initiated successfully!');
      } catch (error) {
        alert('Failed to initiate retraining');
      }
    }
  };

  const handleExport = async () => {
    try {
      const response = await api.post('/admin/export-data', {
        type: 'all',
        format: 'csv'
      });
      
      // Create download link
      const blob = new Blob([JSON.stringify(response.data.data, null, 2)], {
        type: 'application/json'
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics_export_${new Date().toISOString()}.json`;
      a.click();
    } catch (error) {
      alert('Failed to export data');
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading admin panel...</p>
      </div>
    );
  }

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h1>Admin Control Panel</h1>
        <p>Manage system settings and monitor performance</p>
      </div>

      <div className="admin-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'processing' ? 'active' : ''}`}
          onClick={() => setActiveTab('processing')}
        >
          Processing Queue
        </button>
        <button 
          className={`tab ${activeTab === 'models' ? 'active' : ''}`}
          onClick={() => setActiveTab('models')}
        >
          Models
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            <div className="metrics-grid">
              <div className="metric-card">
                <h3>System Status</h3>
                <div className={`status-indicator ${stats?.health?.status}`}>
                  {stats?.health?.status || 'Unknown'}
                </div>
              </div>
              
              <div className="metric-card">
                <h3>Total Reviews</h3>
                <p className="metric-value">{stats?.health?.metrics?.total_reviews || 0}</p>
              </div>
              
              <div className="metric-card">
                <h3>Active Users</h3>
                <p className="metric-value">{stats?.health?.metrics?.total_users || 0}</p>
              </div>
              
              <div className="metric-card">
                <h3>Avg Processing Time</h3>
                <p className="metric-value">
                  {stats?.health?.metrics?.avg_processing_time?.toFixed(2) || 0}s
                </p>
              </div>
            </div>

            <div className="actions-section">
              <h3>Quick Actions</h3>
              <div className="action-buttons">
                <button onClick={handleExport} className="btn btn-secondary">
                  📤 Export Data
                </button>
                <button onClick={handleRetrain} className="btn btn-primary">
                  🔄 Retrain Models
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'processing' && (
          <div className="processing-section">
            <h3>Processing Queue Status</h3>
            <div className="queue-stats">
              <div className="stat">
                <span>Total Processed:</span>
                <strong>{stats?.queue?.pipeline_stats?.total_processed || 0}</strong>
              </div>
              <div className="stat">
                <span>Success Rate:</span>
                <strong>
                  {stats?.queue?.pipeline_stats?.total_processed > 0
                    ? `${((stats.queue.pipeline_stats.successful / stats.queue.pipeline_stats.total_processed) * 100).toFixed(1)}%`
                    : '0%'}
                </strong>
              </div>
            </div>
            
            <h4>Recent Processing Logs</h4>
            <div className="logs-container">
              {stats?.queue?.recent_processing?.map((log, index) => (
                <div key={index} className="log-entry">
                  <span className="log-id">{log.review_id}</span>
                  <span className="log-time">{log.processing_time.toFixed(2)}s</span>
                  <span className="log-date">
                    {new Date(log.created_at).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'models' && (
          <div className="models-section">
            <h3>Model Management</h3>
            <div className="model-cards">
              <div className="model-card">
                <h4>Sentiment Analysis</h4>
                <p>BERT-based Transformer</p>
                <div className="model-stats">
                  <span>Accuracy: 94.5%</span>
                  <span>Last trained: 15 days ago</span>
                </div>
              </div>
              
              <div className="model-card">
                <h4>Topic Extraction</h4>
                <p>BERTopic Model</p>
                <div className="model-stats">
                  <span>Topics: 15</span>
                  <span>Last trained: 15 days ago</span>
                </div>
              </div>
              
              <div className="model-card">
                <h4>Entity Recognition</h4>
                <p>spaCy NER</p>
                <div className="model-stats">
                  <span>F1 Score: 0.89</span>
                  <span>Last trained: 15 days ago</span>
                </div>
              </div>
            </div>
            
            <button onClick={handleRetrain} className="btn btn-primary retrain-btn">
              🔄 Retrain All Models
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPanel;