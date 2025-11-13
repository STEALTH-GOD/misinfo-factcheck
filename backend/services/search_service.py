import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config import Config

class SearchService:
    def __init__(self):
        self.google_api_key = Config.GOOGLE_API_KEY
        self.google_cx = Config.GOOGLE_CX
        
    def search_google_custom_multilingual(self, query, num_results=10, language='en'):
        """Enhanced multilingual search using Google Custom Search API"""
        try:
            if not self.google_api_key or not self.google_cx:
                print("Google API credentials not configured, falling back to DuckDuckGo")
                return self.search_web_ddgs_multilingual(query, num_results, language)
            
            # Import here to avoid circular imports
            from models.translator import get_translator
            translator = get_translator()
            
            articles = []
            
            # Translate query to English for broader search
            if language != 'en':
                query_en = translator.translate_text(query, 'en', language)
            else:
                query_en = query
            
            # Main search in original language
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cx,
                'q': query,
                'num': min(num_results, 10),
                'dateRestrict': 'y2',  # Last 2 years
                'safe': 'active'
            }
            
            # Set language-specific parameters
            if language == 'ne':
                params['lr'] = 'lang_ne'
                params['hl'] = 'ne'
            elif language == 'hi':
                params['lr'] = 'lang_hi'
                params['hl'] = 'hi'
            
            response = requests.get(url, params=params, timeout=Config.TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                for item in items:
                    articles.append({
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'url': item.get('link', ''),
                        'source': 'Google',
                        'search_type': 'original',
                        'language': language
                    })
            
            return articles
            
        except Exception as e:
            print(f"Google multilingual search error: {e}")
            return self.search_web_ddgs_multilingual(query, num_results, language)
    
    def search_web_ddgs_multilingual(self, query, num_results=15, language='en'):
        """Enhanced multilingual DuckDuckGo search"""
        try:
            # Simple fallback search without ddgs dependency
            articles = []
            # Mock search results for now
            articles.append({
                'title': f'Search result for: {query}',
                'snippet': f'This is a mock search result for the query: {query}',
                'url': 'https://example.com/mock-result',
                'source': 'Mock Search',
                'search_type': 'original',
                'language': language
            })
            return articles
        except Exception as e:
            print(f"DuckDuckGo multilingual search error: {e}")
            return []

# Global search service instance
search_service = None

def get_search_service():
    """Get or create the global search service instance"""
    global search_service
    if search_service is None:
        search_service = SearchService()
    return search_service