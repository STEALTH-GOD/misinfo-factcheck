import React from "react";
import StatusBadge from "./StatusBadge";
import ConfidenceScore from "./ConfidenceScore";
import MetricsPanel from "./MetricsPanel";
import SourceAnalysis from "./SourceAnalysis";

const ResultsDisplay = ({results, claim}) => {
  const {verdict, confidence, explanation, evidence = []} = results;

  return (
    <div className="bg-white rounded-2xl shadow-card p-8 space-y-8">
      {/* Header Section */}
      <div className="border-b border-gray-200 pb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Verification Results
        </h2>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-2">Analyzed Claim:</p>
          <p className="text-gray-900 font-medium">"{claim}"</p>
        </div>
      </div>

      {/* Status and Confidence */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
        <StatusBadge verdict={verdict} />
        <ConfidenceScore confidence={confidence} />
      </div>

      {/* Explanation */}
      {explanation && (
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">Analysis</h3>
          <p className="text-blue-800">{explanation}</p>
        </div>
      )}

      {/* Metrics Panel */}
      <MetricsPanel
        confidence={confidence}
        sourcesCount={evidence.length}
        verdict={verdict}
      />

      {/* Source Analysis */}
      {evidence.length > 0 && (
        <SourceAnalysis sources={evidence} claim={claim} />
      )}
    </div>
  );
};

export default ResultsDisplay;
