from dotenv import load_dotenv
load_dotenv()                      

import os, json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    claim = req.claim.strip()
    if not claim:
        raise HTTPException(status_code=400, detail='Empty claim')
    try:
        results = google_search(claim, num=8)
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
    ranked = rank_evidence_by_similarity(claim, filtered, top_k=5)
    evidence_items = []
    for item in ranked:
        snippet = (item.get('text') or '')[:800]
        evidence_items.append({'source': item.get('link',''), 'url': item.get('link',''), 'snippet': snippet})
    res = call_groq(claim, evidence_items, lang=req.lang)
    return {'result': res}


def _load_cached_news(cache_dir=None, max_items=20):
    """Load simple news items from text cache files. Returns list of dicts with id, title, snippet, full_text, source, published_at."""
    base = cache_dir or os.path.join(os.path.dirname(__file__), 'data', 'cache')
    items = []
    try:
        files = sorted([os.path.join(base, f) for f in os.listdir(base) if os.path.isfile(os.path.join(base, f))], key=os.path.getmtime, reverse=True)
    except Exception:
        return []

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as fh:
                text = fh.read()
        except Exception:
            continue

        # Split into paragraphs and use non-empty lines as candidate headlines/snippets
        parts = [p.strip() for p in text.split('\n') if p.strip()]
        # Heuristic: first meaningful lines (skip copyright/footer lines)
        for i, p in enumerate(parts[:50]):
            # skip lines that look like boilerplate
            low = p.lower()
            if any(x in low for x in ('copyright', 'archive', 'feed', 'email', 'phone')):
                continue
            title = p if len(p) < 240 else p[:240]
            snippet = (parts[i+1] if i+1 < len(parts) else '')
            item_id = f"{os.path.basename(file_path)}::{i}"
            items.append({
                'id': item_id,
                'title': title,
                'snippet': snippet[:400],
                'full_text': '\n'.join(parts[i:i+6]),
                'source': os.path.basename(file_path),
                'published_at': os.path.getmtime(file_path)
            })
            if len(items) >= max_items:
                break
        if len(items) >= max_items:
            break

    return items


@app.get('/api/latest_news')
def latest_news(limit: int = 10):
    """Return a list of latest news items parsed from cached text files."""
    items = _load_cached_news(max_items=limit)
    # Simplify output for frontend
    out = []
    for it in items:
        out.append({
            'id': it['id'],
            'title': it['title'],
            'snippet': it['snippet'],
            'source': it['source'],
            'published_at': it['published_at']
        })
    return {'news': out}


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

    # Prepare a minimal evidence item (cached text as evidence)
    evidence_items = [{'source': match.get('source',''), 'url': '', 'snippet': full[:800]}]

    # Call LLM analysis - this will return UNCLEAR if GROQ keys not configured
    analysis = call_groq(title, evidence_items, lang='ne')

    return {
        'id': match['id'],
        'title': title,
        'full_text': full,
        'source': match.get('source'),
        'published_at': match.get('published_at'),
        'analysis': analysis
    }
