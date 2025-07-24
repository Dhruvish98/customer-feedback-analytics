// src/components/ReviewForm/ProcessingVisualization.jsx
import React from 'react';
import './ProcessingVisualization.css';

const ProcessingVisualization = ({ status, progress, processingDetails, result }) => {
  const steps = [
    { id: 'preprocessing', label: 'Text Preprocessing', icon: '📝' },
    { id: 'sentiment', label: 'Sentiment Analysis', icon: '🧠' },
    { id: 'entities', label: 'Entity Recognition', icon: '🏷️' },
    { id: 'topics', label: 'Topic Extraction', icon: '📊' },
    { id: 'saving', label: 'Saving Results', icon: '💾' }
  ];

  const getStepStatus = (stepId) => {
    if (status === 'processing') {
      const currentStepIndex = Math.floor((progress / 100) * steps.length);
      const stepIndex = steps.findIndex(s => s.id === stepId);
      
      if (stepIndex < currentStepIndex) return 'completed';
      if (stepIndex === currentStepIndex) return 'active';
      return 'pending';
    }
    
    if (status === 'completed') return 'completed';
    if (status === 'error') return 'error';
    return 'pending';
  };

  return (
    <div className="processing-visualization">
      <div className="processing-header">
        <h3>Review Processing Pipeline</h3>
        {status === 'processing' && (
          <div className="overall-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <span className="progress-text">{progress}%</span>
          </div>
        )}
      </div>

      <div className="processing-steps">
        {steps.map((step, index) => {
          const stepStatus = getStepStatus(step.id);
          return (
            <div key={step.id} className={`process-step ${stepStatus}`}>
              <div className="step-connector">
                {index > 0 && <div className="connector-line"></div>}
              </div>
              <div className="step-content">
                <div className="step-icon">{step.icon}</div>
                <div className="step-info">
                  <h4>{step.label}</h4>
                  {processingDetails?.stages?.[step.id] && (
                    <p className="step-detail">
                      {processingDetails.stages[step.id].status || 
                       processingDetails.stages[step.id].result}
                    </p>
                  )}
                </div>
                <div className="step-status">
                  {stepStatus === 'completed' && '✅'}
                  {stepStatus === 'active' && (
                    <div className="spinner-small"></div>
                  )}
                  {stepStatus === 'error' && '❌'}
                  {stepStatus === 'pending' && '⏳'}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {status === 'completed' && result && (
        <div className="processing-result">
          <div className="result-summary">
            <h4>Processing Complete!</h4>
            <div className="result-metrics">
              <div className="metric">
              // src/components/ReviewForm/ProcessingVisualization.jsx (continued)
                <span className="metric-label">Review ID</span>
                <span className="metric-value">{result.review_id}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Sentiment</span>
                <span className={`metric-value sentiment-${result.sentiment}`}>
                  {result.sentiment}
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Confidence</span>
                <span className="metric-value">
                  {result.confidence ? `${(result.confidence * 100).toFixed(1)}%` : 'N/A'}
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Processing Time</span>
                <span className="metric-value">{result.processing_time}s</span>
              </div>
            </div>
          </div>

          {processingDetails && (
            <div className="detailed-results">
              <h4>Detailed Analysis</h4>
              
              {processingDetails.stages?.sentiment_analysis && (
                <div className="analysis-section">
                  <h5>Sentiment Analysis</h5>
                  <div className="sentiment-scores">
                    <div className="score-bar">
                      <span className="score-label">Positive</span>
                      <div className="score-container">
                        <div 
                          className="score-fill positive"
                          style={{ 
                            width: `${(processingDetails.stages.sentiment_analysis.scores?.positive || 0) * 100}%` 
                          }}
                        ></div>
                      </div>
                      <span className="score-value">
                        {((processingDetails.stages.sentiment_analysis.scores?.positive || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="score-bar">
                      <span className="score-label">Neutral</span>
                      <div className="score-container">
                        <div 
                          className="score-fill neutral"
                          style={{ 
                            width: `${(processingDetails.stages.sentiment_analysis.scores?.neutral || 0) * 100}%` 
                          }}
                        ></div>
                      </div>
                      <span className="score-value">
                        {((processingDetails.stages.sentiment_analysis.scores?.neutral || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="score-bar">
                      <span className="score-label">Negative</span>
                      <div className="score-container">
                        <div 
                          className="score-fill negative"
                          style={{ 
                            width: `${(processingDetails.stages.sentiment_analysis.scores?.negative || 0) * 100}%` 
                          }}
                        ></div>
                      </div>
                      <span className="score-value">
                        {((processingDetails.stages.sentiment_analysis.scores?.negative || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {processingDetails.stages?.entity_recognition?.entities && (
                <div className="analysis-section">
                  <h5>Entities Detected</h5>
                  <div className="entities-list">
                    {processingDetails.stages.entity_recognition.entities.map((entity, index) => (
                      <span key={index} className="entity-tag">
                        {entity.text} ({entity.label})
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {processingDetails.stages?.topic_modeling?.topics && (
                <div className="analysis-section">
                  <h5>Topics Identified</h5>
                  <div className="topics-list">
                    {processingDetails.stages.topic_modeling.topics.map((topic, index) => (
                      <span key={index} className="topic-bubble">
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {status === 'error' && (
        <div className="processing-error">
          <div className="error-icon">⚠️</div>
          <h4>Processing Error</h4>
          <p>An error occurred while processing your review. Please try again.</p>
        </div>
      )}
    </div>
  );
};

export default ProcessingVisualization;