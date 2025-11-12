import React from "react";

const ConfidenceScore = ({confidence}) => {
  const percentage = Math.round(confidence * 100);

  const getColorClass = (score) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    if (score >= 40) return "text-orange-600";
    return "text-red-600";
  };

  return (
    <div className="text-right">
      <div className="text-sm text-gray-600 mb-1">Confidence Score</div>
      <div className={`text-4xl font-bold ${getColorClass(percentage)}`}>
        {percentage}%
      </div>
    </div>
  );
};

export default ConfidenceScore;
