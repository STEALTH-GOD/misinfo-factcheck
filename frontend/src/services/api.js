// API Base URL configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

// Get trending news by category
export const getTrendingNews = async (category = 'recent', limit = 6) => {
  try {
    console.log(`🔍 Fetching trending news for category: ${category}`);
    
    const response = await fetch(`${API_BASE_URL}/api/news/trending?category=${category}&limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.status === 'success') {
      return result.data;
    } else {
      throw new Error(result.message || 'Failed to fetch trending news');
    }
  } catch (error) {
    console.error('❌ Trending news API error:', error);
    throw error;
  }
};

// Get all news categories for homepage
export const getAllNewsCategories = async (language = 'en') => {
  try {
    console.log(`🔍 Fetching all news categories (language: ${language})`);
    
    const response = await fetch(`${API_BASE_URL}/api/news/categories?language=${language}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.status === 'success') {
      return result.data;
    } else {
      throw new Error(result.message || 'Failed to fetch news categories');
    }
  } catch (error) {
    console.error('❌ News categories API error:', error);
    throw error;
  }
};

// Get article details
export const getArticleDetails = async (articleId, url, title) => {
  try {
    console.log(`🔍 Fetching article details for: ${url}`);

    const params = new URLSearchParams({
      url: url,
      title: title || "",
    });

    const response = await fetch(
      `${API_BASE_URL}/api/article/${articleId}?${params}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    // DEBUG: Log the response structure
    console.log("🔍 API Response:", result);

    if (result.status === "success" && result.data) {
      console.log("🔍 Article data keys:", Object.keys(result.data));
      console.log("🔍 analysis structure:", result.data.analysis);
      return result.data;
    } else {
      throw new Error(result.message || "Failed to fetch article details");
    }
  } catch (error) {
    console.error("❌ Article details API error:", error);
    throw error;
  }
};

// Analyze content for misinformation
export const analyzeContent = async (content) => {
  try {
    console.log('🔍 Analyzing content for misinformation');
    
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.status === 'success') {
      return result.data;
    } else {
      throw new Error(result.message || 'Failed to analyze content');
    }
  } catch (error) {
    console.error('❌ Content analysis API error:', error);
    throw error;
  }
};

// Check URL for misinformation
export const checkUrl = async (url) => {
  try {
    console.log(`🔍 Checking URL: ${url}`);
    
    const response = await fetch(`${API_BASE_URL}/api/check-url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.status === 'success') {
      return result.data;
    } else {
      throw new Error(result.message || 'Failed to check URL');
    }
  } catch (error) {
    console.error('❌ URL check API error:', error);
    throw error;
  }
};

// Get news by specific category
export const getNewsByCategory = async (category, limit = 10) => {
  try {
    console.log(`🔍 Fetching news for category: ${category}`);
    
    const response = await fetch(`${API_BASE_URL}/api/news/${category}?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.status === 'success') {
      return result.data;
    } else {
      throw new Error(result.message || 'Failed to fetch category news');
    }
  } catch (error) {
    console.error(`❌ Category ${category} news API error:`, error);
    throw error;
  }
};

// Health check API
export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('❌ Health check failed:', error);
    throw error;
  }
};

// Export API_BASE_URL for other components that might need it
export { API_BASE_URL };