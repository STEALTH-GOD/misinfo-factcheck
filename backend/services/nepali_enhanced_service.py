import requests
from models.ai_models_rtx import get_similarity_model
from models.translator import get_translator
from utils.nepali_optimizer import get_nepali_optimizer
from config import Config
from bs4 import BeautifulSoup

class NepaliEnhancedService:
    def __init__(self):
        self.nepali_optimizer = get_nepali_optimizer()
        self.similarity_model = get_similarity_model()
        self.translator = get_translator()
    
    def multi_translation_similarity(self, claim, article_text):
        """Calculate similarity using multiple translation approaches"""
        try:
            similarities = []
            
            # Original text similarity (if both are Nepali)
            if (self.nepali_optimizer.detect_nepali(claim) and 
                self.nepali_optimizer.detect_nepali(article_text)):
                orig_sim = self.similarity_model.calculate_similarity(claim, article_text)
                similarities.append(orig_sim)
            
            # Translate both to English
            try:
                claim_en = self.translator.translate_text(claim, 'en', 'ne')
                article_en = self.translator.translate_text(article_text, 'en', 'ne')
                en_sim = self.similarity_model.calculate_similarity(claim_en, article_en)
                similarities.append(en_sim)
            except:
                pass
            
            # Translate to Hindi (often better for Nepali)
            try:
                claim_hi = self.translator.translate_text(claim, 'hi', 'ne')
                article_hi = self.translator.translate_text(article_text, 'hi', 'ne')
                hi_sim = self.similarity_model.calculate_similarity(claim_hi, article_hi)
                similarities.append(hi_sim)
            except:
                pass
            
            # Cross-language similarity (Nepali claim vs English article)
            try:
                if not self.nepali_optimizer.detect_nepali(article_text):
                    claim_en = self.translator.translate_text(claim, 'en', 'ne')
                    cross_sim = self.similarity_model.calculate_similarity(claim_en, article_text)
                    similarities.append(cross_sim)
            except:
                pass
            
            # Return the highest similarity score
            return max(similarities) if similarities else 0.0
            
        except Exception as e:
            print(f"Multi-translation similarity error: {e}")
            return 0.0
    
    def enhanced_nepali_analysis(self, claim, articles):
        """Enhanced analysis specifically for Nepali claims"""
        enhanced_articles = []
        
        for article in articles:
            try:
                # Fetch content
                content = self._fetch_content_smart(article['url'])
                if not content:
                    continue
                
                # Enhanced similarity calculation
                similarity = self.multi_translation_similarity(claim, content)
                
                # Enhanced stance detection
                stance, confidence = self.nepali_optimizer.enhance_nepali_stance_detection(
                    claim, content, article.get('title', '')
                )
                
                # Boost confidence if article is from Nepali source
                nepali_source_boost = self._is_nepali_source(article['url'])
                if nepali_source_boost:
                    confidence = min(0.95, confidence * 1.1)
                
                # Enhanced credibility for Nepali sources
                credibility = self._get_nepali_source_credibility(article['url'])
                
                enhanced_articles.append({
                    'title': article['title'],
                    'url': article['url'],
                    'snippet': article['snippet'][:300],
                    'similarity': round(similarity, 3),
                    'stance': stance,
                    'stance_confidence': round(confidence, 2),
                    'source_credibility': round(credibility, 2),
                    'relevance': 'high' if similarity > 0.6 else 'medium' if similarity > 0.3 else 'low',
                    'language': 'ne',
                    'nepali_optimized': True,
                    'nepali_source': nepali_source_boost
                })
                
            except Exception as e:
                print(f"Error processing Nepali article {article['url']}: {e}")
                continue
        
        return enhanced_articles
    
    def _fetch_content_smart(self, url):
        """Smart content fetching with Nepali-specific handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'ne,en;q=0.9',
                'Accept-Charset': 'UTF-8'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'  # Ensure proper UTF-8 handling
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'aside']):
                element.decompose()
            
            # Get text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            text = ' '.join(line for line in lines if line)
            
            # Clean and limit text
            text = self.nepali_optimizer.preprocess_nepali_text(text)
            return text[:Config.MAX_ARTICLE_CHARS]
            
        except Exception as e:
            print(f"Content fetch error: {e}")
            return ""
    
    def _is_nepali_source(self, url):
        """Check if source is Nepali"""
        nepali_domains = [
            'ekantipur.com', 'onlinekhabar.com', 'setopati.com', 'ratopati.com',
            'nepalnews.com', 'khabarhub.com', 'pahilopost.com', 'republica.com',
            'kathmandupost.com', 'ujyaaloonline.com', 'annapurnapost.com',
            'nagariknews.nagariknetwork.com', 'myrepublica.nagariknetwork.com',
            'himalkhabar.com', 'nayapatrikadaily.com', 'thehimalayantimes.com'
        ]
        
        return any(domain in url.lower() for domain in nepali_domains)
    
    def _get_nepali_source_credibility(self, url):
        """Get credibility score for Nepali sources"""
        domain = url.lower()
        
        # High credibility Nepali sources
        if any(trusted in domain for trusted in [
            'ekantipur.com', 'kathmandupost.com', 'thehimalayantimes.com',
            'myrepublica.nagariknetwork.com', 'republica.com'
        ]):
            return 0.9
        
        # Medium credibility
        elif any(medium in domain for medium in [
            'onlinekhabar.com', 'setopati.com', 'ujyaaloonline.com',
            'pahilopost.com', 'khabarhub.com'
        ]):
            return 0.8
        
        # Lower credibility but still relevant
        elif any(lower in domain for lower in [
            'ratopati.com', 'nepalnews.com', 'annapurnapost.com'
        ]):
            return 0.7
        
        # Unknown Nepali source
        elif self._is_nepali_source(url):
            return 0.6
        
        # Non-Nepali source
        else:
            return 0.5

# Global instance
nepali_service = None

def get_nepali_enhanced_service():
    global nepali_service
    if nepali_service is None:
        nepali_service = NepaliEnhancedService()
    return nepali_service