import React from "react";
import SourceCard from "./SourceCard";

const SourceAnalysis = ({sources, claim}) => {
  if (!sources || sources.length === 0) {
    return (
      <div className="border-t border-gray-200 pt-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">
          Source Analysis
        </h3>
        <div className="bg-gray-50 rounded-lg p-6 text-center">
          <p className="text-gray-600">
            No sources were analyzed for this claim.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="border-t border-gray-200 pt-6">
      <h3 className="text-xl font-bold text-gray-900 mb-6">Source Analysis</h3>
      <div className="space-y-4">
        {sources.map((source, index) => (
          <SourceCard key={index} source={source} index={index} claim={claim} />
        ))}
      </div>
    </div>
  );
};

export default SourceAnalysis;
