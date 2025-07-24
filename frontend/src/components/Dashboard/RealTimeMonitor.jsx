// frontend/src/components/Dashboard/RealTimeMonitor.jsx
import React, { useState, useEffect } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import { motion } from 'framer-motion';
import './RealTimeMonitor.css';

const RealTimeMonitor = () => {
  const [liveData, setLiveData] = useState({
    recentReviews: [],
    sentimentTrend: [],
    alertCount: 0,
    processingQueue: 0
  });
  
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  
  useEffect(() => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:5000/ws/live-updates');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      updateLiveData(data);
    };
    
    return () => ws.close();
  }, []);
  
  const updateLiveData = (newData) => {
    setLiveData(prev => ({
      ...prev,
      recentReviews: [...newData.reviews, ...prev.recentReviews].slice(0, 10),
      sentimentTrend: [...prev.sentimentTrend, newData.sentiment].slice(-20),
      alertCount: newData.alerts,
      processingQueue: newData.queue
    }));
  };
  
  const sentimentChartData = {
    labels: liveData.sentimentTrend.map((_, i) => `${i}m ago`),
    datasets: [
      {
        label: 'Positive',
        data: liveData.sentimentTrend.map(s => s.positive),
        borderColor: '#10b981',
        backgroundColor: '#10b98120',
        tension: 0.4
      },
      {
        label: 'Negative',
        data: liveData.sentimentTrend.map(s => s.negative),
        borderColor: '#ef4444',
        backgroundColor: '#ef444420',
        tension: 0.4
      }
    ]
  };
  
  return (
    <div className="real-time-monitor">
      <div className="monitor-header">
        <h2>Real-Time Analytics Monitor</h2>
        <div className="time-selector">
          {['1h', '6h', '24h', '7d'].map(range => (
            <button
              key={range}
              className={`time-btn ${selectedTimeRange === range ? 'active' : ''}`}
              onClick={() => setSelectedTimeRange(range)}
            >
              {range}
            </button>
          ))}
        </div>
      </div>
      
      <div className="monitor-grid">
        {/* Live Sentiment Trend */}
        <div className="monitor-card sentiment-trend">
          <h3>Sentiment Trend</h3>
          <Line data={sentimentChartData} options={{
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                max: 100
              }
            }
          }} />
        </div>
        
        {/* Alert Feed */}
        <div className="monitor-card alert-feed">
          <h3>
            Active Alerts 
            {liveData.alertCount > 0 && (
              <span className="alert-badge">{liveData.alertCount}</span>
            )}
          </h3>
          <div className="alerts-list">
            {liveData.recentReviews
              .filter(r => r.sentiment === 'negative' && r.confidence > 0.8)
              .map((review, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="alert-item critical"
                >
                  <span className="alert-icon">⚠️</span>
                  <div className="alert-content">
                    <p className="alert-title">Negative Review Alert</p>
                    <p className="alert-desc">{review.product} - {review.aspect}</p>
                  </div>
                  <span className="alert-time">Just now</span>
                </motion.div>
              ))}
          </div>
        </div>
        
        {/* Processing Queue */}
        <div className="monitor-card processing-status">
          <h3>Processing Status</h3>
          <div className="queue-visualization">
            <div className="queue-stat">
              <span className="stat-label">Queue Size</span>
              <span className="stat-value">{liveData.processingQueue}</span>
            </div>
            <div className="processing-animation">
              <div className="pulse-dot"></div>
              <span>Processing...</span>
            </div>
          </div>
        </div>
        
        {/* Recent Reviews Stream */}
        <div className="monitor-card review-stream">
          <h3>Live Review Stream</h3>
          <div className="reviews-feed">
            {liveData.recentReviews.map((review, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`review-item ${review.sentiment}`}
              >
                <div className="review-header">
                  <span className="product-name">{review.product}</span>
                  <span className={`sentiment-badge ${review.sentiment}`}>
                    {review.sentiment}
                  </span>
                </div>
                <p className="review-snippet">{review.text.substring(0, 100)}...</p>
                <div className="review-meta">
                  <span>⭐ {review.rating}</span>
                  <span>{review.timeAgo}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeMonitor;