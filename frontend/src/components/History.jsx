import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertCircle, ExternalLink, Clock, Trash2, Search } from 'lucide-react';

const History = () => {
  const [history, setHistory] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');

  useEffect(() => {
    // Load history from localStorage
    const savedHistory = localStorage.getItem('factCheckHistory');
    if (savedHistory) {
      try {
        const parsedHistory = JSON.parse(savedHistory);
        setHistory(parsedHistory);
      } catch (error) {
        console.error('Error parsing history:', error);
        setHistory([]);
      }
    }
  }, []);

  const clearHistory = () => {
    if (window.confirm('Are you sure you want to clear all history?')) {
      localStorage.removeItem('factCheckHistory');
      setHistory([]);
    }
  };

  const removeItem = (index) => {
    const newHistory = history.filter((_, i) => i !== index);
    setHistory(newHistory);
    localStorage.setItem('factCheckHistory', JSON.stringify(newHistory));
  };

  const getVerdictIcon = (verdict) => {
    switch (verdict) {
      case 'likely_true': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'likely_false': return <XCircle className="w-5 h-5 text-red-600" />;
      case 'mixed_evidence': return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case 'insufficient_data': return <AlertCircle className="w-5 h-5 text-gray-600" />;
      default: return <AlertCircle className="w-5 h-5 text-gray-600" />;
    }
  };

  const getVerdictText = (verdict) => {
    switch (verdict) {
      case 'likely_true': return 'Likely True';
      case 'likely_false': return 'Likely False';
      case 'mixed_evidence': return 'Mixed Evidence';
      case 'insufficient_data': return 'Insufficient Data';
      default: return 'Unknown';
    }
  };

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'likely_true': return 'text-green-600';
      case 'likely_false': return 'text-red-600';
      case 'mixed_evidence': return 'text-yellow-600';
      case 'insufficient_data': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  const filteredHistory = history
    .filter(item => 
      item.claim.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.timestamp) - new Date(a.timestamp);
        case 'oldest':
          return new Date(a.timestamp) - new Date(b.timestamp);
        case 'confidence':
          return b.confidence - a.confidence;
        default:
          return 0;
      }
    });

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        {/* Header */}
        <div className="border-b border-gray-200 px-6 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Fact Check History</h1>
            <button
              onClick={clearHistory}
              disabled={history.length === 0}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              Clear History
            </button>
          </div>

          {/* Search and Sort Controls */}
          <div className="flex gap-4 mt-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search claims..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="confidence">Highest Confidence</option>
            </select>
          </div>
        </div>

        {/* History List */}
        <div className="p-6">
          {filteredHistory.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {history.length === 0 ? 'No History Yet' : 'No Results Found'}
              </h3>
              <p className="text-gray-500">
                {history.length === 0 
                  ? 'Start fact-checking claims to see your history here.'
                  : 'Try adjusting your search or filters.'
                }
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredHistory.map((item, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  {/* Claim and Verdict */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1 mr-4">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {item.claim}
                      </h3>
                      <div className="flex items-center gap-3">
                        {getVerdictIcon(item.verdict)}
                        <span className={`font-semibold ${getVerdictColor(item.verdict)}`}>
                          {getVerdictText(item.verdict)}
                        </span>
                        <span className="text-gray-500">•</span>
                        <span className="text-gray-500">
                          {item.confidence}% confidence
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">
                        {new Date(item.timestamp).toLocaleDateString()}
                      </span>
                      <button
                        onClick={() => removeItem(index)}
                        className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                        title="Remove from history"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Stats */}
                  {item.stats && (
                    <div className="flex gap-6 mb-4 text-sm">
                      <div className="flex items-center gap-1">
                        <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                        <span>Refuting: {item.stats.refuting || 0}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                        <span>Supporting: {item.stats.supporting || 0}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
                        <span>Neutral: {item.stats.neutral || 0}</span>
                      </div>
                      <div className="text-gray-500">
                        Sources: {item.stats.total_articles || 0}
                      </div>
                    </div>
                  )}

                  {/* Top Sources */}
                  {item.analysis && item.analysis.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">
                        Top Sources ({item.analysis.length}):
                      </h4>
                      <div className="space-y-2">
                        {item.analysis.slice(0, 3).map((source, sourceIndex) => (
                          <div key={sourceIndex} className="flex items-center justify-between bg-gray-50 p-3 rounded">
                            <div className="flex-1">
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {source.title}
                              </p>
                              <p className="text-xs text-gray-500">
                                Similarity: {(source.similarity * 100).toFixed(1)}% • 
                                Stance: {source.stance} • 
                                Credibility: {(source.source_credibility * 100).toFixed(0)}%
                              </p>
                            </div>
                            <a
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="ml-2 text-blue-600 hover:text-blue-800"
                              title="View source"
                            >
                              <ExternalLink className="w-4 h-4" />
                            </a>
                          </div>
                        ))}
                        {item.analysis.length > 3 && (
                          <p className="text-xs text-gray-500 text-center">
                            +{item.analysis.length - 3} more sources
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default History;