const API_BASE_URL = 'http://localhost:5000/api';

export const api = {
    // Get homepage news
    getHomepageNews: async (language = 'en', category = 'all') => {
        try {
            const params = new URLSearchParams({ language, category });
            const response = await fetch(`${API_BASE_URL}/homepage-news?${params}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching homepage news:', error);
            throw error;
        }
    },

    // Get article details
    getArticleDetails: async (articleId, url, title) => {
        try {
            const params = new URLSearchParams({ url, title });
            const response = await fetch(`${API_BASE_URL}/article/${articleId}?${params}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching article details:', error);
            throw error;
        }
    },

    // Verify a claim (existing functionality)
    verifyClaim: async (claim) => {
        try {
            const response = await fetch(`${API_BASE_URL}/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ claim }),
            });
            return await response.json();
        } catch (error) {
            console.error('Error verifying claim:', error);
            throw error;
        }
    },

    // Health check
    healthCheck: async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            return await response.json();
        } catch (error) {
            console.error('Error checking health:', error);
            throw error;
        }
    }
};

export default api;