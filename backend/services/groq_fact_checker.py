"""
Groq AI Fact Checker
Uses Groq's compound-mini model (FREE) for enhanced fact-checking decisions
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
from groq import Groq

class GroqFactChecker:
    def __init__(self):
        """Initialize Groq AI client with free API key"""
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        
        if not self.groq_api_key:
            print("⚠️  Warning: GROQ_API_KEY not set. Groq AI verification will be disabled.")
            self.client = None
        else:
            try:
                self.client = Groq(api_key=self.groq_api_key)
                print("✅ Groq AI initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Groq: {e}")
                self.client = None
        
        # Free Groq models
        self.model = "llama-3.3-70b-versatile"  # Fast and free
        
    def verify_claim_with_groq(self, claim: str, context_articles: List[Dict] = None) -> Dict[str, Any]:
        """
        Verify a claim using Groq AI's advanced reasoning
        
        Args:
            claim: The claim to verify
            context_articles: List of relevant news articles for context
            
        Returns:
            Dict with verdict, confidence, reasoning, and evidence
        """
        try:
            if not self.client:
                return self._fallback_verification(claim)
            
            print(f"🔍 Groq AI analyzing: {claim}")
            
            # Build context from articles
            article_context = self._build_article_context(context_articles)
            
            # Create fact-checking prompt
            prompt = self._create_fact_checking_prompt(claim, article_context)
            
            # Get Groq AI analysis
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert fact-checker specializing in Nepal news and current events. 
Your task is to analyze claims and provide accurate, well-reasoned verdicts.

IMPORTANT:
- Use the provided recent news articles as evidence
- Focus on logical reasoning and cross-referencing
- Be specific about why you believe something is true or false
- Consider source credibility
- Look for contradictory evidence carefully

Respond in JSON format ONLY."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent fact-checking
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            # Parse Groq response
            result = self._parse_groq_response(response, claim)
            
            print(f"✅ Groq verdict: {result['verdict']} ({result['confidence']}% confidence)")
            
            return result
            
        except Exception as e:
            print(f"❌ Groq AI error: {e}")
            return self._fallback_verification(claim)
    
    def _create_fact_checking_prompt(self, claim: str, article_context: str) -> str:
        """Create a detailed fact-checking prompt for Groq"""
        
        prompt = f"""Analyze this claim and provide a fact-check verdict:

CLAIM TO VERIFY:
"{claim}"

RECENT NEWS CONTEXT:
{article_context}

TASK:
Analyze the claim carefully and provide your fact-check in this EXACT JSON format:

{{
    "verdict": "true/false/mixed/unverified",
    "confidence": 85,
    "reasoning": "Step-by-step analysis explaining your verdict. Be specific about what evidence supports or contradicts the claim.",
    "key_evidence": [
        "First piece of evidence from the news articles",
        "Second piece of evidence",
        "Third piece of evidence"
    ],
    "contradictions_found": [
        "Any contradictory information if verdict is false"
    ],
    "fact_check_summary": "One paragraph summary of your analysis",
    "reliability_assessment": "Assessment of the sources and information quality"
}}

GUIDELINES:
1. If recent news shows the person/event is active/present elsewhere, claim is FALSE
2. If multiple credible sources confirm the claim, it's TRUE
3. If sources conflict or insufficient evidence, it's MIXED or UNVERIFIED
4. Be specific about dates, sources, and contradictions
5. Consider source credibility in your analysis

Provide ONLY valid JSON, no additional text."""

        return prompt
    
    def _build_article_context(self, articles: List[Dict]) -> str:
        """Build context string from articles"""
        if not articles:
            return "No recent news articles available for context."
        
        context_parts = []
        
        for i, article in enumerate(articles[:10], 1):  # Limit to 10 articles
            context_parts.append(f"""
Article {i}:
Title: {article.get('title', 'Unknown')}
Source: {article.get('source', 'Unknown')}
Published: {article.get('published_date', 'Unknown')}
Content: {article.get('snippet', article.get('description', 'No content'))[:300]}
""")
        
        return "\n".join(context_parts)
    
    def _parse_groq_response(self, response, claim: str) -> Dict[str, Any]:
        """Parse Groq AI response into structured format"""
        try:
            # Extract JSON from response
            content = response.choices[0].message.content
            
            # Parse JSON
            result = json.loads(content)
            
            # Validate and normalize
            verdict = result.get('verdict', 'unverified').lower()
            confidence = min(95, max(0, int(result.get('confidence', 50))))
            
            return {
                'claim': claim,
                'verdict': verdict,
                'confidence': confidence,
                'reasoning': result.get('reasoning', 'No reasoning provided'),
                'key_evidence': result.get('key_evidence', []),
                'contradictions_found': result.get('contradictions_found', []),
                'fact_check_summary': result.get('fact_check_summary', ''),
                'reliability_assessment': result.get('reliability_assessment', ''),
                'ai_model': self.model,
                'analysis_timestamp': datetime.now().isoformat(),
                'groq_powered': True
            }
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse Groq JSON: {e}")
            # Try to extract verdict from text
            return self._extract_verdict_from_text(response.choices[0].message.content, claim)
        except Exception as e:
            print(f"❌ Error parsing Groq response: {e}")
            return self._fallback_verification(claim)
    
    def _extract_verdict_from_text(self, text: str, claim: str) -> Dict[str, Any]:
        """Extract verdict if JSON parsing fails"""
        text_lower = text.lower()
        
        # Determine verdict from text
        if 'verdict: false' in text_lower or 'is false' in text_lower:
            verdict = 'false'
            confidence = 70
        elif 'verdict: true' in text_lower or 'is true' in text_lower:
            verdict = 'true'
            confidence = 70
        elif 'mixed' in text_lower:
            verdict = 'mixed'
            confidence = 50
        else:
            verdict = 'unverified'
            confidence = 30
        
        return {
            'claim': claim,
            'verdict': verdict,
            'confidence': confidence,
            'reasoning': text[:500],
            'key_evidence': [],
            'fact_check_summary': 'Analysis completed but response format was non-standard',
            'ai_model': self.model,
            'analysis_timestamp': datetime.now().isoformat(),
            'groq_powered': True,
            'parse_fallback': True
        }
    
    def _fallback_verification(self, claim: str) -> Dict[str, Any]:
        """Fallback when Groq is unavailable"""
        return {
            'claim': claim,
            'verdict': 'unverified',
            'confidence': 10,
            'reasoning': 'Groq AI service unavailable. Unable to perform advanced analysis.',
            'key_evidence': [],
            'fact_check_summary': 'Groq AI verification could not be performed.',
            'reliability_assessment': 'Manual verification recommended',
            'ai_model': 'fallback',
            'groq_powered': False,
            'fallback': True
        }
    
    def analyze_claim_with_context(self, claim: str, recent_news: List[Dict], domain_credibility: float) -> Dict[str, Any]:
        """
        Enhanced claim analysis with Groq AI
        
        Args:
            claim: The claim to analyze
            recent_news: Recent news articles for context
            domain_credibility: Source credibility score (0-1)
        
        Returns:
            Comprehensive analysis result
        """
        try:
            # Get Groq verification
            groq_result = self.verify_claim_with_groq(claim, recent_news)
            
            # Enhance with domain credibility
            final_confidence = self._calculate_final_confidence(
                groq_result['confidence'],
                domain_credibility,
                len(recent_news)
            )
            
            # Determine final verdict
            final_verdict = self._determine_final_verdict(
                groq_result['verdict'],
                domain_credibility,
                len(recent_news)
            )
            
            return {
                'claim': claim,
                'final_verdict': final_verdict,
                'final_confidence': final_confidence,
                'groq_analysis': groq_result,
                'domain_credibility': domain_credibility,
                'evidence_count': len(recent_news),
                'analysis_method': 'Groq AI Enhanced Verification',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Enhanced analysis error: {e}")
            return {
                'claim': claim,
                'final_verdict': 'unverified',
                'final_confidence': 20,
                'error': str(e),
                'fallback': True
            }
    
    def _calculate_final_confidence(self, groq_confidence: float, domain_credibility: float, evidence_count: int) -> float:
        """Calculate weighted final confidence score"""
        # Weight: 60% Groq AI, 30% domain credibility, 10% evidence count
        groq_weight = 0.6
        domain_weight = 0.3
        evidence_weight = 0.1
        
        # Normalize evidence count (0-10+ articles)
        evidence_score = min(100, (evidence_count / 10) * 100)
        domain_score = domain_credibility * 100
        
        final = (groq_confidence * groq_weight + 
                domain_score * domain_weight + 
                evidence_score * evidence_weight)
        
        return round(min(95, final), 1)
    
    def _determine_final_verdict(self, groq_verdict: str, domain_credibility: float, evidence_count: int) -> str:
        """Determine final verdict with additional context"""
        # If Groq is confident and there's evidence, trust it
        if groq_verdict in ['true', 'false'] and evidence_count >= 3:
            return groq_verdict
        
        # If domain credibility is very low, be more skeptical
        if domain_credibility < 0.5 and groq_verdict == 'true':
            return 'mixed'
        
        # If there's little evidence, be cautious
        if evidence_count < 2 and groq_verdict in ['true', 'false']:
            return 'unverified'
        
        return groq_verdict


# Global instance
groq_fact_checker = None

def get_groq_fact_checker():
    """Get or create the global Groq fact checker instance"""
    global groq_fact_checker
    if groq_fact_checker is None:
        groq_fact_checker = GroqFactChecker()
    return groq_fact_checker
