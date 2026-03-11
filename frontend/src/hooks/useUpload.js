import { useState, useCallback } from 'react';
import { uploadFile } from '../services/api';

/**
 * Custom hook for handling file upload logic
 */
const useUpload = () => {
  const [status, setStatus] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const upload = useCallback(async (file, email) => {
    setStatus('upload');
    setProgress(0);
    setResult(null);
    setError(null);

    try {
      // Handle progress updates
      const handleProgress = (percent) => {
        setProgress(percent);
        
        // Simulate sub-steps based on progress
        if (percent >= 100) {
          setStatus('parse');
        }
      };

      // Start upload
      const response = await uploadFile(file, email, handleProgress);

      // Simulate processing steps
      setStatus('parse');
      await delay(500);
      
      setStatus('analyze');
      await delay(1000);
      
      setStatus('email');
      await delay(500);
      
      setStatus('complete');
      setResult(response);
      setProgress(100);

      return response;
    } catch (err) {
      setError(err.message || 'An unexpected error occurred');
      setStatus('idle');
      throw err;
    }
  }, []);

  const reset = useCallback(() => {
    setStatus('idle');
    setProgress(0);
    setResult(null);
    setError(null);
  }, []);

  return {
    status,
    progress,
    result,
    error,
    upload,
    reset,
    isLoading: status !== 'idle' && status !== 'complete',
  };
};

// Helper function for delays
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export default useUpload;
