import React from "react";
import {ExternalLink} from "lucide-react";

const SourceCard = ({source, index, claim}) => {
  const {source: sourceUrl, url, snippet, title} = source;
  const displayUrl = url || sourceUrl;
  const displayTitle = title || "Source Article";

  // Extract domain from URL for display and determine credibility
  const getDomainInfo = (url) => {
    try {
      const domain = new URL(url).hostname.replace("www.", "");

      // Determine credibility level based on domain
      const highCredibility = [
        "bbc.com",
        "reuters.com",
        "cnn.com",
        "npr.org",
        "apnews.com",
        "kathmandupost.com",
      ];
      const mediumCredibility = [
        "myrepublica.com",
        "nepalitimes.com",
        "onlinekhabar.com",
        "techcrunch.com",
      ];

      let credibility = "unknown";
      if (highCredibility.some((d) => domain.includes(d))) {
        credibility = "high";
      } else if (mediumCredibility.some((d) => domain.includes(d))) {
        credibility = "medium";
      }

      return {domain, credibility};
    } catch {
      // If URL parsing fails, try to extract domain from string
      if (typeof url === "string") {
        if (url.includes("nepalnews"))
          return {domain: "nepalnews.com", credibility: "medium"};
        if (url.includes("kathmandu"))
          return {domain: "kathmandupost.com", credibility: "high"};
        if (url.includes("republica"))
          return {domain: "myrepublica.com", credibility: "medium"};
        if (url.includes("nepali times"))
          return {domain: "nepalitimes.com", credibility: "medium"};
        if (url.includes("khabar"))
          return {domain: "onlinekhabar.com", credibility: "medium"};
        if (url.includes("bbc"))
          return {domain: "bbc.com", credibility: "high"};
        if (url.includes("reuters"))
          return {domain: "reuters.com", credibility: "high"};
      }
      return {domain: url || "Unknown Source", credibility: "unknown"};
    }
  };

  const getCredibilityBadge = (credibility) => {
    switch (credibility) {
      case "high":
        return {
          label: "High Credibility",
          color: "bg-green-100 text-green-700 border-green-200",
        };
      case "medium":
        return {
          label: "Medium Credibility",
          color: "bg-blue-100 text-blue-700 border-blue-200",
        };
      default:
        return {
          label: "Verify Source",
          color: "bg-gray-100 text-gray-600 border-gray-200",
        };
    }
  };

  // Check if we have a valid URL
  const isValidUrl = (string) => {
    try {
      new URL(string);
      return true;
    } catch (_) {
      return false;
    }
  };

  const hasValidUrl = displayUrl && isValidUrl(displayUrl);

  // Determine sentiment based on snippet content (simplified analysis)
  const getSentiment = (snippet) => {
    if (!snippet) return {label: "Neutral", color: "bg-gray-100 text-gray-700"};

    const snippetLower = snippet.toLowerCase();

    // Simple keyword-based sentiment analysis
    const supportWords = [
      "confirms",
      "supports",
      "proves",
      "evidence shows",
      "research indicates",
    ];
    const contradictWords = [
      "denies",
      "contradicts",
      "disproves",
      "false",
      "incorrect",
      "myth",
    ];

    const hasSupport = supportWords.some((word) => snippetLower.includes(word));
    const hasContradict = contradictWords.some((word) =>
      snippetLower.includes(word)
    );

    if (hasSupport && !hasContradict) {
      return {label: "Supports", color: "bg-green-100 text-green-700"};
    } else if (hasContradict && !hasSupport) {
      return {label: "Contradicts", color: "bg-red-100 text-red-700"};
    }

    return {label: "Neutral", color: "bg-gray-100 text-gray-700"};
  };

  // Determine relevance based on snippet length and content
  const getRelevance = (snippet) => {
    if (!snippet)
      return {label: "Low Relevance", color: "bg-red-50 text-red-600"};

    if (snippet.length > 400) {
      return {label: "High Relevance", color: "bg-green-50 text-green-600"};
    } else if (snippet.length > 200) {
      return {label: "Medium Relevance", color: "bg-yellow-50 text-yellow-600"};
    }

    return {label: "Low Relevance", color: "bg-red-50 text-red-600"};
  };

  const sentiment = getSentiment(snippet);
  const relevance = getRelevance(snippet);
  const domainInfo = getDomainInfo(displayUrl);
  const credibilityBadge = getCredibilityBadge(domainInfo.credibility);

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-sm font-medium text-gray-500">
              Source {index + 1}
            </span>
            <span className="text-gray-300">•</span>
            <span className="text-sm text-gray-600">{domainInfo.domain}</span>
            <span
              className={`text-xs px-2 py-1 border rounded-full ${credibilityBadge.color}`}
            >
              {credibilityBadge.label}
            </span>
          </div>
          {hasValidUrl ? (
            <a
              href={displayUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 font-medium flex items-center space-x-1 group"
            >
              <span className="group-hover:underline">View Source</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          ) : (
            <div className="text-gray-500 font-medium flex items-center space-x-1">
              <span>Source: {displayUrl || "Local Cache"}</span>
              <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                Cached
              </span>
            </div>
          )}
        </div>
      </div>

      {displayTitle && displayTitle !== "Source Article" && (
        <div className="mb-3">
          <h4 className="text-sm font-semibold text-gray-900 line-clamp-2">
            {displayTitle}
          </h4>
        </div>
      )}

      {snippet && (
        <div className="mb-4">
          <p className="text-gray-700 text-sm leading-relaxed">
            {snippet.length > 300 ? `${snippet.substring(0, 300)}...` : snippet}
          </p>
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${sentiment.color}`}
        >
          {sentiment.label}
        </span>
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${relevance.color}`}
        >
          {relevance.label}
        </span>
      </div>
    </div>
  );
};

export default SourceCard;
