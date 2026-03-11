import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import EmailInput from './components/EmailInput';
import StatusFeed from './components/StatusFeed';
import ResultCard from './components/ResultCard';
import useUpload from './hooks/useUpload';
import { checkHealth } from './services/api';
import './index.css';

function App() {
  const [file, setFile] = useState(null);
  const [email, setEmail] = useState('');
  const [apiHealth, setApiHealth] = useState(null);
  
  const { 
    status, 
    progress, 
    result, 
    error, 
    upload, 
    reset, 
    isLoading 
  } = useUpload();

  // Check API health on mount
  useEffect(() => {
    const checkApi = async () => {
      const health = await checkHealth();
      setApiHealth(health);
    };
    checkApi();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file || !email) {
      return;
    }

    try {
      await upload(file, email);
    } catch (err) {
      console.error('Upload failed:', err);
    }
  };

  const handleReset = () => {
    setFile(null);
    setEmail('');
    reset();
  };

  const isFormValid = file && email && /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email);

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1 className="logo">
            <span className="logo-icon">🐰</span>
            <span className="logo-text">Sales Insights</span>
          </h1>
          <p className="tagline">Sales Insight Automator</p>
          {apiHealth && (
            <span className={`health-badge ${apiHealth.healthy ? 'healthy' : 'unhealthy'}`}>
              {apiHealth.healthy ? '● Online' : '○ Offline'}
            </span>
          )}
        </div>
      </header>

      <main className="main">
        <div className="container">
          <div className="hero">
            <h2>Transform Your Sales Data Into Actionable Insights</h2>
            <p>
              Upload your CSV or Excel file, and our AI will generate a 
              professional sales report delivered straight to your inbox.
            </p>
          </div>

          {result ? (
            <ResultCard result={result} onReset={handleReset} />
          ) : (
            <form className="upload-form" onSubmit={handleSubmit}>
              <div className="form-section">
                <FileUpload 
                  onFileSelect={setFile} 
                  disabled={isLoading}
                />
              </div>

              <div className="form-section">
                <EmailInput 
                  value={email}
                  onChange={setEmail}
                  disabled={isLoading}
                />
              </div>

              <StatusFeed 
                status={status}
                progress={progress}
                error={error}
              />

              <div className="form-actions">
                <button
                  type="submit"
                  className="btn btn-primary btn-large"
                  disabled={!isFormValid || isLoading}
                >
                  {isLoading ? (
                    <>
                      <span className="btn-spinner" />
                      Processing...
                    </>
                  ) : (
                    <>
                      🚀 Generate Report
                    </>
                  )}
                </button>
              </div>
            </form>
          )}

          <div className="features">
            <div className="feature">
              <span className="feature-icon">📊</span>
              <h3>Smart Analysis</h3>
              <p>AI-powered insights from your sales data</p>
            </div>
            <div className="feature">
              <span className="feature-icon">⚡</span>
              <h3>Fast Processing</h3>
              <p>Results delivered in seconds</p>
            </div>
            <div className="feature">
              <span className="feature-icon">🔒</span>
              <h3>Secure</h3>
              <p>Your data is encrypted and protected</p>
            </div>
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>© 2026 Rabbitt AI • Sales Insight Automator</p>
        <p className="footer-links">
          <a href="/docs" target="_blank" rel="noopener noreferrer">API Docs</a>
          <span>•</span>
          <a href="https://github.com/rabbittai" target="_blank" rel="noopener noreferrer">GitHub</a>
        </p>
      </footer>
    </div>
  );
}

export default App;
