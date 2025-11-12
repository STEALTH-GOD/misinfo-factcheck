import React, { useState, useEffect } from 'react';
import { ArrowLeft } from 'lucide-react';
import { api } from '../services/api';
import StatusBadge from './StatusBadge';
import ConfidenceScore from './ConfidenceScore';
import MetricsPanel from './MetricsPanel';
import SourceAnalysis from './SourceAnalysis';

const ArticleDetails = ({ articleId, onBack }) => {
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!articleId) return;
    loadArticle();
  }, [articleId]);

  const loadArticle = async () => {
    try {
      setLoading(true);
      const response = await api.getNewsDetail(articleId);
      setArticle(response);
    } catch (err) {
      setError(err.message);
      console.error('Error loading article:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="article-details">
        <div className="article-loading">
          <div className="loading-spinner"></div>
          <p>Loading article analysis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="article-details">
        <div className="article-error">
          <button onClick={onBack} className="back-button">
            <ArrowLeft className="back-icon" />
            Back to News
          </button>
          <h3>Unable to load article</h3>
          <p>{error}</p>
          <button onClick={loadArticle} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!article) return null;

  const analysis = article.analysis || {
    verdict: 'UNCLEAR',
    confidence: 0,
    explanation: 'No analysis available',
    evidence: []
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="article-details">
      <div className="article-container">
        <button onClick={onBack} className="back-button">
          <ArrowLeft className="back-icon" />
          Back to News
        </button>

        <div className="article-header">
          <h1>{article.title}</h1>
          <div className="article-meta">
            <span className="article-source">{article.source}</span>
            <span className="article-date">
              {formatDate(article.published_at)}
            </span>
          </div>
        </div>

        <div className="article-content">
          <h3>Full Article</h3>
          <div className="article-text">
            {article.full_text}
          </div>
        </div>

        <div className="credibility-analysis">
          <h2>Credibility Analysis</h2>
          
          <div className="analysis-summary">
            <StatusBadge verdict={analysis.verdict} />
            <ConfidenceScore confidence={analysis.confidence} />
          </div>

          {analysis.explanation && (
            <div className="analysis-explanation">
              <h3>Analysis Details</h3>
              <p>{analysis.explanation}</p>
            </div>
          )}

          <MetricsPanel
            confidence={analysis.confidence}
            sourcesCount={analysis.evidence?.length || 0}
            verdict={analysis.verdict}
          />

          {analysis.evidence && analysis.evidence.length > 0 && (
            <SourceAnalysis sources={analysis.evidence} claim={article.title} />
          )}
        </div>
      </div>
    </div>
  );
};

export default ArticleDetails;