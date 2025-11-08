import React, { useState, useEffect } from 'react';
import './HomePage.css';
import NewsCard from './NewsCard';

const HomePage = () => {
    const [newsData, setNewsData] = useState({
        recent: [],
        verified_true: [],
        verified_false: []
    });
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('recent');
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchHomepageNews();
    }, []);

    const fetchHomepageNews = async () => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await fetch('http://localhost:5000/api/homepage-news');
            const result = await response.json();
            
            if (result.status === 'success') {
                setNewsData(result.data);
            } else {
                setError('Failed to load news');
            }
        } catch (error) {
            console.error('Error fetching news:', error);
            setError('Network error occurred');
        } finally {
            setLoading(false);
        }
    };

    const refreshNews = () => {
        fetchHomepageNews();
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <div className="text-center text-white">
                    <div className="animate-spin w-12 h-12 border-4 border-white border-t-transparent rounded-full mx-auto mb-4"></div>
                    <p className="text-xl">Loading latest news...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <div className="text-center text-white">
                    <div className="text-6xl mb-4">⚠️</div>
                    <h2 className="text-2xl mb-4">{error}</h2>
                    <button 
                        onClick={refreshNews}
                        className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600">
            {/* Header */}
            <header className="bg-white bg-opacity-10 backdrop-blur-md py-16">
                <div className="container mx-auto px-4 text-center text-white">
                    <h1 className="text-5xl font-bold mb-4">🔍 AI Fact Checker</h1>
                    <p className="text-xl mb-8 opacity-90">
                        Stay informed with verified news and fact-checked information
                    </p>
                    <button 
                        onClick={refreshNews}
                        className="bg-white bg-opacity-20 border-2 border-white border-opacity-30 text-white px-8 py-3 rounded-full font-semibold hover:bg-opacity-30 transition transform hover:scale-105"
                    >
                        🔄 Refresh News
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-8">
                {/* Navigation Tabs */}
                <div className="flex justify-center mb-8">
                    <div className="bg-white bg-opacity-10 backdrop-blur-md p-2 rounded-2xl flex gap-2">
                        <button 
                            className={`px-6 py-3 rounded-xl font-semibold transition ${
                                activeTab === 'recent' 
                                    ? 'bg-white text-blue-600 shadow-lg' 
                                    : 'text-white hover:bg-white hover:bg-opacity-20'
                            }`}
                            onClick={() => setActiveTab('recent')}
                        >
                            📰 Latest News ({newsData.recent?.length || 0})
                        </button>
                        <button 
                            className={`px-6 py-3 rounded-xl font-semibold transition ${
                                activeTab === 'verified_true' 
                                    ? 'bg-white text-blue-600 shadow-lg' 
                                    : 'text-white hover:bg-white hover:bg-opacity-20'
                            }`}
                            onClick={() => setActiveTab('verified_true')}
                        >
                            ✅ Verified True ({newsData.verified_true?.length || 0})
                        </button>
                        <button 
                            className={`px-6 py-3 rounded-xl font-semibold transition ${
                                activeTab === 'verified_false' 
                                    ? 'bg-white text-blue-600 shadow-lg' 
                                    : 'text-white hover:bg-white hover:bg-opacity-20'
                            }`}
                            onClick={() => setActiveTab('verified_false')}
                        >
                            ❌ Debunked ({newsData.verified_false?.length || 0})
                        </button>
                    </div>
                </div>

                {/* News Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                    {newsData[activeTab]?.map((article, index) => (
                        <NewsCard 
                            key={article.id || index}
                            article={article}
                        />
                    ))}
                </div>

                {/* Empty State */}
                {(!newsData[activeTab] || newsData[activeTab].length === 0) && (
                    <div className="text-center py-16">
                        <div className="text-6xl mb-4">📰</div>
                        <p className="text-white text-xl mb-6">No news available in this category</p>
                        <button 
                            onClick={refreshNews}
                            className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
                        >
                            Try Refreshing
                        </button>
                    </div>
                )}
            </main>
        </div>
    );
};

export default HomePage;