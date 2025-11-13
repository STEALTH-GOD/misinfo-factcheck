import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

# Import our modules (simplified imports)
from config import Config
from utils.language_detector import detect_language
from services.search_service import get_search_service
from services.content_service import get_content_service
from services.stance_detector import get_stance_detector
from services.credibility_scorer import get_credibility_scorer
from services.news_retrieval_service import get_news_retrieval_service
from models.ai_models import get_similarity_model  # Use simple version

app = Flask(__name__)
CORS(app)

# Initialize services (simplified)
print("Initializing AI Fact Checker services...")
search_service = get_search_service()
content_service = get_content_service()
stance_detector = get_stance_detector()
credibility_scorer = get_credibility_scorer()
news_service = get_news_retrieval_service()
similarity_model = get_similarity_model()  # No GPU parameter needed
print("All services initialized successfully!")

# Homepage News Endpoint
@app.route('/api/homepage-news', methods=['GET'])
def get_homepage_news():
    """Get Nepal-focused news for homepage display"""
    try:
        language = request.args.get('language', 'en')
        category = request.args.get('category', 'all')
        
        print(f"Getting Nepal-focused news for language: {language}")
        
        if category == 'all':
            # Use the correct method name that exists in your class
            news_data = news_service.get_all_news_categories(language)
        else:
            news_data = {
                category: news_service.get_trending_news(category, limit=6, language=language)
            }
        
        return jsonify({
            'status': 'success',
            'data': news_data,
            'timestamp': datetime.now().isoformat(),
            'language': language,
            'context': 'Nepal-focused'
        })
        
    except Exception as e:
        print(f"Nepal homepage news error: {e}")
        import traceback
        traceback.print_exc()  # This will show the full error details
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve Nepal news: {str(e)}',
            'data': {
                'recent': [],
                'verified_true': [],
                'verified_false': []
            }
        }), 500

# Article Details Endpoint
@app.route('/api/article/<article_id>', methods=['GET'])
def get_article_details(article_id):
    """Get detailed article information - real URLs only"""
    try:
        url = request.args.get('url')
        title = request.args.get('title', '')
        
        print(f"Getting article details for ID: {article_id}, URL: {url}")
        
        if not url:
            return jsonify({
                'status': 'error',
                'message': 'Article URL is required'
            }), 400
        
        # Get article details from news service
        from services.news_retrieval_service import get_news_retrieval_service
        news_service = get_news_retrieval_service()
        
        article_details = news_service.get_article_details(article_id, url, title)
        
        # Check if it's an error response
        if isinstance(article_details, dict) and article_details.get('status') == 'error':
            return jsonify({
                'status': 'error',
                'message': article_details.get('message', 'Article not accessible'),
                'error': article_details.get('error', 'URL validation failed')
            }), 404
        
        if not article_details:
            return jsonify({
                'status': 'error',
                'message': 'Article not found or not accessible'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': article_details,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Article details error: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': 'Failed to process article request'
        }), 500

# Main Verification Endpoint (Updated)
@app.route('/api/verify', methods=['POST'])
def verify_claim():
    try:
        data = request.get_json()
        claim = data.get('claim', '').strip()
        
        if not claim:
            return jsonify({'error': 'No claim provided'}), 400
        
        print(f"Fact-checking claim: {claim}")
        
        # Enhanced language detection
        from utils.nepali_optimizer import get_nepali_optimizer
        nepali_optimizer = get_nepali_optimizer()
        
        is_nepali = nepali_optimizer.detect_nepali(claim)
        detected_language = 'ne' if is_nepali else detect_language(claim)
        
        print(f"Detected language: {detected_language} (Enhanced: {is_nepali})")
        
        # Search for articles
        articles = search_service.search_google_custom_multilingual(
            claim, num_results=Config.DEFAULT_SEARCH_RESULTS, language=detected_language
        )
        
        if not articles:
            return jsonify({
                'verdict': 'insufficient_data',
                'confidence': 0,
                'credibility_score': 0,
                'detected_language': detected_language,
                'message': 'कुनै सान्दर्भिक लेख फेला परेन' if is_nepali else 'No relevant articles found',
                'analysis': []
            })
        
        # Use enhanced Nepali service if Nepali claim
        if is_nepali:
            print("Using enhanced Nepali processing...")
            from services.nepali_enhanced_service import get_nepali_enhanced_service
            nepali_service = get_nepali_enhanced_service()
            articles_analysis = nepali_service.enhanced_nepali_analysis(claim, articles)
        else:
            # Standard processing for other languages
            articles_analysis = []
            for article in articles:
                content = content_service.fetch_article_content(article['url'])
                if content:
                    similarity = content_service.calculate_similarity_multilingual(
                        claim, content, detected_language
                    )
                    stance, stance_confidence = stance_detector.enhanced_detect_stance_multilingual(
                        claim, content, article['title'], detected_language
                    )
                    source_credibility = credibility_scorer.get_source_credibility_multilingual(
                        article['url'], detected_language
                    )
                    
                    if similarity > Config.SIMILARITY_THRESHOLD:
                        articles_analysis.append({
                            'title': article['title'],
                            'url': article['url'],
                            'snippet': article['snippet'][:300],
                            'similarity': round(similarity, 3),
                            'stance': stance,
                            'stance_confidence': round(stance_confidence, 2),
                            'source_credibility': round(source_credibility, 2),
                            'relevance': 'high' if similarity > 0.7 else 'medium' if similarity > 0.4 else 'low',
                            'search_type': article.get('search_type', 'original'),
                            'language': article.get('language', detected_language),
                            'nepali_optimized': False
                        })
        
        print(f"Analyzed {len(articles_analysis)} relevant articles")
        
        # Calculate overall credibility
        result = credibility_scorer.analyze_enhanced_credibility(articles_analysis, claim)
        
        # Adjust scoring for Nepali content
        if is_nepali and articles_analysis:
            nepali_sources = sum(1 for a in articles_analysis if a.get('nepali_source', False))
            if nepali_sources > 0:
                result['confidence'] = min(95, result['confidence'] * 1.1)
                result['nepali_sources_found'] = nepali_sources
        
        result['analysis'] = sorted(articles_analysis, key=lambda x: x['similarity'], reverse=True)
        result['claim'] = claim
        result['detected_language'] = detected_language
        result['enhanced_nepali'] = is_nepali
        result['timestamp'] = datetime.now().isoformat()
        result['search_engine'] = 'Google' if Config.GOOGLE_API_KEY else 'DuckDuckGo'
        
        # Add Nepali-specific messages
        if is_nepali:
            result['language_note'] = 'नेपाली भाषामा उन्नत विश्लेषण गरिएको'
            if result['verdict'] == 'likely_false':
                result['nepali_message'] = 'यो दावी झूटो हुन सक्छ'
            elif result['verdict'] == 'likely_true':
                result['nepali_message'] = 'यो दावी साँचो हुन सक्छ'
            else:
                result['nepali_message'] = 'यो दावीबारे मिश्रित प्रमाण छन्'
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Verification error: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Health check endpoint (simplified)
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'search': 'operational',
            'content': 'operational', 
            'ai_models': 'operational',
            'news_retrieval': 'operational'
        },
        'device_info': similarity_model.get_device_info()
    })

# Add this route to your app.py after the homepage-news route:

@app.route('/api/news/categories', methods=['GET'])
def get_news_categories():
    """Get news categories - alternative endpoint"""
    try:
        language = request.args.get('language', 'en')
        
        print(f"Getting news categories for language: {language}")
        
        news_data = news_service.get_all_news_categories(language)
        
        return jsonify({
            'status': 'success',
            'data': news_data,
            'timestamp': datetime.now().isoformat(),
            'language': language
        })
        
    except Exception as e:
        print(f"News categories error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve news categories: {str(e)}',
            'data': {
                'recent': [],
                'verified_true': [],
                'verified_false': [],
                'international': []
            }
        }), 500

if __name__ == '__main__':
    print("🚀 Starting AI Fact Checker API...")
    print(f"🖥️ Processing: CPU-based (Simplified)")
    print(f"🌐 Languages: English, Nepali, Hindi")
    print(f"🔍 Search: {'Google Custom' if Config.GOOGLE_API_KEY else 'DuckDuckGo'}")
    print(f"📰 News Feed: Enabled")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )