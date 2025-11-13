import requests
from bs4 import BeautifulSoup
from config import Config

class ContentService:
    def fetch_article_content(self, url, max_chars=None):
        """Fetch full article content from URL"""
        if max_chars is None:
            max_chars = Config.MAX_ARTICLE_CHARS
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=Config.TIMEOUT)
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
    
    def calculate_similarity_multilingual(self, claim, article_text, language='en'):
        """Calculate similarity with translation support"""
        try:
            from models.ai_models import get_similarity_model
            from models.translator import get_translator
            
            similarity_model = get_similarity_model()
            translator = get_translator()
            
            if not article_text.strip():
                return 0.0
            
            # For non-English content, try both original and translated versions
            if language != 'en':
                try:
                    claim_en = translator.translate_text(claim, 'en', language)
                    article_en = translator.translate_text(article_text, 'en', language)
                    
                    # Calculate similarity for both original and translated
                    orig_similarity = similarity_model.calculate_similarity(claim, article_text)
                    trans_similarity = similarity_model.calculate_similarity(claim_en, article_en)
                    
                    # Return the higher similarity score
                    return max(orig_similarity, trans_similarity)
                    
                except:
                    # Fallback to original language analysis
                    pass
            
            # Standard similarity calculation
            return similarity_model.calculate_similarity(claim, article_text)
            
        except Exception as e:
            print(f"Multilingual similarity calculation error: {e}")
            return 0.0

# Global content service instance
content_service = None

def get_content_service():
    """Get or create the global content service instance"""
    global content_service
    if content_service is None:
        content_service = ContentService()
    return content_service