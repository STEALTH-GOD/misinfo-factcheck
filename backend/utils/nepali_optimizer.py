import re
from langdetect import detect

class NepaliOptimizer:
    def __init__(self):
        # Expanded Nepali character detection
        self.nepali_chars = set([
            'क', 'ख', 'ग', 'घ', 'ङ', 'च', 'छ', 'ज', 'झ', 'ञ', 
            'ट', 'ठ', 'ड', 'ढ', 'ण', 'त', 'थ', 'द', 'ध', 'न', 
            'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ल', 'व', 'श', 
            'ष', 'स', 'ह', 'क्ष', 'त्र', 'ज्ञ', 'ा', 'ि', 'ी', 
            'ु', 'ू', 'े', 'ै', 'ो', 'ौ', '्', 'ं', 'ः', '।', '॥'
        ])
        
        # Enhanced Nepali keywords
        self.nepali_truth_indicators = [
            # Strong truth indicators
            'सत्य', 'ठिक', 'सही', 'वास्तविक', 'साँचो', 'प्रमाणित', 'पुष्टि',
            'अनुसन्धानले देखाएको', 'वैज्ञानिक तथ्य', 'विश्वसनीय स्रोत',
            'सरकारी तथ्याङ्क', 'आधिकारिक जानकारी', 'प्रामाणिक',
            
            # Research/evidence words
            'अध्ययन', 'अनुसन्धान', 'सर्वेक्षण', 'तथ्याङ्क', 'आंकडा',
            'रिपोर्ट', 'विशेषज्ञ', 'डाक्टर', 'वैज्ञानिक',
            
            # Confirmation phrases
            'पत्ता लागेको छ', 'देखिएको छ', 'भएको छ', 'भनिएको छ',
            'स्पष्ट भएको छ', 'थाहा भएको छ'
        ]
        
        self.nepali_false_indicators = [
            # Strong false indicators
            'झूटो', 'गलत', 'भ्रामक', 'मिथ्या', 'असत्य', 'फर्जी', 'नकली',
            'निराधार', 'आधारहीन', 'बेठिक', 'बेकार', 'भुल',
            
            # Denial words
            'होइन', 'छैन', 'भएको छैन', 'हुन्न', 'हुँदैन', 'हुन सक्दैन',
            'सम्भव छैन', 'असम्भव', 'नभएको', 'नरहेको',
            
            # Refutation phrases
            'तथ्य परीक्षणले देखाएको', 'भ्रम मात्र', 'अफवाह', 'हल्ला',
            'बिना आधार', 'प्रमाणहीन', 'झुक्याउने', 'धोका'
        ]
        
        # Nepali neutral/uncertain words
        self.nepali_neutral_indicators = [
            'सायद', 'हुन सक्छ', 'हुन सक्ने', 'भन्ने गरिएको', 'चर्चामा',
            'बहसमा', 'विवादमा', 'स्पष्ट छैन', 'थाहा छैन', 'अनिश्चित'
        ]
    
    def detect_nepali(self, text):
        """Enhanced Nepali detection"""
        if not text:
            return False
            
        # Count Nepali characters
        nepali_char_count = sum(1 for char in text if char in self.nepali_chars)
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return False
            
        nepali_ratio = nepali_char_count / total_chars
        
        # If more than 30% Nepali characters, consider it Nepali
        return nepali_ratio > 0.3
    
    def preprocess_nepali_text(self, text):
        """Clean and normalize Nepali text"""
        if not text:
            return text
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize some common variations
        text = text.replace('।।', '।')
        text = text.replace('  ', ' ')
        
        return text
    
    def enhance_nepali_stance_detection(self, claim, article_text, title=""):
        """Enhanced stance detection specifically for Nepali"""
        combined_text = f"{title} {article_text}".lower()
        claim_lower = claim.lower()
        
        # Preprocess
        combined_text = self.preprocess_nepali_text(combined_text)
        claim_lower = self.preprocess_nepali_text(claim_lower)
        
        # Score calculation with weighted keywords
        truth_score = 0
        false_score = 0
        neutral_score = 0
        
        # Check for truth indicators
        for indicator in self.nepali_truth_indicators:
            count = combined_text.count(indicator.lower())
            if count > 0:
                # Weight based on strength of indicator
                if any(strong in indicator for strong in ['प्रमाणित', 'वैज्ञानिक', 'अनुसन्धान']):
                    truth_score += count * 3
                else:
                    truth_score += count * 2
        
        # Check for false indicators
        for indicator in self.nepali_false_indicators:
            count = combined_text.count(indicator.lower())
            if count > 0:
                if any(strong in indicator for strong in ['झूटो', 'मिथ्या', 'फर्जी']):
                    false_score += count * 3
                else:
                    false_score += count * 2
        
        # Check for neutral indicators
        for indicator in self.nepali_neutral_indicators:
            count = combined_text.count(indicator.lower())
            neutral_score += count
        
        # Contextual analysis
        # Check if claim keywords are directly contradicted
        claim_keywords = [word for word in claim_lower.split() if len(word) > 2]
        for keyword in claim_keywords:
            if f"{keyword} होइन" in combined_text or f"{keyword} छैन" in combined_text:
                false_score += 2
            if f"{keyword} सही" in combined_text or f"{keyword} ठिक" in combined_text:
                truth_score += 2
        
        # Calculate final stance
        total_score = truth_score + false_score + neutral_score
        
        if total_score == 0:
            return 'neutral', 0.5
        
        if false_score > truth_score * 1.2:  # Bias correction for Nepali
            confidence = min(0.9, 0.6 + (false_score / total_score) * 0.3)
            return 'refutes', confidence
        elif truth_score > false_score * 1.5:
            confidence = min(0.9, 0.6 + (truth_score / total_score) * 0.3)
            return 'supports', confidence
        else:
            return 'neutral', 0.6

# Global instance
nepali_optimizer = None

def get_nepali_optimizer():
    global nepali_optimizer
    if nepali_optimizer is None:
        nepali_optimizer = NepaliOptimizer()
    return nepali_optimizer