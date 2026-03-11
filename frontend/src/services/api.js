/**
 * API service for communicating with the backend
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY;

/**
 * Upload a file and trigger analysis
 * @param {File} file - The CSV or XLSX file to upload
 * @param {string} email - The recipient email address
 * @param {function} onProgress - Progress callback (0-100)
 * @returns {Promise<object>} - The API response
 */
export async function uploadFile(file, email, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    
    // Track upload progress
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable && onProgress) {
        const percent = Math.round((event.loaded / event.total) * 100);
        onProgress(percent);
      }
    };

    xhr.onload = () => {
      try {
        const response = JSON.parse(xhr.responseText);
        
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(response);
        } else {
          reject({
            message: response.detail || response.message || 'Upload failed',
            status: xhr.status,
            detail: response,
          });
        }
      } catch (e) {
        reject({
          message: 'Invalid response from server',
          status: xhr.status,
          detail: xhr.responseText,
        });
      }
    };

    xhr.onerror = () => {
      reject({
        message: 'Network error. Please check your connection.',
        status: 0,
        detail: null,
      });
    };

    xhr.ontimeout = () => {
      reject({
        message: 'Request timed out. Please try again.',
        status: 0,
        detail: null,
      });
    };

    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('recipient_email', email);

    // Configure and send request
    xhr.open('POST', `${BASE_URL}/api/upload`);
    xhr.setRequestHeader('X-API-Key', API_KEY);
    xhr.timeout = 120000; // 2 minute timeout
    xhr.send(formData);
  });
}

/**
 * Check API health status
 * @returns {Promise<object>} - Health check response
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${BASE_URL}/api/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    const data = await response.json();

    return {
      healthy: response.ok,
      provider: data.provider || 'unknown',
      status: data.status,
      version: data.version,
    };
  } catch (error) {
    return {
      healthy: false,
      provider: 'unavailable',
      status: 'error',
      error: error.message,
    };
  }
}

export default {
  uploadFile,
  checkHealth,
};
