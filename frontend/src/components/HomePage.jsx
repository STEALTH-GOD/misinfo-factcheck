import React, { useState, useEffect } from 'react';
import NewsCard from '../components/NewsCard';
import { api } from '../services/api';
import { RefreshCw } from 'lucide-react';
import './HomePage.css';

const HomePage = ({ onOpenArticle }) => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('latest');
  const [refreshing, setRefreshing] = useState(false);

  // Mock data for demonstration
  const mockNews = [
    {
      id: '1',
      title: 'Government Announces Infrastructure Development Plans',
      snippet: 'Major infrastructure projects announced including road connectivity improvements and digital infrastructure expansion across rural areas.',
      source: 'Ekantipur Daily',
      published_at: Date.now() / 1000,
      verification_status: 'VERIFIED_TRUE',
      category: 'Politics',
      tags: ['Politics', 'Technology', 'Infrastructure'],
      trustScore: 95
    },
    {
      id: '2', 
      title: 'Economic Growth Indicators Show Positive Trends',
      snippet: 'Recent economic data indicates steady growth in key sectors with improved employment rates and increased investment.',
      source: 'My Republica',
      published_at: Date.now() / 1000,
      verification_status: 'UNVERIFIED',
      category: 'Economy',
      tags: ['Economy'],
      trustScore: 68
    },
    {
      id: '3',
      title: 'Environmental Conservation Efforts Gain Momentum',
      snippet: 'New environmental protection initiatives launched with focus on sustainable development and climate change adaptation.',
      source: 'Online Khabar',
      published_at: Date.now() / 1000,
      verification_status: 'UNVERIFIED',
      category: 'Environment',
      tags: ['Environment', 'Infrastructure'],
      trustScore: 72
    },
    {
      id: '4',
      title: 'False Claims About COVID-19 Treatments Spread Online',
      snippet: 'Misinformation regarding unproven COVID-19 treatments continues to circulate on social media platforms despite lack of scientific evidence.',
      source: 'Health Fact Check',
      published_at: Date.now() / 1000,
      verification_status: 'DEBUNKED',
      category: 'Health',
      tags: ['Health', 'Misinformation', 'COVID-19'],
      trustScore: 15
    },
    {
      id: '5',
      title: 'Technology Sector Shows Strong Growth in Local Market',
      snippet: 'Local technology companies report significant growth with increased demand for digital services and solutions.',
      source: 'Tech Today',
      published_at: Date.now() / 1000,
      verification_status: 'VERIFIED_TRUE',
      category: 'Technology',
      tags: ['Technology', 'Business'],
      trustScore: 88
    },
    {
      id: '6',
      title: 'Conspiracy Theories About 5G Networks Resurface',
      snippet: 'Debunked conspiracy theories linking 5G networks to health issues continue to spread despite scientific consensus on safety.',
      source: 'Science Verify',
      published_at: Date.now() / 1000,
      verification_status: 'DEBUNKED',
      category: 'Technology',
      tags: ['Technology', 'Health', 'Conspiracy'],
      trustScore: 8
    }
  ];

  useEffect(() => {
    loadNews();
  }, []);

  const loadNews = async () => {
    try {
      setLoading(true);
      // Try to load from API, fallback to mock data
      try {
        // Add timestamp to prevent caching and ensure fresh data
        const timestamp = Date.now();
        const response = await api.getLatestNews(15, timestamp);  // Get more items for variety
        const apiNews = response.news?.map(item => ({
          ...item,
          // Keep the verification_status from backend
          category: item.category || 'General',
          tags: item.tags || ['General']
        })) || [];
        setNews(apiNews.length > 0 ? apiNews : mockNews);
      } catch (apiError) {
        console.error('API Error:', apiError);
        // Use mock data if API fails
        setNews(mockNews);
      }
    } catch (err) {
      setError(err.message);
      setNews(mockNews); // Fallback to mock data
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadNews();
    setRefreshing(false);
  };

  const getTabCounts = () => {
    const latest = news.length;
    const verified = news.filter(n => n.verification_status === 'TRUE').length;
    const debunked = news.filter(n => n.verification_status === 'FALSE').length;
    return { latest, verified, debunked };
  };

  const getFilteredNews = () => {
    switch (activeTab) {
      case 'verified':
        return news.filter(n => n.verification_status === 'TRUE');
      case 'debunked':
        return news.filter(n => n.verification_status === 'FALSE');
      default:
        return news;
    }
  };

  const counts = getTabCounts();
  const filteredNews = getFilteredNews();

  if (loading) {
    return (
      <div className="homepage">
        <div className="homepage-loading">
          <div className="loading-spinner"></div>
          <p>Loading latest news...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="homepage">
      <div className="homepage-header">
        <div className="homepage-hero">
          <div className="hero-icon">🔍</div>
          <h1>AI Fact Checker</h1>
          <p>Stay informed with verified news and fact-checked information</p>
          <button onClick={handleRefresh} className="refresh-button" disabled={refreshing}>
            <RefreshCw className={`refresh-icon ${refreshing ? 'spinning' : ''}`} />
            Refresh News
          </button>
        </div>

        <div className="news-tabs">
          <button 
            className={`tab-button ${activeTab === 'latest' ? 'active' : ''}`}
            onClick={() => setActiveTab('latest')}
          >
            📰 Latest News ({counts.latest})
          </button>
          <button 
            className={`tab-button ${activeTab === 'verified' ? 'active' : ''}`}
            onClick={() => setActiveTab('verified')}
          >
            ✅ Verified True ({counts.verified})
          </button>
          <button 
            className={`tab-button ${activeTab === 'debunked' ? 'active' : ''}`}
            onClick={() => setActiveTab('debunked')}
          >
            ❌ Debunked ({counts.debunked})
          </button>
        </div>
      </div>

      {error && (
        <div className="homepage-error">
          <h3>Unable to load news</h3>
          <p>{error}</p>
          <button onClick={loadNews} className="retry-button">
            Try Again
          </button>
        </div>
      )}

      <div className="news-grid">
        {filteredNews.map((article) => (
          <NewsCard
            key={article.id}
            article={article}
            onClick={onOpenArticle}
          />
        ))}
      </div>

      {filteredNews.length === 0 && !loading && (
        <div className="homepage-empty">
          <h3>No articles found</h3>
          <p>No articles match the selected filter.</p>
        </div>
      )}
    </div>
  );
};

export default HomePage;