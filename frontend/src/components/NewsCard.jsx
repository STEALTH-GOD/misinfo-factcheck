import React from 'react';
import './NewsCard.css';
import { useNavigate } from 'react-router-dom';

const NewsCard = ({ article }) => {
    const navigate = useNavigate();

    const handleCardClick = () => {
        navigate(`/article/${article.id}`, {
            state: { 
                article,
                url: article.url,
                title: article.title 
            }
        });
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'verified_true': return 'bg-green-500';
            case 'verified_false': return 'bg-red-500';
            case 'likely_true': return 'bg-green-400';
            case 'questionable': return 'bg-yellow-500';
            default: return 'bg-gray-500';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'verified_true': return '✅';
            case 'verified_false': return '❌';
            case 'likely_true': return '🟢';
            case 'questionable': return '🟡';
            default: return '⚪';
        }
    };

    const getStatusText = (status) => {
        switch (status) {
            case 'verified_true': return 'VERIFIED TRUE';
            case 'verified_false': return 'DEBUNKED';
            case 'likely_true': return 'LIKELY TRUE';
            case 'questionable': return 'QUESTIONABLE';
            default: return 'UNVERIFIED';
        }
    };

    return (
        <div 
            className="bg-white bg-opacity-95 backdrop-blur-md rounded-2xl p-6 cursor-pointer transition-all duration-300 hover:transform hover:scale-105 hover:shadow-2xl border border-white border-opacity-20"
            onClick={handleCardClick}
        >
            {/* Header */}
            <div className="flex justify-between items-start mb-4">
                <span className={`${getStatusColor(article.verification_status)} text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1`}>
                    <span>{getStatusIcon(article.verification_status)}</span>
                    {getStatusText(article.verification_status)}
                </span>
                <span className="text-gray-500 text-sm font-medium bg-gray-100 px-2 py-1 rounded-lg">
                    {article.source}
                </span>
            </div>

            {/* Content */}
            <div className="mb-4">
                <h3 className="text-lg font-bold text-gray-800 mb-3 line-clamp-2 leading-tight">
                    {article.title}
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed line-clamp-3">
                    {article.snippet}
                </p>
            </div>

            {/* Tags */}
            {article.tags && article.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                    {article.tags.slice(0, 3).map((tag, index) => (
                        <span 
                            key={index} 
                            className="bg-blue-100 text-blue-700 px-2 py-1 rounded-lg text-xs font-medium"
                        >
                            {tag}
                        </span>
                    ))}
                </div>
            )}

            {/* Footer */}
            <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                <div className="flex flex-col">
                    <span className="text-xs text-gray-500 mb-1">Trust Score</span>
                    <div className="flex items-center gap-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div 
                                className={`h-2 rounded-full ${
                                    article.trustworthiness_score > 0.7 ? 'bg-green-500' :
                                    article.trustworthiness_score > 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                                }`}
                                style={{ width: `${(article.trustworthiness_score || 0) * 100}%` }}
                            />
                        </div>
                        <span className="text-sm font-bold text-gray-700">
                            {((article.trustworthiness_score || 0) * 100).toFixed(0)}%
                        </span>
                    </div>
                </div>
                <span className="text-xs text-gray-400">
                    {new Date(article.published_date).toLocaleDateString()}
                </span>
            </div>
        </div>
    );
};

export default NewsCard;