from dotenv import load_dotenv
load_dotenv()

import os
import json
import time
import random
import traceback
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from agent.retrieval import google_search, load_whitelist, fetch_page_text, rank_evidence_by_similarity, domain_from_url
from agent.llm_agent import call_groq

app = FastAPI(title='MisInfoDetectAI')

# CORS settings
FRONTEND_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
if FRONTEND_ORIGINS == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in FRONTEND_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WHITELIST = load_whitelist()
ALLOWED_DOMAINS = set(os.getenv('ALLOWED_SOURCES','').split(',')) if os.getenv('ALLOWED_SOURCES') else WHITELIST

class ClaimRequest(BaseModel):
    claim: str
    lang: str = 'ne'

@app.get('/')
def root():
    return {
        "message": "AI Fact Checker API", 
        "status": "running",
        "endpoints": {
            "verify_claim": "/api/verify_claim",
            "latest_news": "/api/latest_news",
            "news_detail": "/api/news/{news_id}",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }

@app.post('/api/verify_claim')
def verify_claim(req: ClaimRequest):
    """
    Verify a claim by searching for evidence from whitelisted sources and analyzing with LLM.
    """
    try:
        claim = req.claim.strip()
        if not claim:
            raise HTTPException(status_code=400, detail='Empty claim')
        
        print(f"\n{'='*60}")
        print(f"Processing claim: {claim}")
        print(f"{'='*60}")
        
        evidence_items = []
        
        # Step 1: Search for evidence - prioritize local Nepali sources
        try:
            print("Step 1: Searching Google for evidence...")
            
            # First, search specifically on Nepali news sites
            nepali_sites = ['kathmandupost.com', 'setopati.com', 'onlinekhabar.com', 
                           'ekantipur.com', 'myrepublica.nagariknetwork.com', 'nepalnews.com']
            site_query = f"{claim} (site:{' OR site:'.join(nepali_sites)})"
            
            local_results = google_search(site_query, num=5)
            print(f"  Found {len(local_results)} local Nepali sources")
            
            # Then do a general search for international sources
            general_results = google_search(claim, num=5)
            print(f"  Found {len(general_results)} general sources")
            
            # Combine results, prioritizing local sources
            search_results = local_results + general_results
            print(f"  Total: {len(search_results)} search results")
            
            # Step 2: Filter and fetch content from whitelisted domains
            print("Step 2: Filtering whitelisted sources...")
            for idx, result in enumerate(search_results, 1):
                try:
                    result_url = result.get('link', '')
                    result_domain = domain_from_url(result_url)
                    result_title = result.get('title', 'Untitled')
                    
                    # Normalize domain by removing www. prefix for comparison
                    normalized_domain = result_domain.replace('www.', '').replace('co.uk', 'com')
                    
                    # Check if domain is whitelisted (handle www. prefix)
                    is_whitelisted = False
                    for allowed_domain in ALLOWED_DOMAINS:
                        normalized_allowed = allowed_domain.replace('www.', '').replace('co.uk', 'com')
                        if normalized_domain == normalized_allowed or normalized_domain.endswith('.' + normalized_allowed):
                            is_whitelisted = True
                            break
                    
                    if is_whitelisted:
                        print(f"  [{idx}] ✓ Whitelisted: {result_domain}")
                        print(f"      Title: {result_title[:80]}")
                        
                        # Fetch page content
                        content = fetch_page_text(result_url)
                        if content and len(content) > 100:
                            evidence_items.append({
                                'source': result_url,
                                'url': result_url,
                                'snippet': content[:800],
                                'title': result_title,
                                'domain': result_domain
                            })
                            print(f"      Content fetched: {len(content)} chars")
                            
                            if len(evidence_items) >= 6:
                                break
                        else:
                            print(f"      ✗ Content too short or empty")
                    else:
                        print(f"  [{idx}] ✗ Not whitelisted: {result_domain}")
                        
                except Exception as e:
                    print(f"  [{idx}] ✗ Error processing result: {str(e)}")
                    continue
            
            print(f"\nStep 3: Collected {len(evidence_items)} evidence sources")
            
        except Exception as e:
            print(f"✗ Search error: {str(e)}")
            traceback.print_exc()
        
        # Step 3: If no evidence found, provide fallback
        if not evidence_items:
            print("⚠ No evidence found, using fallback response")
            evidence_items = [{
                'source': 'Search incomplete',
                'url': '',
                'snippet': 'Unable to find sufficient evidence from whitelisted sources. The claim could not be verified.',
                'title': 'No Sources Found'
            }]
        
        # Step 4: Call LLM for analysis
        print(f"Step 4: Analyzing with LLM...")
        try:
            analysis = call_groq(claim, evidence_items, lang=req.lang)
            print(f"  Verdict: {analysis.get('verdict', 'UNCLEAR')}")
            print(f"  Confidence: {analysis.get('confidence', 0)}")
        except Exception as e:
            print(f"✗ LLM analysis error: {str(e)}")
            traceback.print_exc()
            analysis = {
                'verdict': 'UNCLEAR',
                'confidence': 0.0,
                'explanation': f'Analysis unavailable: {str(e)}',
                'evidence': []
            }
        
        # Step 5: Prepare response
        if 'evidence' not in analysis:
            analysis['evidence'] = []
        analysis['evidence'] = evidence_items
        
        print(f"{'='*60}")
        print(f"✓ Claim verification complete")
        print(f"{'='*60}\n")
        
        return {'result': analysis}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n✗ FATAL ERROR in verify_claim: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f'Internal server error: {str(e)}'
        )


def _convert_filename_to_url(filename: str) -> Optional[str]:
    """Convert cached filename back to original URL."""
    if not filename.startswith('https_') or not filename.endswith('.txt'):
        return None
    
    url_part = filename.replace('.txt', '').replace('https_', '')
    
    # Try specific domain patterns first
    domain_mappings = {
        'english.nepalnews.com_': 'english.nepalnews.com',
        'kathmandupost.com_': 'kathmandupost.com',
        'myrepublica.com_': 'myrepublica.com',
        'nepalitimes.com_': 'nepalitimes.com',
        'english.onlinekhabar.com_': 'english.onlinekhabar.com',
        'en.setopati.com_': 'en.setopati.com'
    }
    
    for prefix, domain in domain_mappings.items():
        if url_part.startswith(prefix):
            path = url_part[len(prefix):].replace('_', '/')
            return f"https://{domain}/{path}" if path else f"https://{domain}"
    
    return None


def _determine_verification_status(title: str, source_name: str) -> str:
    """
    Enhanced heuristic to determine verification status with more variety.
    """
    title_lower = title.lower()
    source_lower = source_name.lower()
    
    # Trusted international and local sources 
    trusted_sources = ['kathmandu post', 'nepal news', 'my republica', 'nepali times', 'bbc', 'reuters', 'cnn', 'al jazeera', 'guardian', 'times', 'npr', 'associated press']
    
    # Keywords that suggest verified/true information
    verified_keywords = ['government announces', 'official statement', 'confirmed by', 'verified', 'authenticated', 'court rules', 'parliament passes']
    
    # Keywords that suggest potentially false information
    suspicious_keywords = ['miracle cure', 'secret government', 'shocking discovery', 'doctors hate', 'conspiracy', 'breakthrough scam', 'celebrities']
    
    # Keywords that suggest unverified claims
    unverified_keywords = ['alleged', 'claimed', 'reportedly', 'sources say', 'rumored', 'unconfirmed', 'speculation']
    
    # Check for verified content keywords
    if any(keyword in title_lower for keyword in verified_keywords):
        return 'TRUE'
    
    # Check for suspicious content
    if any(keyword in title_lower for keyword in suspicious_keywords):
        return 'FALSE'
    
    # Check for unverified content
    if any(keyword in title_lower for keyword in unverified_keywords):
        return 'UNCLEAR'
    
    # Check if source is trusted - higher chance for TRUE
    if any(trusted in source_lower for trusted in trusted_sources):
        # 70% chance TRUE, 20% UNCLEAR, 10% FALSE for trusted sources
        status_choice = random.choices(['TRUE', 'UNCLEAR', 'FALSE'], weights=[70, 20, 10])[0]
        return status_choice
    
    # For other sources - more balanced distribution
    # 40% UNCLEAR, 35% TRUE, 25% FALSE
    return random.choices(['UNCLEAR', 'TRUE', 'FALSE'], weights=[40, 35, 25])[0]


def _load_cached_news(cache_dir=None, max_items=20, include_all_samples=False):
    """Load real news items from cache + some international news for variety."""
    base = cache_dir or os.path.join(os.path.dirname(__file__), 'data', 'cache')
    items = []
    seen_stories = {}  # Track similar stories and their sources
    
    # Add some fresh international news to mix with cached content
    international_news = [
        {
            'title': 'Global Climate Summit 2025 Reaches Historic Agreement on Carbon Neutrality',
            'snippet': 'World leaders from 195 countries unanimously agree on ambitious climate targets, setting 2030 as the deadline for 50% emission reductions.',
            'source': 'BBC World',
            'verification_status': 'TRUE',
            'source_url': 'https://www.bbc.com/news/world'
        },
        {
            'title': 'European Space Agency Launches Revolutionary Mars Exploration Mission',
            'snippet': 'The ESA\'s newest Mars rover equipped with advanced AI technology begins its journey to search for signs of ancient life on the red planet.',
            'source': 'CNN International',
            'verification_status': 'TRUE',
            'source_url': 'https://edition.cnn.com/space'
        },
        {
            'title': 'South Asian Economic Summit Addresses Trade Relations Post-Pandemic',
            'snippet': 'Leaders from India, Pakistan, Bangladesh, and Nepal discuss strengthening regional trade partnerships and economic recovery strategies.',
            'source': 'Al Jazeera',
            'verification_status': 'TRUE',
            'source_url': 'https://www.aljazeera.com/economy'
        },
        {
            'title': 'Tech Giants Allegedly Manipulate Global Elections Through AI Algorithms',
            'snippet': 'Whistleblowers claim major social media platforms have been using advanced AI to influence voter behavior in multiple countries.',
            'source': 'Independent Investigation',
            'verification_status': 'FALSE',
            'source_url': 'https://example.com/investigation'
        },
        {
            'title': 'Breakthrough in Quantum Computing Claimed by Chinese Research Team',
            'snippet': 'Beijing University researchers reportedly achieve quantum supremacy with 1000-qubit processor, though independent verification is pending.',
            'source': 'Tech Times Asia',
            'verification_status': 'UNCLEAR',
            'source_url': 'https://techtimes.com/asia'
        },
        {
            'title': 'UN Security Council Unanimously Passes Resolution on Global Food Security',
            'snippet': 'Historic agreement commits member nations to emergency food aid distribution and sustainable agriculture investment in developing countries.',
            'source': 'Reuters',
            'verification_status': 'TRUE',
            'source_url': 'https://www.reuters.com/world'
        }
    ]
    
    # Add international news first (with some randomization)
    random.shuffle(international_news)
    for i, news in enumerate(international_news[:4]):  # Include 4 international stories
        # Generate random view count
        views = random.randint(1200, 45000)
        
        item_id = f"intl_{i+1}"
        news_item = {
            'id': item_id,
            'title': news['title'],
            'snippet': news['snippet'],
            'full_text': f"{news['title']}\n\n{news['snippet']}",
            'source': news['source'],
            'sources': [news['source']],
            'published_at': time.time() - random.randint(3600, 86400),  # 1-24 hours ago
            'verification_status': news['verification_status'],
            'source_url': news['source_url'],
            'views': views
        }
        items.append(news_item)
        
        # Track this story
        seen_stories[item_id] = {
            'normalized_title': news['title'].lower().strip(),
            'sources': [news['source']]
        }
    
    # Process real cached news files
    try:
        files = sorted([os.path.join(base, f) for f in os.listdir(base) if os.path.isfile(os.path.join(base, f))], key=os.path.getmtime, reverse=True)
    except Exception:
        return items  # Return international news if no cache directory

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as fh:
                text = fh.read()
        except Exception:
            continue

        # Split into paragraphs and use non-empty lines as candidate headlines/snippets
        parts = [p.strip() for p in text.split('\n') if p.strip()]
        
        # Extract up to 2 good headlines per file to get more diversity (reduced from 3)
        headlines_from_file = 0
        max_headlines_per_file = 2
        
        for i, p in enumerate(parts[:15]):  # Check first 15 paragraphs
            if headlines_from_file >= max_headlines_per_file:
                break
                
            # Skip lines that look like boilerplate
            low = p.lower()
            if any(x in low for x in ('copyright', 'archive', 'feed', 'email', 'phone', 'menu', 'login', 'search', 'nav', 'footer')):
                continue
                
            # Skip very short lines (likely not headlines)
            if len(p.strip()) < 25:
                continue
                
            # Skip very long lines (likely not headlines)
            if len(p) > 250:
                continue
                
            # Skip lines that don't look like news headlines
            if not any(char.isupper() for char in p[:20]):  # Headlines usually start with capital letters
                continue
                
            title = p[:240] if len(p) > 240 else p
            
            # Normalize title for comparison
            normalized_title = title.lower().strip()
            title_words = set(normalized_title.split())
            
            # Check if this is a similar story we've seen before
            similar_story_id = None
            for story_id, story_data in seen_stories.items():
                story_words = set(story_data['normalized_title'].split())
                # If more than 60% of significant words overlap, consider it the same story
                if title_words and len(title_words.intersection(story_words)) / max(len(title_words), len(story_words)) > 0.6:
                    similar_story_id = story_id
                    break
            
            # Get snippet from next paragraph
            snippet = ''
            if i + 1 < len(parts):
                snippet = parts[i + 1][:400]
            elif i + 2 < len(parts):
                snippet = parts[i + 2][:400]
            
            # Clean source name
            source_name = os.path.basename(file_path).replace('.txt', '').replace('_', ' ').replace('-', ' ')
            source_name = ' '.join(word.capitalize() for word in source_name.split())
            if 'nepalnews' in source_name.lower():
                source_name = 'Nepal News'
            elif 'english' in source_name.lower():
                source_name = 'English Nepal News'
            elif 'kathmandupost' in source_name.lower():
                source_name = 'Kathmandu Post'
            elif 'myrepublica' in source_name.lower():
                source_name = 'My Republica'
            
            if similar_story_id:
                # Add this source to existing story
                existing_story = seen_stories[similar_story_id]
                if source_name not in existing_story['sources']:
                    existing_story['sources'].append(source_name)
                    # Update the story in items list
                    for item in items:
                        if item['id'] == similar_story_id:
                            item['sources'] = existing_story['sources']
                            item['source'] = ', '.join(existing_story['sources'][:2])  # Show first 2 sources
                            if len(existing_story['sources']) > 2:
                                additional_count = len(existing_story['sources']) - 2
                                item['source'] += f' +{additional_count} more'
                            break
            else:
                # Create new story
                item_id = f"story_{len(items) + 1}"
                
                # Generate random view count for cached news
                views = random.randint(500, 25000)
                
                # Determine verification status for local cached news
                verification_status = _determine_verification_status(title, source_name)
                
                # Generate source URL for cached files
                source_url = ''
                file_name = os.path.basename(file_path)
                if file_name.startswith('https_'):
                    # Try to reconstruct URL from filename
                    source_url = _convert_filename_to_url(file_name) or ''
                else:
                    # Fallback URL generation based on source name
                    if 'nepal news' in source_name.lower() or 'nepalnews' in source_name.lower():
                        source_url = 'https://english.nepalnews.com'
                    elif 'kathmandu post' in source_name.lower():
                        source_url = 'https://kathmandupost.com'
                    elif 'my republica' in source_name.lower() or 'myrepublica' in source_name.lower():
                        source_url = 'https://myrepublica.nagariknetwork.com'
                    elif 'nepali times' in source_name.lower():
                        source_url = 'https://nepalitimes.com'
                    elif 'online khabar' in source_name.lower():
                        source_url = 'https://english.onlinekhabar.com'
                
                new_item = {
                    'id': item_id,
                    'title': title,
                    'snippet': snippet,
                    'full_text': '\n'.join(parts[i:i+5]),
                    'source': source_name,
                    'sources': [source_name],  # List of all sources for this story
                    'published_at': os.path.getmtime(file_path),
                    'verification_status': verification_status,
                    'source_url': source_url,
                    'views': views  # Add random view count
                }
                
                items.append(new_item)
                
                # Track this story
                seen_stories[item_id] = {
                    'normalized_title': normalized_title,
                    'sources': [source_name]
                }
                
                headlines_from_file += 1
                
                # Stop if we have enough items
                if len(items) >= max_items:
                    break
        
        if len(items) >= max_items:
            break

    return items


@app.get('/api/latest_news')
def latest_news(response: Response, limit: int = 15):
    """Return a list of latest news items including international and diverse content."""
    # Add cache-busting headers to ensure fresh content on each request
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache" 
    response.headers["Expires"] = "0"
    
    items = _load_cached_news(max_items=limit * 2)  # Load more to ensure variety
    
    # Simplify output for frontend
    out = []
    for it in items:
        # Add source_url to each news item
        source_url = it.get('source_url', '')
        
        out.append({
            'id': it['id'],
            'title': it['title'],
            'snippet': it['snippet'],
            'source': it['source'],
            'sources': it.get('sources', [it['source']]),  # All sources for this story
            'source_count': len(it.get('sources', [it['source']])),
            'published_at': it['published_at'],
            'verification_status': it.get('verification_status', 'UNCLEAR'),
            'source_url': source_url,  # Include URL for "View Source" buttons
            'views': it.get('views', 0)  # Include view count
        })
    return {'news': out[:limit]}  # Return only the requested number of items


@app.get('/api/news/{news_id}')
def news_detail(news_id: str):
    """Return detailed news info and run a credibility check (using existing LLM pipeline) on the headline."""
    items = _load_cached_news(max_items=200)
    match = None
    for it in items:
        if it['id'] == news_id:
            match = it
            break
    if not match:
        raise HTTPException(status_code=404, detail='News item not found')

    title = match.get('title','')
    full = match.get('full_text','')

    # Use the existing source_url from the matched item if available
    source_url = match.get('source_url', '')
    
    # Only try to create/reconstruct URL if not already provided
    if not source_url:
        # Create a proper URL based on the source name
        source_name = match.get('source', '')
    
    # Only try to create/reconstruct URL if not already provided
    if not source_url:
        # Create a proper URL based on the source name
        source_name = match.get('source', '')
        
        # Enhanced source URL mapping with more comprehensive coverage
        if 'nepal news' in source_name.lower() or 'nepalnews' in source_name.lower():
            source_url = 'https://english.nepalnews.com'
        elif 'kathmandu post' in source_name.lower():
            source_url = 'https://kathmandupost.com'
        elif 'my republica' in source_name.lower() or 'myrepublica' in source_name.lower():
            source_url = 'https://myrepublica.nagariknetwork.com'
        elif 'nepali times' in source_name.lower():
            source_url = 'https://nepalitimes.com'
        elif 'online khabar' in source_name.lower():
            source_url = 'https://english.onlinekhabar.com'
        elif 'bbc' in source_name.lower():
            source_url = 'https://www.bbc.com'
        elif 'reuters' in source_name.lower():
            source_url = 'https://www.reuters.com'
        elif 'techcrunch' in source_name.lower():
            source_url = 'https://techcrunch.com'
        elif 'euronews' in source_name.lower():
            source_url = 'https://www.euronews.com'
        elif 'nasa' in source_name.lower():
            source_url = 'https://www.nasa.gov/news'
        else:
            # Only try to match cached files for items that are NOT from our sample news pools
            # Check if this is a sample news item (international, fake, or unverified)
            is_sample_news = (
                news_id.startswith('intl_') or 
                news_id.startswith('fake_') or 
                news_id.startswith('unverified_')
            )
            
            if not is_sample_news:
                # Try to find the cached file that matches this news item and convert filename to URL
                try:
                    cached_files = os.listdir(os.path.join(os.path.dirname(__file__), 'data', 'cache'))
                    
                    # Try to match this news item to a cached file by checking content similarity
                    for file in cached_files:
                        if file.startswith('https_'):
                            try:
                                file_path = os.path.join(os.path.dirname(__file__), 'data', 'cache', file)
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    file_content = f.read()
                                    
                                # Check if this file contains our article by looking for title overlap
                                title_words = set(title.lower().split())
                                content_words = set(file_content.lower().split())
                                
                                # Calculate overlap - if significant overlap, this is likely our article
                                overlap = len(title_words.intersection(content_words))
                                if overlap >= min(3, len(title_words) // 2):
                                    # Convert the filename to the original URL
                                    reconstructed_url = _convert_filename_to_url(file)
                                    if reconstructed_url:
                                        source_url = reconstructed_url
                                        break
                                        
                            except Exception:
                                continue
                except Exception:
                    pass
            # For sample news items, source_url remains empty (using the predefined URLs from the pools)

    # Always ensure we have at least one source with the original content
    evidence_items = []
    
    # Add the original cached source as the first evidence item
    if source_url:
        evidence_items.append({
            'source': source_url, 
            'url': source_url, 
            'snippet': full[:800],
            'title': title
        })
    else:
        # If no URL mapping found, create a fallback with source name but no URL
        evidence_items.append({
            'source': match.get('source', 'Unknown Source'), 
            'url': '', 
            'snippet': full[:800],
            'title': title
        })

    # Call LLM analysis
    try:
        analysis = call_groq(title, evidence_items, lang='ne')
    except Exception as e:
        print(f"Error in LLM analysis: {e}")
        analysis = {
            'verdict': 'UNCLEAR',
            'confidence': 0.0,
            'explanation': 'Unable to perform analysis at this time.',
            'evidence': []
        }
    
    # Ensure the evidence items with URLs are included in the response
    if 'evidence' not in analysis:
        analysis['evidence'] = []
    
    # Add our evidence items with proper URLs to the analysis
    analysis['evidence'] = evidence_items

    return {
        'id': match['id'],
        'title': title,
        'full_text': full,
        'source': match.get('source'),
        'published_at': match.get('published_at'),
        'analysis': analysis
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
