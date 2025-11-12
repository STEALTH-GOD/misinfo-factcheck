import React from "react";

const MetricsPanel = ({confidence, sourcesCount, verdict}) => {
  const credibilityScore = Math.round(confidence * 100) / 100;

  const getEvidenceQuality = (verdict, sourcesCount) => {
    if (sourcesCount === 0) return "N/A";
    if (verdict === "TRUE" || verdict === "FALSE") return "High";
    if (verdict === "MISLEADING") return "Medium";
    return "Low";
  };

  const evidenceQuality = getEvidenceQuality(verdict, sourcesCount);

  const metrics = [
    {
      label: "Credibility Score",
      value: `${credibilityScore}/1.00`,
      color:
        credibilityScore >= 0.8
          ? "text-green-600"
          : credibilityScore >= 0.5
          ? "text-yellow-600"
          : "text-red-600",
    },
    {
      label: "Evidence Quality",
      value: evidenceQuality,
      color:
        evidenceQuality === "High"
          ? "text-green-600"
          : evidenceQuality === "Medium"
          ? "text-yellow-600"
          : "text-gray-600",
    },
    {
      label: "Sources Analyzed",
      value: sourcesCount.toString(),
      color:
        sourcesCount >= 3
          ? "text-green-600"
          : sourcesCount >= 1
          ? "text-yellow-600"
          : "text-red-600",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {metrics.map((metric, index) => (
        <div key={index} className="bg-gray-50 rounded-lg p-4 text-center">
          <div className="text-sm text-gray-600 mb-2">{metric.label}</div>
          <div className={`text-2xl font-bold ${metric.color}`}>
            {metric.value}
          </div>
        </div>
      ))}
    </div>
  );
};

export default MetricsPanel;
