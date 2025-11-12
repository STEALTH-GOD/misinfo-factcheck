const API_BASE_URL = "http://localhost:8000";

export const api = {
  // Fact checking endpoints
  verifyClaim: async (claim, lang = "ne") => {
    const response = await fetch(`${API_BASE_URL}/api/verify_claim`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({claim, lang}),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  // News endpoints
  getLatestNews: async (limit = 10, timestamp = null) => {
    let url = `${API_BASE_URL}/api/latest_news?limit=${limit}`;

    // Add cache-busting parameter if timestamp provided
    if (timestamp) {
      url += `&_t=${timestamp}`;
    }

    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Cache-Control": "no-cache",
        Pragma: "no-cache",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  getNewsDetail: async (newsId) => {
    const response = await fetch(
      `${API_BASE_URL}/api/news/${encodeURIComponent(newsId)}`
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  // Health check
  getHealth: async () => {
    const response = await fetch(`${API_BASE_URL}/`);
    return response.json();
  },
};

export default api;
