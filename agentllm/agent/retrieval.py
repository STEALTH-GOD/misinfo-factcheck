import os, requests, json, time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = Path(os.getenv('CACHE_DIR', BASE_DIR / 'data' / 'cache'))
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Don't import or load model here - do it in a function
MODEL = None

def _get_model():
    """Load model only when needed"""
    global MODEL
    if MODEL is None:
        from sentence_transformers import SentenceTransformer
        MODEL = SentenceTransformer('all-MiniLM-L6-v2')  # Smaller model
    return MODEL

def domain_from_url(url):
    try:
        return urlparse(url).netloc
    except:
        return ''

def load_whitelist(path=BASE_DIR / 'data' / 'curated_sources.json'):
    if not os.path.exists(path):
        return set()
    with open(path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    domains = set()
    for key in ('nepali_news_sources','fact_checking_sources','government_sources'):
        for s in cfg.get(key, []):
            host = s.get('base_url','').replace('http://','').replace('https://','').split('/')[0]
            domains.add(host)
    return domains

def google_search(query, num=8):
    key = os.getenv('GOOGLE_CSE_API_KEY','')
    cse = os.getenv('GOOGLE_CSE_ID','')
    if not key or not cse:
        raise RuntimeError('Missing GOOGLE_CSE_API_KEY or GOOGLE_CSE_ID in env')
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {'q': query, 'cx': cse, 'key': key, 'num': num}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    items = data.get('items', [])
    results = []
    for it in items:
        results.append({
            'title': it.get('title'),
            'link': it.get('link'),
            'snippet': it.get('snippet','')
        })
    return results

def fetch_page_text(url):
    safe_name = url.replace('://','_').replace('/','_')
    cache_file = CACHE_DIR / (safe_name + '.txt')
    if cache_file.exists():
        return cache_file.read_text(encoding='utf-8')
    try:
        r = requests.get(url, timeout=10, headers={'User-Agent':'MisInfoDetectAI/1.0'})
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        for s in soup(['script','style','noscript']):
            s.decompose()
        text = '\n'.join([p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()])
        cache_file.write_text(text, encoding='utf-8')
        return text
    except Exception as e:
        return ''

def rank_evidence_by_similarity(claim, candidates, top_k=5):
    if not candidates:
        return []
    
    model = _get_model()  # Load model when this function is called
    claim_emb = model.encode([claim], convert_to_numpy=True)[0]
    texts = [c.get('text','')[:10000] for c in candidates]
    embeddings = model.encode(texts, convert_to_numpy=True)
    sims = []
    for idx, emb in enumerate(embeddings):
        score = float(np.dot(claim_emb, emb) / (np.linalg.norm(claim_emb) * np.linalg.norm(emb) + 1e-12))
        sims.append((score, candidates[idx]))
    sims.sort(key=lambda x: x[0], reverse=True)
    return [c for s,c in sims[:top_k]]