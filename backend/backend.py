from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from datetime import datetime
from bs4 import BeautifulSoup
import os
import re
import numpy as np

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize models (loads once at startup)
print("Loading AI models...")
similarity_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
print("Models loaded successfully!")

# API Keys
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
GOOGLE_CX = os.getenv('GOOGLE_CX', '')

# Trusted news sources for credibility scoring
TRUSTED_SOURCES = [
    'reuters.com', 'apnews.com', 'bbc.com', 'cnn.com', 'nytimes.com',
    'washingtonpost.com', 'guardian.com', 'npr.org', 'politifact.com',
    'snopes.com', 'factcheck.org', 'economist.com', 'wsj.com', 'abc.go.com',
    'cbsnews.com', 'nbcnews.com', 'usatoday.com', 'time.com', 'newsweek.com'
]

UNRELIABLE_SOURCES = [
    'infowars.com', 'breitbart.com', 'naturalnews.com', 'beforeitsnews.com',
    'worldnetdaily.com', 'truthfeed.com', 'dailystormer.com', 'zerohedge.com'
]


def search_google_custom(query, num_results=10):
    """Search using Google Custom Search API"""
    try:
        if not GOOGLE_API_KEY or not GOOGLE_CX:
            print("Google API credentials not configured, falling back to DuckDuckGo")
            return search_web_ddgs(query, num_results)
        
        articles = []
        
        # Main search
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_CX,
            'q': query,
            'num': min(num_results, 10),  # Google allows max 10 per request
            'dateRestrict': 'y1',  # Last year only for fresher results
            'safe': 'active'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            for item in items:
                articles.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'source': 'Google',
                    'search_type': 'original'
                })
        
        # Additional fact-checking searches
        fact_check_queries = [
            f"{query} fact check",
            f"{query} debunked false",
            f"{query} verified true"
        ]
        
        for fact_query in fact_check_queries:
            try:
                params['q'] = fact_query
                params['num'] = 3
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    for item in items:
                        articles.append({
                            'title': item.get('title', ''),
                            'snippet': item.get('snippet', ''),
                            'url': item.get('link', ''),
                            'source': 'Google',
                            'search_type': 'fact_check'
                        })
            except:
                continue
        
        return articles
        
    except Exception as e:
        print(f"Google search error: {e}")
        return search_web_ddgs(query, num_results)


def search_web_ddgs(query, num_results=15):
    """Fallback: Enhanced DuckDuckGo search with updated package"""
    try:
        from ddgs import DDGS  # Updated import
        
        articles = []
        
        # Search for the original claim
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
            for result in results:
                articles.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('href', ''),
                    'source': 'DuckDuckGo',
                    'search_type': 'original'
                })
        
        # Search for fact-checking specific queries
        fact_check_queries = [
            f"{query} fact check",
            f"{query} debunked",
            f"{query} verified"
        ]
        
        for fact_query in fact_check_queries:
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(fact_query, max_results=3))
                    for result in results:
                        articles.append({
                            'title': result.get('title', ''),
                            'snippet': result.get('body', ''),
                            'url': result.get('href', ''),
                            'source': 'DuckDuckGo',
                            'search_type': 'fact_check'
                        })
            except:
                continue
                
        return articles[:20]
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
        return []


def search_web_news_api(query, num_results=10):
    """Alternative: Use NewsAPI for news-specific searches"""
    try:
        NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
        if not NEWS_API_KEY:
            return []
        
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'apiKey': NEWS_API_KEY,
            'sortBy': 'relevancy',
            'pageSize': num_results,
            'language': 'en'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = []
            
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'snippet': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': 'NewsAPI',
                    'search_type': 'news'
                })
            
            return articles
        
    except Exception as e:
        print(f"NewsAPI search error: {e}")
        
    return []


def get_source_credibility(url):
    """Rate source credibility based on domain"""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        
        # Remove www. prefix
        domain = domain.replace('www.', '')
        
        if any(trusted in domain for trusted in TRUSTED_SOURCES):
            return 0.9  # High credibility
        elif any(unreliable in domain for unreliable in UNRELIABLE_SOURCES):
            return 0.2  # Low credibility
        elif 'factcheck' in domain or 'snopes' in domain or 'politifact' in domain:
            return 0.95  # Very high credibility for fact-checkers
        elif domain.endswith('.gov') or domain.endswith('.edu'):
            return 0.85  # Government and educational sources
        else:
            return 0.6   # Neutral credibility
    except:
        return 0.5


def enhanced_detect_stance(claim, article_text, title=""):
    """Enhanced stance detection with better keyword analysis"""
    try:
        # Combine title and article for better context
        combined_text = f"{title} {article_text}".lower()
        claim_lower = claim.lower()
        
        # Enhanced keyword lists with more specific patterns
        strong_refuting_words = [
            'false', 'fake', 'hoax', 'debunked', 'disproven', 'myth', 'untrue',
            'misleading', 'misinformation', 'fact-check reveals false', 'not true',
            'fabricated', 'baseless', 'unfounded', 'incorrect', 'wrong',
            'conspiracy theory', 'no evidence', 'lacks evidence', 'unproven',
            'rating: false', 'mostly false', 'pants on fire', 'fiction'
        ]
        
        strong_supporting_words = [
            'confirmed', 'verified', 'proven', 'true', 'accurate', 'correct',
            'evidence shows', 'research confirms', 'studies prove', 'data shows',
            'scientists confirm', 'experts verify', 'officially confirmed',
            'rating: true', 'mostly true', 'legitimate', 'substantiated'
        ]
        
        moderate_refuting_words = [
            'doubt', 'question', 'dispute', 'challenge', 'contradict',
            'inconsistent', 'lacking evidence', 'unsubstantiated', 'skeptical',
            'needs more evidence', 'insufficient proof', 'questionable'
        ]
        
        moderate_supporting_words = [
            'supports', 'indicates', 'suggests', 'shows', 'demonstrates',
            'research indicates', 'study shows', 'evidence suggests',
            'data indicates', 'findings show'
        ]
        
        # Look for fact-checking verdict patterns
        fact_check_patterns = [
            r'rating:?\s*(false|true|mostly false|mostly true|pants on fire)',
            r'verdict:?\s*(false|true|misleading|accurate)',
            r'claim:?\s*.+?\s*(false|true|misleading|accurate)',
            r'(this is|this claim is)\s*(false|true|misleading|accurate)'
        ]
        
        verdict_score = 0
        for pattern in fact_check_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            for match in matches:
                if match.lower() in ['false', 'mostly false', 'pants on fire', 'misleading']:
                    verdict_score -= 3
                elif match.lower() in ['true', 'mostly true', 'accurate']:
                    verdict_score += 3
        
        # Calculate weighted scores
        strong_refute = sum(3 for word in strong_refuting_words if word in combined_text)
        moderate_refute = sum(1 for word in moderate_refuting_words if word in combined_text)
        strong_support = sum(3 for word in strong_supporting_words if word in combined_text)
        moderate_support = sum(1 for word in moderate_supporting_words if word in combined_text)
        
        # Add verdict score from fact-checking patterns
        total_refute = strong_refute + moderate_refute + abs(min(0, verdict_score))
        total_support = strong_support + moderate_support + max(0, verdict_score)
        
        # Check for direct contradictions with claim keywords
        claim_keywords = set(word for word in claim_lower.split() if len(word) > 3)
        contradiction_boost = 0
        for word in claim_keywords:
            if f"not {word}" in combined_text or f"no {word}" in combined_text:
                contradiction_boost += 2
            if f"{word} is false" in combined_text or f"{word} are false" in combined_text:
                contradiction_boost += 3
        
        total_refute += contradiction_boost
        
        # Look for source credibility indicators in the text itself
        credibility_indicators = ['according to experts', 'scientists say', 'research shows', 'study finds']
        credibility_boost = sum(1 for indicator in credibility_indicators if indicator in combined_text)
        
        # Determine stance with improved logic
        if total_refute > total_support:
            # Higher threshold for calling something false
            if total_refute >= total_support * 1.5:
                confidence = min(0.95, 0.7 + (strong_refute * 0.05) + (contradiction_boost * 0.03))
                return 'refutes', confidence
            else:
                return 'neutral', 0.6
        elif total_support > total_refute:
            if total_support >= total_refute * 1.3:
                confidence = min(0.95, 0.7 + (strong_support * 0.05) + (credibility_boost * 0.02))
                return 'supports', confidence
            else:
                return 'neutral', 0.6
        else:
            return 'neutral', 0.5
            
    except Exception as e:
        print(f"Enhanced stance detection error: {e}")
        return 'neutral', 0.5


def analyze_enhanced_credibility(articles_analysis, claim):
    """Enhanced credibility analysis with multiple factors"""
    if not articles_analysis:
        return {
            'verdict': 'insufficient_data',
            'confidence': 0,
            'credibility_score': 0,
            'evidence_quality': 'none',
            'stats': {'refuting': 0, 'supporting': 0, 'neutral': 0}
        }
    
    # Count stances weighted by source credibility and similarity
    weighted_refuting = 0
    weighted_supporting = 0
    weighted_neutral = 0
    
    total_credibility = 0
    high_similarity_articles = 0
    fact_check_articles = 0
    
    for article in articles_analysis:
        # Base weight from credibility and similarity
        base_weight = article['source_credibility'] * (article['similarity'] + 0.1)
        
        # Boost fact-checking articles
        if article.get('search_type') == 'fact_check':
            fact_check_articles += 1
            base_weight *= 2.0  # Give more weight to fact-checking articles
        
        # Boost high similarity articles
        if article['similarity'] > 0.6:
            high_similarity_articles += 1
            base_weight *= 1.3
            
        # Apply stance-specific weighting
        stance_weight = base_weight * article['stance_confidence']
        
        if article['stance'] == 'refutes':
            # Give slightly more weight to refuting evidence to counteract bias
            weighted_refuting += stance_weight * 1.1
        elif article['stance'] == 'supports':
            weighted_supporting += stance_weight
        else:
            weighted_neutral += base_weight * 0.5  # Reduce neutral weight
            
        total_credibility += article['source_credibility']
    
    # Calculate verdict based on weighted evidence
    total_weighted = weighted_refuting + weighted_supporting + weighted_neutral
    
    if total_weighted == 0:
        verdict = 'insufficient_data'
        confidence = 0
        credibility_score = 0
    elif weighted_refuting > weighted_supporting * 1.1:  # Lowered threshold for false detection
        verdict = 'likely_false'
        confidence = min(95, (weighted_refuting / total_weighted) * 100)
        credibility_score = max(5, 100 - confidence)
        
        # Boost confidence if we have fact-checking articles that refute
        if fact_check_articles > 0:
            confidence = min(95, confidence * 1.2)
            
    elif weighted_supporting > weighted_refuting * 1.3:  # Higher threshold for true claims
        verdict = 'likely_true'
        confidence = min(95, (weighted_supporting / total_weighted) * 100)
        credibility_score = min(95, confidence)
    else:
        verdict = 'mixed_evidence'
        confidence = 50
        credibility_score = 50
    
    # Adjust confidence based on evidence quality
    avg_credibility = total_credibility / len(articles_analysis) if articles_analysis else 0
    if avg_credibility > 0.8 and (high_similarity_articles >= 2 or fact_check_articles >= 1):
        evidence_quality = 'high'
        confidence = min(95, confidence * 1.1)
    elif avg_credibility > 0.6 and high_similarity_articles >= 1:
        evidence_quality = 'medium'
    else:
        evidence_quality = 'low'
        confidence *= 0.8
    
    return {
        'verdict': verdict,
        'confidence': int(confidence),
        'credibility_score': int(credibility_score),
        'evidence_quality': evidence_quality,
        'stats': {
            'refuting': sum(1 for a in articles_analysis if a['stance'] == 'refutes'),
            'supporting': sum(1 for a in articles_analysis if a['stance'] == 'supports'),
            'neutral': sum(1 for a in articles_analysis if a['stance'] == 'neutral'),
            'high_credibility_sources': sum(1 for a in articles_analysis if a['source_credibility'] > 0.8),
            'fact_check_sources': fact_check_articles,
            'total_articles': len(articles_analysis)
        }
    }


@app.route('/api/verify', methods=['POST'])
def verify_claim():
    try:
        data = request.get_json()
        claim = data.get('claim', '').strip()
        
        if not claim:
            return jsonify({'error': 'No claim provided'}), 400
        
        print(f"Fact-checking claim: {claim}")
        
        # Try Google search first, fall back to DuckDuckGo
        articles = search_google_custom(claim, num_results=15)
        
        if not articles:
            return jsonify({
                'verdict': 'insufficient_data',
                'confidence': 0,
                'credibility_score': 0,
                'message': 'No relevant articles found',
                'analysis': []
            })
        
        # Analyze each article with enhanced methods
        articles_analysis = []
        for article in articles:
            content = fetch_article_content(article['url'])
            if content:
                similarity = calculate_similarity(claim, content)
                stance, stance_confidence = enhanced_detect_stance(claim, content, article['title'])
                source_credibility = get_source_credibility(article['url'])
                
                # Only include articles with reasonable similarity
                if similarity > 0.2:
                    articles_analysis.append({
                        'title': article['title'],
                        'url': article['url'],
                        'snippet': article['snippet'][:300],
                        'similarity': round(similarity, 3),
                        'stance': stance,
                        'stance_confidence': round(stance_confidence, 2),
                        'source_credibility': round(source_credibility, 2),
                        'relevance': 'high' if similarity > 0.7 else 'medium' if similarity > 0.4 else 'low',
                        'search_type': article.get('search_type', 'original')
                    })
        
        print(f"Analyzed {len(articles_analysis)} relevant articles")
        
        # Calculate overall credibility with enhanced analysis
        result = analyze_enhanced_credibility(articles_analysis, claim)
        result['analysis'] = sorted(articles_analysis, key=lambda x: x['similarity'], reverse=True)
        result['claim'] = claim
        result['timestamp'] = datetime.now().isoformat()
        result['search_engine'] = 'Google' if GOOGLE_API_KEY else 'DuckDuckGo'
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Verification error: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'AI Fact Checker API',
        'version': '2.0',
        'search_engine': 'Google' if GOOGLE_API_KEY else 'DuckDuckGo',
        'endpoints': {
            'health': '/api/health',
            'verify': '/api/verify (POST)'
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'models_loaded': True,
        'google_configured': bool(GOOGLE_API_KEY and GOOGLE_CX),
        'timestamp': datetime.now().isoformat()
    })


def fetch_article_content(url, max_chars=3000):
    """Fetch full article content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:max_chars]
    except Exception as e:
        print(f"Content fetch error for {url}: {e}")
        return ""


def calculate_similarity(claim, article_text):
    """Calculate semantic similarity between claim and article"""
    try:
        if not article_text.strip():
            return 0.0
            
        claim_embedding = similarity_model.encode([claim])
        article_embedding = similarity_model.encode([article_text])
        similarity = util.cos_sim(claim_embedding, article_embedding)[0][0].item()
        return similarity
    except Exception as e:
        print(f"Similarity calculation error: {e}")
        return 0.0


if __name__ == '__main__':
    print("Starting Enhanced Misinformation Detection API...")
    print(f"Google Search: {'Configured' if GOOGLE_API_KEY else 'Not configured, using DuckDuckGo'}")
    app.run(debug=True, host='0.0.0.0', port=5000)