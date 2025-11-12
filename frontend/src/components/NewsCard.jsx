import React, { useState } from 'react';
import { Calendar, ExternalLink, X } from 'lucide-react';
import './NewsCard.css';

const NewsCard = ({ article, onClick }) => {
  const [showSourceModal, setShowSourceModal] = useState(false);
  const [selectedSource, setSelectedSource] = useState(null);

  const formatDate = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'TRUE':
        return { text: 'VERIFIED TRUE', class: 'verified-true' };
      case 'FALSE':
        return { text: 'FALSE/MISLEADING', class: 'debunked' };
      case 'UNCLEAR':
        return { text: 'UNVERIFIED', class: 'unverified' };
      default:
        return { text: 'UNVERIFIED', class: 'unverified' };
    }
  };

  const getCardBackgroundClass = (status) => {
    switch (status) {
      case 'TRUE':
        return 'news-card-verified'; // Green background
      case 'FALSE':
        return 'news-card-false'; // Red background
      case 'UNCLEAR':
        return 'news-card-unclear'; // Gray background
      default:
        return 'news-card-unclear';
    }
  };

  const handleSourceClick = (e, source) => {
    e.stopPropagation(); // Prevent card click
    setSelectedSource(source);
    setShowSourceModal(true);
  };

  const handleSourcesClick = (e) => {
    e.stopPropagation(); // Prevent card click
    setSelectedSource('all');
    setShowSourceModal(true);
  };

  const closeModal = () => {
    setShowSourceModal(false);
    setSelectedSource(null);
  };

  const statusBadge = getStatusBadge(article.verification_status);
  const backgroundClass = getCardBackgroundClass(article.verification_status);

  return (
    <>
      <div className={`news-card ${backgroundClass}`} onClick={() => onClick(article.id)}>
        <div className="news-card-header">
          <div className={`verification-badge ${statusBadge.class}`}>
            {statusBadge.text}
          </div>
          <div className="news-card-source-container">
            <div 
              className="news-card-source clickable-source" 
              onClick={(e) => handleSourceClick(e, article.source)}
              title="Click to view source details"
            >
              {article.source}
            </div>
            {article.source_count > 1 && (
              <div 
                className="source-count clickable-source"
                onClick={handleSourcesClick}
                title="Click to view all sources"
              >
                {article.source_count} sources
              </div>
            )}
          </div>
        </div>
        
        <h3 className="news-card-title">{article.title}</h3>
        
        <p className="news-card-snippet">
          {article.snippet}
        </p>

        {article.sources && article.sources.length > 1 && (
          <div className="news-card-sources" onClick={handleSourcesClick}>
            <span className="sources-label">Sources:</span>
            <div className="sources-list">
              {article.sources.slice(0, 3).map((source, index) => (
                <span 
                  key={index} 
                  className="source-item clickable-source"
                  onClick={(e) => handleSourceClick(e, source)}
                  title={`Click to view ${source}`}
                >
                  {source}
                </span>
              ))}
              {article.sources.length > 3 && (
                <span 
                  className="more-sources clickable-source"
                  onClick={handleSourcesClick}
                  title="Click to view all sources"
                >
                  +{article.sources.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}
        
        <div className="news-card-footer">
          <div className="news-card-views">
            {article.views ? `${article.views.toLocaleString()} views` : '0 views'}
          </div>
          <div className="news-card-meta">
            {article.trustScore && (
              <div className="trust-score">
                Trust: {article.trustScore}%
              </div>
            )}
            <div className="news-card-date">
              <Calendar className="news-card-date-icon" />
              {formatDate(article.published_at)}
            </div>
          </div>
        </div>
      </div>

      {/* Source Modal */}
      {showSourceModal && (
        <div className="source-modal-overlay" onClick={closeModal}>
          <div className="source-modal" onClick={(e) => e.stopPropagation()}>
            <div className="source-modal-header">
              <h3>Source Information</h3>
              <button className="source-modal-close" onClick={closeModal}>
                <X size={20} />
              </button>
            </div>
            <div className="source-modal-content">
              {selectedSource === 'all' ? (
                <div>
                  <h4>All Sources for this story:</h4>
                  <ul className="all-sources-list">
                    {article.sources.map((source, index) => (
                      <li key={index} className="source-list-item">
                        <ExternalLink size={16} />
                        <span>{source}</span>
                      </li>
                    ))}
                  </ul>
                  <p className="source-note">
                    This story has been reported by {article.sources.length} different sources.
                  </p>
                </div>
              ) : (
                <div>
                  <h4>Source: {selectedSource}</h4>
                  <div className="source-details">
                    <p><strong>Publication:</strong> {selectedSource}</p>
                    <p><strong>Story:</strong> {article.title}</p>
                    <p><strong>Published:</strong> {formatDate(article.published_at)}</p>
                  </div>
                  <div className="source-actions">
                    <button 
                      className="source-btn"
                      onClick={() => {
                        if (article.source_url) {
                          window.open(article.source_url, '_blank');
                        } else {
                          alert('Source URL not available for this article');
                        }
                      }}
                    >
                      <ExternalLink size={16} />
                      View Original Article
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default NewsCard;