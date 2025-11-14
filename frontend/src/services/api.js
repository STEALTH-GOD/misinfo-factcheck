const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Individual API functions
export const verifyClaimAPI = async (claim, lang = "ne") => {
  const response = await fetch(`${API_BASE_URL}/api/verify_claim`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({claim, lang}),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export const getLatestNews = async (limit = 15) => {
  const response = await fetch(
    `${API_BASE_URL}/api/latest_news?limit=${limit}&_t=${Date.now()}`
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export const getNewsDetail = async (newsId) => {
  const response = await fetch(`${API_BASE_URL}/api/news/${newsId}`);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

// Export api object with all methods (for backward compatibility)
export const api = {
  verifyClaim: verifyClaimAPI, // Add this alias
  verifyClaimAPI: verifyClaimAPI,
  getLatestNews: getLatestNews,
  getNewsDetail: getNewsDetail,
};

// Default export
export default api;
