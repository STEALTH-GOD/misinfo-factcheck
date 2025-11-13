import re
from urllib.parse import urlparse
from utils.constants import (
    TRUSTED_SOURCES, NEPALI_TRUSTED_SOURCES, UNRELIABLE_SOURCES,
    HIGH_CREDIBILITY_DOMAINS, MEDIUM_CREDIBILITY_DOMAINS, LOW_CREDIBILITY_DOMAINS
)

class CredibilityScorer:
    def __init__(self):
        # Combine all trusted sources
        self.trusted_sources = TRUSTED_SOURCES + NEPALI_TRUSTED_SOURCES
        self.unreliable_sources = UNRELIABLE_SOURCES
        
        # Domain patterns for credibility assessment
        self.high_credibility_patterns = [
            r'\.edu$', r'\.gov$', r'\.org$'  # Educational, government, organization domains
        ]
        
        self.low_credibility_patterns = [
            r'\.tk$', r'\.ml$', r'\.ga$', r'\.cf$',  # Free domains often used for spam
            r'wordpress\.com', r'blogspot\.com',      # Free blog platforms
            r'facebook\.com', r'twitter\.com',        # Social media
        ]

    def get_source_credibility(self, url):
        """Get credibility score for a source URL"""
        try:
            if not url:
                return 0.5
            
            domain = self.extract_domain(url)
            return self._calculate_domain_credibility(domain)
            
        except Exception as e:
            print(f"Error calculating source credibility: {e}")
            return 0.5

    def get_source_credibility_multilingual(self, url, language='en'):
        """Enhanced credibility scoring with language-specific considerations"""
        try:
            base_credibility = self.get_source_credibility(url)
            
            # Boost score for language-specific trusted sources
            domain = self.extract_domain(url)
            
            if language == 'ne' and any(nepali_source in domain for nepali_source in NEPALI_TRUSTED_SOURCES):
                base_credibility = min(0.95, base_credibility * 1.2)
            
            return base_credibility
            
        except Exception as e:
            print(f"Error in multilingual credibility scoring: {e}")
            return 0.5

    def _calculate_domain_credibility(self, domain):
        """Calculate credibility score based on domain"""
        if not domain:
            return 0.5
        
        domain_lower = domain.lower()
        
        # Check against known reliable sources
        if any(trusted in domain_lower for trusted in self.trusted_sources):
            return 0.9
        
        # Check against known unreliable sources
        if any(unreliable in domain_lower for unreliable in self.unreliable_sources):
            return 0.2
        
        # Check domain patterns
        for pattern in self.high_credibility_patterns:
            if re.search(pattern, domain_lower):
                return 0.8
        
        for pattern in self.low_credibility_patterns:
            if re.search(pattern, domain_lower):
                return 0.3
        
        # Check for news/media indicators
        news_indicators = ['news', 'times', 'post', 'herald', 'tribune', 'journal']
        if any(indicator in domain_lower for indicator in news_indicators):
            return 0.7
        
        # Default credibility for unknown sources
        return 0.5

    def extract_domain(self, url):
        """Extract domain from URL"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception as e:
            print(f"Error extracting domain from {url}: {e}")
            return ""

    def get_credibility_factors(self, url):
        """Get detailed credibility factors for a source"""
        try:
            domain = self.extract_domain(url)
            factors = {
                'domain': domain,
                'is_trusted_source': any(trusted in domain.lower() for trusted in self.trusted_sources),
                'is_unreliable_source': any(unreliable in domain.lower() for unreliable in self.unreliable_sources),
                'has_news_indicators': any(indicator in domain.lower() for indicator in ['news', 'times', 'post']),
                'domain_extension': domain.split('.')[-1] if '.' in domain else 'unknown',
                'credibility_score': self.get_source_credibility(url)
            }
            
            # Check for educational/government domains
            factors['is_educational'] = domain.endswith('.edu')
            factors['is_government'] = domain.endswith('.gov')
            factors['is_organization'] = domain.endswith('.org')
            
            return factors
            
        except Exception as e:
            print(f"Error getting credibility factors: {e}")
            return {'error': str(e), 'credibility_score': 0.5}

    def analyze_enhanced_credibility(self, articles_analysis, claim):
        """Analyze overall credibility of claim based on multiple articles"""
        try:
            if not articles_analysis:
                return {
                    'verdict': 'insufficient_data',
                    'confidence': 0,
                    'credibility_score': 0,
                    'message': 'No articles found for analysis'
                }

            # Calculate weighted credibility scores
            total_weight = 0
            credibility_sum = 0
            stance_scores = {'supports': 0, 'refutes': 0, 'neutral': 0}
            
            for article in articles_analysis:
                similarity = article.get('similarity', 0)
                credibility = article.get('source_credibility', 0.5)
                stance = article.get('stance', 'neutral')
                
                # Weight by similarity and credibility
                weight = similarity * credibility
                total_weight += weight
                credibility_sum += credibility * weight
                
                # Count stances weighted by credibility
                stance_scores[stance] += credibility

            # Calculate overall credibility
            overall_credibility = credibility_sum / total_weight if total_weight > 0 else 0.5

            # Determine verdict based on stance distribution
            total_stance_weight = sum(stance_scores.values())
            if total_stance_weight == 0:
                return {
                    'verdict': 'neutral',
                    'confidence': 50,
                    'credibility_score': overall_credibility
                }

            supports_ratio = stance_scores['supports'] / total_stance_weight
            refutes_ratio = stance_scores['refutes'] / total_stance_weight
            
            # Determine verdict
            if refutes_ratio > 0.6:
                verdict = 'likely_false'
                confidence = min(95, int(refutes_ratio * 100 + overall_credibility * 20))
            elif supports_ratio > 0.6:
                verdict = 'likely_true'
                confidence = min(95, int(supports_ratio * 100 + overall_credibility * 20))
            elif refutes_ratio > supports_ratio * 1.5:
                verdict = 'questionable'
                confidence = min(80, int((refutes_ratio - supports_ratio) * 100 + overall_credibility * 15))
            else:
                verdict = 'mixed_evidence'
                confidence = min(70, int(overall_credibility * 70))

            return {
                'verdict': verdict,
                'confidence': confidence,
                'credibility_score': round(overall_credibility, 3),
                'stance_distribution': {
                    'supports': round(supports_ratio, 2),
                    'refutes': round(refutes_ratio, 2),
                    'neutral': round(stance_scores['neutral'] / total_stance_weight, 2)
                },
                'articles_analyzed': len(articles_analysis),
                'high_credibility_sources': sum(1 for a in articles_analysis if a.get('source_credibility', 0) > 0.8)
            }

        except Exception as e:
            print(f"Error in enhanced credibility analysis: {e}")
            return {
                'verdict': 'error',
                'confidence': 0,
                'credibility_score': 0,
                'message': f'Analysis error: {str(e)}'
            }

# Global credibility scorer instance
credibility_scorer = None

def get_credibility_scorer():
    """Get or create the global credibility scorer instance"""
    global credibility_scorer
    if credibility_scorer is None:
        credibility_scorer = CredibilityScorer()
    return credibility_scorer