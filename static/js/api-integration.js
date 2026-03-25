// Frontend API Integration for AWS Lambda Backend
class CodePulseAPI {
  constructor() {
    // Get API endpoint from environment or fallback to localhost
    this.apiEndpoint = window.location.hostname === 'localhost' 
      ? 'http://127.0.0.1:8000/api' 
      : 'https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/prod';
    
    this.init();
  }

  init() {
    console.log('🔧 Initializing CodePulse API...');
    console.log('🌐 API Endpoint:', this.apiEndpoint);
  }

  async analyzePortfolio(username) {
    try {
      console.log(`🔍 Analyzing portfolio for: ${username}`);
      
      const response = await fetch(`${this.apiEndpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        'Accept': 'application/json'
        },
        body: JSON.stringify({ username: username.trim() })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      console.log('✅ Analysis complete:', data);
      return data;

    } catch (error) {
      console.error('❌ Analysis failed:', error);
      throw error;
    }
  }

  async getAnalysisHistory(username) {
    try {
      console.log(`📚 Getting history for: ${username}`);
      
      const response = await fetch(`${this.apiEndpoint}?username=${encodeURIComponent(username)}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ History loaded:', data);
      return data.history || [];

    } catch (error) {
      console.error('❌ Failed to get history:', error);
      return [];
    }
  }

  // Fallback to local API when AWS is not available
  async analyzePortfolioLocal(username) {
    try {
      console.log(`🔍 Analyzing portfolio locally for: ${username}`);
      
      const response = await fetch('/api/analyze/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({ username: username.trim() })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Local analysis complete:', data);
      return data;

    } catch (error) {
      console.error('❌ Local analysis failed:', error);
      throw error;
    }
  }

  getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrftoken') {
        return decodeURIComponent(value);
      }
    }
    return null;
  }

  // Check if AWS API is available
  async isAWSAPIAvailable() {
    try {
      const response = await fetch(`${this.apiEndpoint}/health`, {
        method: 'GET',
        timeout: 5000
      });
      return response.ok;
    } catch (error) {
      console.log('⚠️ AWS API not available, using local fallback');
      return false;
    }
  }

  // Smart routing - use AWS when available, fallback to local
  async analyze(username) {
    const awsAvailable = await this.isAWSAPIAvailable();
    
    if (awsAvailable) {
      console.log('🚀 Using AWS Lambda backend');
      return await this.analyzePortfolio(username);
    } else {
      console.log('🔄 Using local Django backend');
      return await this.analyzePortfolioLocal(username);
    }
  }
}

// Initialize global API instance
window.codePulseAPI = new CodePulseAPI();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CodePulseAPI;
}
