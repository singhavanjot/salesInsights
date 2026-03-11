import React from 'react';

const ResultCard = ({ result, onReset }) => {
  if (!result) return null;

  const isSuccess = result.status === 'success';

  return (
    <div className={`result-card ${isSuccess ? 'success' : 'error'}`}>
      <div className="result-header">
        <span className="result-icon">
          {isSuccess ? '🎉' : '❌'}
        </span>
        <h3 className="result-title">
          {isSuccess ? 'Report Sent Successfully!' : 'Something Went Wrong'}
        </h3>
      </div>

      <div className="result-body">
        <p className="result-message">{result.message}</p>
        
        {isSuccess && result.preview && (
          <div className="result-preview">
            <h4>Report Preview</h4>
            <div className="preview-content">
              {result.preview}...
            </div>
          </div>
        )}

        {result.timestamp && (
          <p className="result-timestamp">
            Generated: {new Date(result.timestamp).toLocaleString()}
          </p>
        )}
      </div>

      <div className="result-actions">
        <button 
          className="btn btn-primary"
          onClick={onReset}
        >
          Upload Another File
        </button>
      </div>
    </div>
  );
};

export default ResultCard;
