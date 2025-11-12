import React, {useEffect, useState} from "react";
import ResultsDisplay from "./ResultsDisplay";

const NewsDetail = ({newsId, onBack}) => {
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!newsId) return;
    setLoading(true);
    fetch(`http://localhost:8000/api/news/${encodeURIComponent(newsId)}`)
      .then((r) => r.json())
      .then((data) => setItem(data))
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [newsId]);

  if (loading)
    return (
      <div className="bg-white rounded-2xl shadow-card p-6 mt-6">
        Loading...
      </div>
    );
  if (error)
    return (
      <div className="bg-white rounded-2xl shadow-card p-6 mt-6 text-red-600">
        Error: {error}
      </div>
    );
  if (!item) return null;

  const analysis = item.analysis || {
    verdict: "UNCLEAR",
    confidence: 0,
    explanation: "No analysis",
    evidence: [],
  };

  return (
    <div className="bg-white rounded-2xl shadow-card p-6 mt-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">{item.title}</h2>
        <button onClick={onBack} className="px-3 py-1 bg-gray-100 rounded">
          Back
        </button>
      </div>

      <div className="text-sm text-gray-700 whitespace-pre-line">
        {item.full_text}
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Credibility Analysis</h3>
        <ResultsDisplay results={analysis} claim={item.title} />
      </div>
    </div>
  );
};

export default NewsDetail;
