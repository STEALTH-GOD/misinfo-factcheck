import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import ArticleDetails from '../components/ArticleDetails';
import { getArticleDetails } from '../services/api';

const ArticleDetailPage = () => {
    const { articleId } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const [articleData, setArticleData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchArticleDetails();
    }, [articleId]);

    const fetchArticleDetails = async () => {
        try {
            setLoading(true);
            setError(null);

            // Get URL and title from location state or prompt user
            const url = location.state?.url || location.state?.article?.url;
            const title = location.state?.title || location.state?.article?.title;

            if (!url) {
                setError('Article URL not provided');
                return;
            }

            const params = new URLSearchParams({
                url: url,
                title: title || 'Article Analysis'
            });

            const data = await getArticleDetails(articleId, url, title);
            setArticleData(data);
        } catch (error) {
            console.error('Failed to fetch article details:', error);
            setError('Failed to load article details');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <div className="text-center text-white">
                    <div className="animate-spin w-16 h-16 border-4 border-white border-t-transparent rounded-full mx-auto mb-6"></div>
                    <h2 className="text-2xl font-bold mb-2">Analyzing Article</h2>
                    <p className="text-lg opacity-90">Performing comprehensive fact-check analysis...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <div className="text-center text-white max-w-lg">
                    <div className="text-6xl mb-6">⚠️</div>
                    <h2 className="text-3xl font-bold mb-4">Analysis Failed</h2>
                    <p className="text-xl mb-8">{error}</p>
                    <div className="space-x-4">
                        <button 
                            onClick={() => navigate('/')}
                            className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
                        >
                            ← Back to Home
                        </button>
                        <button 
                            onClick={fetchArticleDetails}
                            className="bg-transparent border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition"
                        >
                            Try Again
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 py-8">
            <div className="container mx-auto px-4">
                {/* Back Button */}
                <div className="mb-8">
                    <button 
                        onClick={() => navigate('/')}
                        className="bg-white bg-opacity-20 backdrop-blur-md border border-white border-opacity-30 text-white px-6 py-3 rounded-lg font-semibold hover:bg-opacity-30 transition flex items-center gap-2"
                    >
                        ← Back to News Feed
                    </button>
                </div>

                {/* Article Details */}
                <ArticleDetails articleData={articleData} />
            </div>
        </div>
    );
};

export default ArticleDetailPage;