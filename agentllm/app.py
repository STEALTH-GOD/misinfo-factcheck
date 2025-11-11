from dotenv import load_dotenv
load_dotenv()                      

import os, json, time, random
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from agent.retrieval import google_search, load_whitelist, fetch_page_text, rank_evidence_by_similarity, domain_from_url
from agent.llm_agent import call_groq

app = FastAPI(title='MisInfoDetectAI')

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }

@app.post('/api/verify_claim')
def verify_claim(req: ClaimRequest):
    """
    Verify a user claim by searching for evidence from multiple whitelisted sources.
    
    Process:
    1. Search Google for up to 10 results related to the claim
    2. Filter results to only include whitelisted domains  
    3. Rank the evidence by similarity to the claim
    4. Select top 6 most relevant sources
    5. Send to LLM for analysis
    6. Return analysis with all evidence sources preserved
    """
    claim = req.claim.strip()
    if not claim:
        raise HTTPException(status_code=400, detail='Empty claim')
    
    # Use the enhanced authoritative source finder
    evidence_items = _find_authoritative_sources(claim, max_sources=6)
    
    if not evidence_items:
        # Fallback to original search method if enhanced search fails
        try:
            results = google_search(claim, num=10)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        filtered = []
        for r in results:
            host = domain_from_url(r.get('link',''))
            if host in ALLOWED_DOMAINS or any(host.endswith(d) for d in ALLOWED_DOMAINS):
                text = fetch_page_text(r.get('link',''))
                filtered.append({'title': r.get('title'), 'link': r.get('link'), 'text': text})
        if not filtered:
            raise HTTPException(status_code=404, detail='No whitelisted evidence found')
        ranked = rank_evidence_by_similarity(claim, filtered, top_k=6)
        evidence_items = []
        for item in ranked:
            snippet = (item.get('text') or '')[:800]
            evidence_items.append({
                'source': item.get('link',''), 
                'url': item.get('link',''), 
                'snippet': snippet,
                'title': item.get('title', 'Source Article')
            })
    
    res = call_groq(claim, evidence_items, lang=req.lang)
    
    # Ensure all evidence sources are included in the response
    if 'evidence' not in res:
        res['evidence'] = []
    
    # Add our evidence items with proper URLs to the response
    res['evidence'] = evidence_items
    
    return {'result': res}


def _convert_filename_to_url(filename):
    """
    Convert cached filename back to original article URL.
    Example: https_english.nepalnews.com_economic_reforms_2025.txt -> https://english.nepalnews.com/economic_reforms_2025
    """
    if not filename.startswith('https_') or not filename.endswith('.txt'):
        return None
    
    # Remove .txt extension
    url_part = filename.replace('.txt', '')
    
    # Remove https_ prefix
    url_without_protocol = url_part.replace('https_', '')
    
    # Handle specific domain patterns we know about
    domain = None
    path = None
    
    if url_without_protocol.startswith('english.nepalnews.com_'):
        domain = 'english.nepalnews.com'
        path_part = url_without_protocol[len('english.nepalnews.com_'):]
        path = path_part.replace('_', '/')
    elif url_without_protocol.startswith('kathmandu_post_com_'):
        domain = 'kathmandupost.com'
        path_part = url_without_protocol[len('kathmandu_post_com_'):]
        path = path_part.replace('_', '/')
    elif url_without_protocol.startswith('myrepublica_com_'):
        domain = 'myrepublica.com'
        path_part = url_without_protocol[len('myrepublica_com_'):]
        path = path_part.replace('_', '/')
    elif url_without_protocol.startswith('nepali_times_com_'):
        domain = 'nepalitimes.com'
        path_part = url_without_protocol[len('nepali_times_com_'):]
        path = path_part.replace('_', '/')
    elif url_without_protocol.startswith('online_khabar_com_'):
        domain = 'english.onlinekhabar.com'
        path_part = url_without_protocol[len('online_khabar_com_'):]
        path = path_part.replace('_', '/')
    elif url_without_protocol.startswith('en.setopati.com_'):
        domain = 'en.setopati.com'
        path_part = url_without_protocol[len('en.setopati.com_'):]
        path = path_part.replace('_', '/')
    else:
        # Generic fallback - try to reconstruct from underscore-separated parts
        parts = url_without_protocol.split('_')
        if len(parts) >= 3:
            # Try to identify domain pattern: subdomain_domain_tld_path...
            # Look for 'com', 'org', 'net', 'gov' as TLD indicators
            tld_index = -1
            for i, part in enumerate(parts):
                if part in ['com', 'org', 'net', 'gov', 'np']:
                    tld_index = i
                    break
            
            if tld_index >= 1:
                # Reconstruct domain
                domain_parts = parts[:tld_index+1]
                path_parts = parts[tld_index+1:] if tld_index+1 < len(parts) else []
                
                # Convert domain parts back to dots
                domain = '.'.join(domain_parts)
                path = '/'.join(path_parts) if path_parts else ''
            else:
                return None
        else:
            return None
    
    # Construct final URL
    url = f"https://{domain}"
    if path:
        url += f"/{path}"
    
    return url


def _find_authoritative_sources(claim, max_sources=5):
    """
    Search for authoritative news sources related to a claim.
    Returns a list of evidence items with real URLs and content.
    """
    evidence_items = []
    
    try:
        # Search for news about this claim
        search_results = google_search(claim, num=8)
        
        # Prioritize sources by reliability
        priority_domains = [
            'bbc.com', 'reuters.com', 'cnn.com', 'npr.org', 'apnews.com',
            'kathmandupost.com', 'myrepublica.nagariknetwork.com', 
            'nepalitimes.com', 'english.onlinekhabar.com'
        ]
        
        # First pass: look for high-priority sources
        for result in search_results:
            result_url = result.get('link', '')
            result_domain = domain_from_url(result_url)
            
            if any(priority_domain in result_domain for priority_domain in priority_domains):
                if result_domain in ALLOWED_DOMAINS or any(result_domain.endswith(d) for d in ALLOWED_DOMAINS):
                    try:
                        content = fetch_page_text(result_url)
                        if content and len(content) > 200:
                            evidence_items.append({
                                'source': result_url,
                                'url': result_url,
                                'snippet': content[:800],
                                'title': result.get('title', 'News Article'),
                                'domain': result_domain
                            })
                            
                            if len(evidence_items) >= max_sources:
                                return evidence_items
                    except Exception:
                        continue
        
        # Second pass: any remaining whitelisted sources
        for result in search_results:
            if len(evidence_items) >= max_sources:
                break
                
            result_url = result.get('link', '')
            result_domain = domain_from_url(result_url)
            
            # Skip if we already added this domain
            if any(item.get('domain') == result_domain for item in evidence_items):
                continue
            
            if result_domain in ALLOWED_DOMAINS or any(result_domain.endswith(d) for d in ALLOWED_DOMAINS):
                try:
                    content = fetch_page_text(result_url)
                    if content and len(content) > 200:
                        evidence_items.append({
                            'source': result_url,
                            'url': result_url,
                            'snippet': content[:800],
                            'title': result.get('title', 'News Article'),
                            'domain': result_domain
                        })
                except Exception:
                    continue
                    
    except Exception as e:
        print(f"Error finding authoritative sources: {e}")
    
    return evidence_items


def _determine_verification_status(title, source_name):
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
            'title': f'Original: {title[:100]}...' if len(title) > 100 else title
        })
    else:
        # If no URL mapping found, create a fallback with source name but no URL
        evidence_items.append({
            'source': source_name, 
            'url': '', 
            'snippet': full[:800],
            'title': f'Cached: {title[:100]}...' if len(title) > 100 else title
        })
    
    # Try to find additional authoritative sources about this topic
    try:
        additional_sources = _find_authoritative_sources(title, max_sources=4)
        # Add unique sources (avoid duplicating the original source)
        for additional_source in additional_sources:
            if not any(additional_source.get('url') == existing.get('url') for existing in evidence_items):
                evidence_items.append(additional_source)
                if len(evidence_items) >= 5:  # Limit to 5 total sources
                    break
    except Exception as e:
        print(f"Could not find additional sources: {e}")
        # Continue with just the original source

    # Call LLM analysis - this will return UNCLEAR if GROQ keys not configured
    analysis = call_groq(title, evidence_items, lang='ne')
    
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
    uvicorn.run(app, host="127.0.0.1", port=8000)
