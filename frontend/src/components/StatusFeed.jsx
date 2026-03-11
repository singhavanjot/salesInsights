import React from 'react';

const StatusFeed = ({ status, progress, error }) => {
  const steps = [
    { id: 'upload', label: 'Uploading file', icon: '📤' },
    { id: 'parse', label: 'Parsing data', icon: '📊' },
    { id: 'analyze', label: 'AI analysis', icon: '🤖' },
    { id: 'email', label: 'Sending email', icon: '📧' },
    { id: 'complete', label: 'Complete', icon: '✅' },
  ];

  const getStepStatus = (stepId) => {
    const stepOrder = ['idle', 'upload', 'parse', 'analyze', 'email', 'complete'];
    const currentIndex = stepOrder.indexOf(status);
    const stepIndex = stepOrder.indexOf(stepId);

    if (error && stepId === status) return 'error';
    if (status === 'complete' && stepId === 'complete') return 'complete';
    if (stepIndex < currentIndex) return 'done';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  if (status === 'idle') {
    return null;
  }

  return (
    <div className="status-feed">
      <h3 className="status-title">Processing Status</h3>
      
      {progress > 0 && progress < 100 && (
        <div className="progress-bar-container">
          <div 
            className="progress-bar" 
            style={{ width: `${progress}%` }}
          />
          <span className="progress-text">{progress}%</span>
        </div>
      )}

      <ul className="status-steps">
        {steps.map((step) => {
          const stepStatus = getStepStatus(step.id);
          return (
            <li 
              key={step.id} 
              className={`status-step ${stepStatus}`}
            >
              <span className="step-icon">
                {stepStatus === 'done' ? '✓' : 
                 stepStatus === 'error' ? '✗' : 
                 stepStatus === 'active' ? '⏳' : 
                 step.icon}
              </span>
              <span className="step-label">{step.label}</span>
              {stepStatus === 'active' && (
                <span className="step-spinner" />
              )}
            </li>
          );
        })}
      </ul>

      {error && (
        <div className="status-error">
          <span className="error-icon">⚠️</span>
          <span className="error-message">{error}</span>
        </div>
      )}
    </div>
  );
};

export default StatusFeed;
