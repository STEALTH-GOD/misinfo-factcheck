import React, {useEffect, useState} from "react";

const NewsCard = ({item, onClick}) => {
  return (
    <div
      onClick={() => onClick(item.id)}
      className="cursor-pointer bg-white rounded-xl p-4 shadow-card hover:shadow-lg transition-shadow"
    >
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-lg font-semibold text-gray-900">{item.title}</h4>
        <div className="text-sm text-gray-500">{item.source}</div>
      </div>
      <p className="text-sm text-gray-700">{item.snippet}</p>
    </div>
  );
};

const NewsHomepage = ({onOpenNews}) => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch("http://localhost:8000/api/latest_news")
      .then((r) => r.json())
      .then((data) => {
        setNews(data.news || []);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="bg-white rounded-2xl shadow-card p-6 mt-6">
      <h3 className="text-xl font-bold mb-4">Latest News</h3>
      {loading && <div className="text-gray-600">Loading news...</div>}
      {error && <div className="text-red-600">Error loading news: {error}</div>}
      {!loading && !error && news.length === 0 && (
        <div className="text-gray-600">No recent news found.</div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        {news.map((n) => (
          <NewsCard key={n.id} item={n} onClick={onOpenNews} />
        ))}
      </div>
    </div>
  );
};

export default NewsHomepage;
