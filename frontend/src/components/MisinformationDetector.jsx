import React, { useState } from 'react';
import { Search, CheckCircle, XCircle, AlertCircle, ExternalLink, Clock, Shield } from 'lucide-react';

const MisinformationDetector = () => {
  const [claim, setClaim] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [apiUrl, setApiUrl] = useState('http://localhost:5000');

  // Function to save results to history
  const saveToHistory = (claim, results) => {
    try {
      const historyItem = {
        claim,
        ...results,
        id: Date.now(), // Simple ID generation
        timestamp: new Date().toISOString()
      };

      // Get existing history
      const existingHistory = JSON.parse(localStorage.getItem('factCheckHistory') || '[]');
      
      // Add new item to the beginning
      const newHistory = [historyItem, ...existingHistory];
      
      // Keep only the last 50 items
      const limitedHistory = newHistory.slice(0, 50);
      
      // Save to localStorage
      localStorage.setItem('factCheckHistory', JSON.stringify(limitedHistory));
    } catch (error) {
      console.error('Error saving to history:', error);
    }
  };

  // Dynamic API call to backend
  const verifyClaimDynamic = async (claim) => {
    try {
      const response = await fetch(`${apiUrl}/api/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ claim }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API call failed:', error);
      throw new Error('Failed to connect to backend API. Make sure the Flask server is running on port 5000.');
    }
  };

  const handleVerify = async () => {
    if (!claim.trim()) {
      setError('Please enter a claim to verify');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const result = await verifyClaimDynamic(claim);
      setResults(result);
      
      // Save to history
      saveToHistory(claim, result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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

  const getVerdictIcon = (verdict) => {
    switch (verdict) {
      case 'likely_true': return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'likely_false': return <XCircle className="w-6 h-6 text-red-600" />;
      case 'mixed_evidence': return <AlertCircle className="w-6 h-6 text-yellow-600" />;
      case 'insufficient_data': return <AlertCircle className="w-6 h-6 text-gray-600" />;
      default: return <AlertCircle className="w-6 h-6 text-gray-600" />;
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

  const getStanceBadge = (stance) => {
    const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";
    switch (stance) {
      case 'supports':
        return (
          <span className={`${baseClasses} bg-green-100 text-green-800`}>
            Supports
          </span>
        );
      case 'refutes':
        return (
          <span className={`${baseClasses} bg-red-100 text-red-800`}>
            Refutes
          </span>
        );
      case 'neutral':
        return (
          <span className={`${baseClasses} bg-gray-100 text-gray-800`}>
            Neutral
          </span>
        );
      default:
        return (
          <span className={`${baseClasses} bg-gray-100 text-gray-800`}>
            {stance}
          </span>
        );
    }
  };

  const getRelevanceBadge = (relevance) => {
    const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";
    switch (relevance) {
      case 'high':
        return (
          <span className={`${baseClasses} bg-blue-100 text-blue-800`}>
            High Relevance
          </span>
        );
      case 'medium':
        return (
          <span className={`${baseClasses} bg-yellow-100 text-yellow-800`}>
            Medium Relevance
          </span>
        );
      case 'low':
        return (
          <span className={`${baseClasses} bg-gray-100 text-gray-800`}>
            Low Relevance
          </span>
        );
      default:
        return (
          <span className={`${baseClasses} bg-gray-100 text-gray-800`}>
            {relevance}
          </span>
        );
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Fact Checker</h1>
          <p className="text-gray-600">Verify claims using AI-powered analysis and trusted sources</p>
        </div>

        {/* Input Section */}
        <div className="mb-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <textarea
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                placeholder="Enter a claim to fact-check (e.g., 'The Earth is flat', 'COVID-19 vaccines are effective')"
                className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows="3"
              />
            </div>
          </div>
          <div className="mt-4 flex gap-4">
            <button
              onClick={handleVerify}
              disabled={loading || !claim.trim()}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Verifying...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Verify Claim
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 text-red-700">
              <XCircle className="w-5 h-5" />
              <span className="font-medium">Error:</span>
            </div>
            <p className="mt-1 text-red-600">{error}</p>
          </div>
        )}

        {/* Results Section */}
        {results && (
          <div className="space-y-6">
            {/* Verdict Summary */}
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getVerdictIcon(results.verdict)}
                  <h2 className={`text-2xl font-bold ${getVerdictColor(results.verdict)}`}>
                    {getVerdictText(results.verdict)}
                  </h2>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500">Confidence</div>
                  <div className="text-2xl font-bold text-gray-900">{results.confidence}%</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <div className="bg-white p-4 rounded-lg">
                  <div className="text-sm text-gray-500">Credibility Score</div>
                  <div className="text-xl font-bold text-gray-900">{results.credibility_score}/100</div>
                </div>
                <div className="bg-white p-4 rounded-lg">
                  <div className="text-sm text-gray-500">Evidence Quality</div>
                  <div className="text-xl font-bold text-gray-900 capitalize">{results.evidence_quality || 'N/A'}</div>
                </div>
                <div className="bg-white p-4 rounded-lg">
                  <div className="text-sm text-gray-500">Sources Analyzed</div>
                  <div className="text-xl font-bold text-gray-900">{results.stats?.total_articles || 0}</div>
                </div>
              </div>

              {/* Stats Breakdown */}
              {results.stats && (
                <div className="mt-4 flex gap-4 text-sm">
                  <span className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    Refuting: {results.stats.refuting || 0}
                  </span>
                  <span className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    Supporting: {results.stats.supporting || 0}
                  </span>
                  <span className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
                    Neutral: {results.stats.neutral || 0}
                  </span>
                  {results.stats.high_credibility_sources !== undefined && (
                    <span className="flex items-center gap-1">
                      <Shield className="w-3 h-3 text-blue-500" />
                      High Credibility: {results.stats.high_credibility_sources}
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Sources Analysis */}
            {results.analysis && results.analysis.length > 0 && (
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">Source Analysis</h3>
                <div className="space-y-4">
                  {results.analysis.map((article, index) => (
                    <div key={index} className="bg-white border border-gray-200 rounded-lg p-6">
                      <div className="flex justify-between items-start mb-3">
                        <h4 className="text-lg font-semibold text-gray-900 flex-1 mr-4">
                          {article.title}
                        </h4>
                        <div className="flex gap-2 flex-shrink-0">
                          {getStanceBadge(article.stance)}
                          {getRelevanceBadge(article.relevance)}
                        </div>
                      </div>

                      <p className="text-gray-600 mb-4">{article.snippet}</p>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span>Similarity: {(article.similarity * 100).toFixed(1)}%</span>
                          <span>Source Credibility: {(article.source_credibility * 100).toFixed(0)}%</span>
                          <span>Stance Confidence: {(article.stance_confidence * 100).toFixed(0)}%</span>
                        </div>
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm"
                        >
                          <ExternalLink className="w-4 h-4" />
                          View Source
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="text-center text-sm text-gray-500">
              <div className="flex items-center justify-center gap-2">
                <Clock className="w-4 h-4" />
                Analyzed on {new Date(results.timestamp).toLocaleString()}
              </div>
              {results.search_engine && (
                <div className="mt-1">
                  Search powered by {results.search_engine}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MisinformationDetector;