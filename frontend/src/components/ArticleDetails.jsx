import React from 'react';

const ArticleDetails = ({ articleData }) => {
    if (!articleData) {
        return (
            <div className="text-center py-8">
                <div className="text-gray-500">Loading article details...</div>
            </div>
        );
    }

    const { analysis, context_articles, source_info } = articleData;

    // Use safe access for all properties in ArticleDetails.jsx
    const overallVerdict = analysis?.overall_verdict || {};
    const contentAnalysis = analysis?.content_analysis || {};
    const sourceAnalysis = analysis?.source_analysis || {};

    // Example of safe property access:
    const verdictStatus = overallVerdict.status || 'unknown';
    const confidence = overallVerdict.confidence || 0;

    const getVerdictColor = (verdict) => {
        switch (verdict) {
            case 'reliable': return 'text-green-600 bg-green-100';
            case 'questionable': return 'text-red-600 bg-red-100';
            case 'mixed': return 'text-yellow-600 bg-yellow-100';
            default: return 'text-gray-600 bg-gray-100';
        }
    };

    const getVerdictIcon = (verdict) => {
        switch (verdict) {
            case 'reliable': return '✅';
            case 'questionable': return '⚠️';
            case 'mixed': return '🔍';
            default: return '❓';
        }
    };

    return (
        <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-xl p-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-800 mb-4">{articleData.title}</h1>
                
                {/* Overall Verdict */}
                <div className={`inline-flex items-center gap-2 px-6 py-3 rounded-full font-bold text-lg ${getVerdictColor(analysis.overall_verdict)}`}>
                    <span>{getVerdictIcon(analysis.overall_verdict)}</span>
                    <span className="uppercase">{analysis.overall_verdict}</span>
                    <span className="text-sm">({(analysis.overall_score * 100).toFixed(0)}%)</span>
                </div>
            </div>

            {/* Analysis Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-xl">
                    <div className="text-blue-600 font-semibold mb-2">Stance Detection</div>
                    <div className="text-2xl font-bold text-blue-800">{analysis.stance}</div>
                    <div className="text-sm text-blue-600">{(analysis.stance_confidence * 100).toFixed(0)}% confidence</div>
                </div>
                
                <div className="bg-gradient-to-r from-green-50 to-green-100 p-6 rounded-xl">
                    <div className="text-green-600 font-semibold mb-2">Source Credibility</div>
                    <div className="text-2xl font-bold text-green-800">{(analysis.source_credibility * 100).toFixed(0)}%</div>
                    <div className="text-sm text-green-600">{source_info.domain}</div>
                </div>
                
                <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-6 rounded-xl">
                    <div className="text-purple-600 font-semibold mb-2">Content Analysis</div>
                    <div className="text-2xl font-bold text-purple-800">{analysis.content_length.toLocaleString()}</div>
                    <div className="text-sm text-purple-600">characters analyzed</div>
                </div>
            </div>

            {/* Content Preview */}
            <div className="mb-8">
                <h2 className="text-xl font-bold text-gray-800 mb-4">📰 Content Preview</h2>
                <div className="bg-gray-50 p-6 rounded-xl">
                    <p className="text-gray-700 leading-relaxed">{articleData.content_preview}</p>
                </div>
            </div>

            {/* Context Articles */}
            {context_articles && context_articles.length > 0 && (
                <div className="mb-8">
                    <h2 className="text-xl font-bold text-gray-800 mb-4">🔗 Related Articles</h2>
                    <div className="space-y-4">
                        {context_articles.map((contextArticle, index) => (
                            <div key={index} className="bg-gray-50 p-4 rounded-xl">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="font-semibold text-gray-800 flex-1">{contextArticle.title}</h3>
                                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-lg text-xs font-medium ml-4">
                                        {(contextArticle.similarity * 100).toFixed(0)}% similar
                                    </span>
                                </div>
                                <p className="text-gray-600 text-sm mb-2">{contextArticle.snippet}</p>
                                <a 
                                    href={contextArticle.url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:text-blue-800 text-sm underline"
                                >
                                    Read full article →
                                </a>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Source Information */}
            <div className="border-t pt-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">📍 Source Information</h2>
                <div className="bg-gray-50 p-6 rounded-xl">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <strong className="text-gray-700">Domain:</strong>
                            <span className="ml-2 text-gray-600">{source_info.domain}</span>
                        </div>
                        <div>
                            <strong className="text-gray-700">Original URL:</strong>
                            <a 
                                href={articleData.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="ml-2 text-blue-600 hover:text-blue-800 underline break-all"
                            >
                                View Original
                            </a>
                        </div>
                    </div>
                    
                    {source_info.credibility_factors && (
                        <div className="mt-4">
                            <strong className="text-gray-700">Credibility Factors:</strong>
                            <ul className="mt-2 space-y-1">
                                {Object.entries(source_info.credibility_factors).map(([factor, value], index) => (
                                    <li key={index} className="text-sm text-gray-600">
                                        • {factor}: {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </div>

            {/* Analysis Timestamp */}
            <div className="text-center mt-8 pt-6 border-t">
                <p className="text-gray-500 text-sm">
                    Analysis completed: {new Date(analysis.analysis_timestamp).toLocaleString()}
                </p>
            </div>
        </div>
    );
};

export default ArticleDetails;