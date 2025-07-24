// frontend/src/components/Analytics/PredictiveAnalytics.jsx
import React, { useState, useEffect } from 'react';
import { Line, Doughnut } from 'react-chartjs-2';
import { motion } from 'framer-motion';
import GaugeChart from 'react-gauge-chart';
import { useParams } from 'react-router-dom'; // Add this import
import api from '../../services/api';
import './PredictiveAnalytics.css';

const PredictiveAnalytics = () => {  // Remove productId prop
  const { productId } = useParams(); // Get productId from URL
  const [predictions, setPredictions] = useState(null);
  const [selectedScenario, setSelectedScenario] = useState('baseline');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  

  useEffect(() => {
    if (productId && productId !== 'undefined') {
      fetchPredictions();
    } else {
      setError('No product ID provided');
      setLoading(false);
    }
  }, [productId]);
  
  const fetchPredictions = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/analytics/predictions/${productId}`);
      setPredictions(response.data);
    } catch (error) {
      console.error('Error fetching predictions:', error);
      setError('Failed to load predictions. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return (
    <div className="loading-container">
      <div className="spinner"></div>
      <p>Loading predictions...</p>
    </div>
  );
  
  if (error) return (
    <div className="error-container">
      <h3>Error</h3>
      <p>{error}</p>
      <button onClick={() => window.history.back()}>Go Back</button>
    </div>
  );
  
  if (!predictions || !predictions.historical) {
    return (
      <div className="no-data-container">
        <h3>No Prediction Data Available</h3>
        <p>Insufficient data to generate predictions for this product.</p>
        <button onClick={() => window.history.back()}>Go Back</button>
      </div>
    );
  }
  
  const forecastData = {
    labels: [
      ...predictions.historical.labels,
      ...predictions.forecast[selectedScenario].labels
    ],
    datasets: [
      {
        label: 'Historical Rating',
        data: [...predictions.historical.ratings, ...Array(30).fill(null)],
        borderColor: '#667eea',
        backgroundColor: '#667eea20',
        borderWidth: 2
      },
      {
        label: 'Predicted Rating',
        data: [
          ...Array(predictions.historical.ratings.length - 1).fill(null),
          predictions.historical.ratings[predictions.historical.ratings.length - 1],
          ...predictions.forecast[selectedScenario].ratings
        ],
        borderColor: '#10b981',
        backgroundColor: '#10b98120',
        borderDash: [5, 5],
        borderWidth: 2
      },
      {
        label: 'Confidence Interval',
        data: [
          ...Array(predictions.historical.ratings.length - 1).fill(null),
          predictions.historical.ratings[predictions.historical.ratings.length - 1],
          ...predictions.forecast[selectedScenario].upper_bound
        ],
        borderColor: 'transparent',
        backgroundColor: '#10b98110',
        fill: '+1'
      },
      {
        label: 'Lower Bound',
        data: [
          ...Array(predictions.historical.ratings.length - 1).fill(null),
          predictions.historical.ratings[predictions.historical.ratings.length - 1],
          ...predictions.forecast[selectedScenario].lower_bound
        ],
        borderColor: 'transparent',
        backgroundColor: 'transparent',
        fill: false
      }
    ]
  };
  
  return (
    <div className="predictive-analytics">
      <div className="analytics-header">
        <h2>Predictive Analytics & Forecasting</h2>
        <div className="scenario-selector">
          <label>Scenario:</label>
          <select 
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
          >
            <option value="baseline">Baseline</option>
            <option value="optimistic">Optimistic</option>
            <option value="pessimistic">Pessimistic</option>
          </select>
        </div>
      </div>
      
      <div className="predictions-grid">
        {/* Rating Forecast */}
        <div className="prediction-card forecast">
          <h3>30-Day Rating Forecast</h3>
          <Line data={forecastData} options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              annotation: {
                annotations: {
                  currentLine: {
                    type: 'line',
                    xMin: predictions.historical.ratings.length - 1,
                    xMax: predictions.historical.ratings.length - 1,
                    borderColor: '#666',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    label: {
                      content: 'Today',
                      enabled: true,
                      position: 'start'
                    }
                  }
                }
              }
            }
          }} />
          <div className="forecast-summary">
            <div className="summary-item">
              <span>Predicted Rating in 30 days:</span>
              <strong className={predictions.forecast[selectedScenario].trend > 0 ? 'positive' : 'negative'}>
                {predictions.forecast[selectedScenario].final_rating.toFixed(2)} ★
              </strong>
            </div>
            <div className="summary-item">
              <span>Confidence:</span>
              <strong>{(predictions.forecast[selectedScenario].confidence * 100).toFixed(0)}%</strong>
            </div>
          </div>
        </div>
        
        {/* Churn Risk Analysis */}
        <div className="prediction-card churn-risk">
          <h3>Customer Churn Risk</h3>
          <div className="gauge-container">
            <GaugeChart
              id="churn-gauge"
              nrOfLevels={30}
              percent={predictions.churn_risk.score}
              colors={['#10b981', '#f59e0b', '#ef4444']}
              arcPadding={0.02}
              textColor="#333"
            />
          </div>
          <div className="risk-factors">
            <h4>Risk Factors:</h4>
            {predictions.churn_risk.factors.map((factor, idx) => (
              <div key={idx} className="risk-factor">
                <span className="factor-name">{factor.name}</span>
                <div className="factor-impact">
                  <div className="impact-bar">
                    <div 
                      className="impact-fill"
                      style={{ 
                        width: `${factor.impact * 100}%`,
                        backgroundColor: factor.impact > 0.6 ? '#ef4444' : 
                                       factor.impact > 0.3 ? '#f59e0b' : '#10b981'
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Sales Impact Prediction */}
        <div className="prediction-card sales-impact">
          <h3>Predicted Sales Impact</h3>
          <div className="impact-visualization">
            <Doughnut data={{
              labels: ['Current Sales', 'Potential Increase', 'Risk of Loss'],
              datasets: [{
                data: [
                  predictions.sales_impact.current,
                  predictions.sales_impact.potential_increase,
                  predictions.sales_impact.potential_loss
                ],
                backgroundColor: ['#667eea', '#10b981', '#ef4444'],
                borderWidth: 0
              }]
            }} options={{
              cutout: '70%',
              plugins: {
                legend: { position: 'bottom' }
              }
            }} />
            <div className="impact-center">
              <span className="impact-value">
                {predictions.sales_impact.net_impact > 0 ? '+' : ''}
                {predictions.sales_impact.net_impact}%
              </span>
              <span className="impact-label">Net Impact</span>
            </div>
          </div>
        </div>
        
        {/* Actionable Insights */}
        <div className="prediction-card insights">
          <h3>AI-Powered Recommendations</h3>
          <div className="insights-list">
            {predictions.recommendations.map((rec, idx) => (
              <motion.div
                key={idx}
                className={`insight-item ${rec.priority}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <div className="insight-header">
                  <span className="priority-badge">{rec.priority}</span>
                  <span className="potential-impact">+{rec.impact}% improvement</span>
                </div>
                <h4>{rec.title}</h4>
                <p>{rec.description}</p>
                <div className="insight-actions">
                  <button className="action-btn primary">Implement</button>
                  <button className="action-btn secondary">Learn More</button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictiveAnalytics;