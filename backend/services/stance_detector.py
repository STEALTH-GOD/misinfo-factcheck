from utils.constants import (ENGLISH_REFUTING_WORDS, ENGLISH_SUPPORTING_WORDS,
                           NEPALI_REFUTING_WORDS, NEPALI_SUPPORTING_WORDS,
                           HINDI_REFUTING_WORDS, HINDI_SUPPORTING_WORDS)

class StanceDetector:
    def detect_stance(self, claim, article_text, title=""):
        """Basic stance detection method (wrapper for enhanced method)"""
        try:
            # Detect language first
            from utils.language_detector import detect_language
            from utils.nepali_optimizer import get_nepali_optimizer
            
            nepali_optimizer = get_nepali_optimizer()
            
            # Check if it's Nepali content
            if nepali_optimizer.detect_nepali(claim) or nepali_optimizer.detect_nepali(article_text):
                language = 'ne'
            else:
                language = detect_language(claim)
            
            # Use the enhanced multilingual method
            return self.enhanced_detect_stance_multilingual(claim, article_text, title, language)
            
        except Exception as e:
            print(f"Basic stance detection error: {e}")
            return 'neutral', 0.5
    
    def enhanced_detect_stance_multilingual(self, claim, article_text, title="", language='en'):
        """Enhanced multilingual stance detection"""
        try:
            from models.translator import get_translator
            translator = get_translator()
            
            combined_text = f"{title} {article_text}".lower()
            claim_lower = claim.lower()
            
            # Get language-specific keywords
            strong_refuting_words = ENGLISH_REFUTING_WORDS.copy()
            strong_supporting_words = ENGLISH_SUPPORTING_WORDS.copy()
            
            # Add language-specific keywords
            if language == 'ne':
                strong_refuting_words.extend(NEPALI_REFUTING_WORDS)
                strong_supporting_words.extend(NEPALI_SUPPORTING_WORDS)
                
                # Use Nepali optimizer for better analysis
                from utils.nepali_optimizer import get_nepali_optimizer
                nepali_optimizer = get_nepali_optimizer()
                return nepali_optimizer.enhance_nepali_stance_detection(claim, article_text, title)
                
            elif language == 'hi':
                strong_refuting_words.extend(HINDI_REFUTING_WORDS)
                strong_supporting_words.extend(HINDI_SUPPORTING_WORDS)
            
            # If analyzing non-English content, try translation for better analysis
            translated_text = combined_text
            if language != 'en':
                try:
                    translated_text = translator.translate_text(combined_text, 'en', language).lower()
                except Exception as e:
                    print(f"Translation error in stance detection: {e}")
                    pass
            
            # Analyze both original and translated text
            texts_to_analyze = [combined_text]
            if language != 'en' and translated_text != combined_text:
                texts_to_analyze.append(translated_text)
            
            total_refute = 0
            total_support = 0
            
            for text in texts_to_analyze:
                # Calculate scores for this text
                refute_score = sum(3 for word in strong_refuting_words if word in text)
                support_score = sum(3 for word in strong_supporting_words if word in text)
                
                # Add weight for stronger indicators
                for word in ['false', 'fake', 'debunked', 'misleading', 'incorrect']:
                    if word in text:
                        refute_score += 5
                
                for word in ['true', 'correct', 'verified', 'confirmed', 'accurate']:
                    if word in text:
                        support_score += 5
                
                total_refute += refute_score
                total_support += support_score
            
            # Check for direct contradictions
            claim_keywords = set(word for word in claim_lower.split() if len(word) > 3)
            contradiction_boost = 0
            
            for text in texts_to_analyze:
                for word in claim_keywords:
                    # Direct negation patterns
                    negation_patterns = [
                        f"not {word}", f"no {word}", f"{word} is false", 
                        f"{word} are false", f"{word} is incorrect", 
                        f"{word} is wrong", f"debunked {word}"
                    ]
                    
                    for pattern in negation_patterns:
                        if pattern in text:
                            contradiction_boost += 3
            
            total_refute += contradiction_boost
            
            # Calculate total indicators
            total_indicators = total_refute + total_support
            
            # Determine stance with improved logic
            if total_indicators == 0:
                return 'neutral', 0.5
            
            if total_refute > total_support:
                if total_refute >= total_support * 1.5:
                    confidence = min(0.95, 0.6 + (total_refute / max(total_indicators, 1)) * 0.3)
                    return 'refutes', confidence
                else:
                    return 'neutral', 0.6
            elif total_support > total_refute:
                if total_support >= total_refute * 1.3:
                    confidence = min(0.95, 0.6 + (total_support / max(total_indicators, 1)) * 0.3)
                    return 'supports', confidence
                else:
                    return 'neutral', 0.6
            else:
                return 'neutral', 0.5
                
        except Exception as e:
            print(f"Enhanced stance detection error: {e}")
            return 'neutral', 0.5
    
    def analyze_stance_confidence(self, claim, articles_analysis):
        """Analyze overall stance confidence across multiple articles"""
        try:
            if not articles_analysis:
                return 'neutral', 0.5
            
            supports_count = sum(1 for a in articles_analysis if a.get('stance') == 'supports')
            refutes_count = sum(1 for a in articles_analysis if a.get('stance') == 'refutes')
            neutral_count = sum(1 for a in articles_analysis if a.get('stance') == 'neutral')
            
            total_articles = len(articles_analysis)
            
            # Calculate weighted confidence based on source credibility
            weighted_supports = sum(a.get('source_credibility', 0.5) for a in articles_analysis if a.get('stance') == 'supports')
            weighted_refutes = sum(a.get('source_credibility', 0.5) for a in articles_analysis if a.get('stance') == 'refutes')
            
            # Determine overall stance
            if refutes_count > supports_count and weighted_refutes > weighted_supports * 0.8:
                confidence = min(0.95, 0.5 + (refutes_count / total_articles) * 0.4)
                return 'refutes', confidence
            elif supports_count > refutes_count and weighted_supports > weighted_refutes * 0.8:
                confidence = min(0.95, 0.5 + (supports_count / total_articles) * 0.4)
                return 'supports', confidence
            else:
                return 'neutral', 0.6
                
        except Exception as e:
            print(f"Stance confidence analysis error: {e}")
            return 'neutral', 0.5

# Global stance detector instance
stance_detector = None

def get_stance_detector():
    """Get or create the global stance detector instance"""
    global stance_detector
    if stance_detector is None:
        stance_detector = StanceDetector()
    return stance_detector