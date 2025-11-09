from dotenv import load_dotenv
load_dotenv()                      

import os, json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.retrieval import google_search, load_whitelist, fetch_page_text, rank_evidence_by_similarity, domain_from_url
from agent.llm_agent import call_groq

app = FastAPI(title='MisInfoDetectAI')

WHITELIST = load_whitelist()
ALLOWED_DOMAINS = set(os.getenv('ALLOWED_SOURCES','').split(',')) if os.getenv('ALLOWED_SOURCES') else WHITELIST

class ClaimRequest(BaseModel):
    claim: str
    lang: str = 'ne'

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
