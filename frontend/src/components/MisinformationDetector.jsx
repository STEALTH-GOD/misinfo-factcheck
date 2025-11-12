import React, { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import StatusBadge from './StatusBadge';
import ConfidenceScore from './ConfidenceScore';
import MetricsPanel from './MetricsPanel';
import SourceAnalysis from './SourceAnalysis';
import './MisinformationDetector.css';

const MisinformationDetector = () => {
  const [claim, setClaim] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!claim.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await api.verifyClaim(claim.trim());
      setResults(response.result);
    } catch (err) {
      setError(err.message);
      // Fallback for demo
      setResults({
        verdict: 'UNCLEAR',
        confidence: 0.0,
        explanation: 'Unable to verify claim due to network error.',
        evidence: []
      });
    } finally {
      setLoading(false);
    }
  };

  const handleNewClaim = () => {
    setClaim('');
    setResults(null);
    setError(null);
  };

  return (
    <div className="misinformation-detector">
      <div className="detector-container">
        <div className="detector-header">
          <h1>AI Fact Checker</h1>
          <p>Verify claims using AI-powered analysis and trusted sources</p>
        </div>

        <form onSubmit={handleSubmit} className="detector-form">
          <div className="input-group">
            <textarea
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              placeholder="Enter a claim to fact-check (e.g., 'The Earth is flat', 'COVID-19 vaccines are effective')"
              disabled={loading}
              rows={results ? 3 : 4}
              className="claim-input"
            />
          </div>

          <div className="button-group">
            <button
              type="submit"
              disabled={!claim.trim() || loading}
              className="verify-button"
            >
              {loading ? (
                <>
                  <Loader2 className="button-icon animate-spin" />
                  Verifying...
                </>
              ) : (
                <>
                  <Search className="button-icon" />
                  {results ? 'Verify New Claim' : 'Verify Claim'}
                </>
              )}
            </button>

            {results && (
              <button
                type="button"
                onClick={handleNewClaim}
                className="new-claim-button"
              >
                New Claim
              </button>
            )}
          </div>
        </form>

        {error && (
          <div className="error-message">
            <p>⚠️ {error}</p>
          </div>
        )}

        {results && (
          <div className="results-section">
            <div className="results-header">
              <h2>Verification Results</h2>
              <div className="analyzed-claim">
                <span>Analyzed Claim:</span>
                <p>"{claim}"</p>
              </div>
            </div>

            <div className="results-summary">
              <StatusBadge verdict={results.verdict} />
              <ConfidenceScore confidence={results.confidence} />
            </div>

            {results.explanation && (
              <div className="explanation-section">
                <h3>Analysis</h3>
                <p>{results.explanation}</p>
              </div>
            )}

            <MetricsPanel
              confidence={results.confidence}
              sourcesCount={results.evidence?.length || 0}
              verdict={results.verdict}
            />

            {results.evidence && results.evidence.length > 0 && (
              <SourceAnalysis sources={results.evidence} claim={claim} />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MisinformationDetector;