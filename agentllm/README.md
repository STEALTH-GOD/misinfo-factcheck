MisInfoDetectAI

Overview

- Google Custom Search (CSE) for retrieval (whitelisted domains)
- Page fetching + caching (newspaper3k)
- Reranking via sentence-transformers embeddings
- Groq API (Mixtral) as the single LLM provider
- FastAPI endpoint for frontend integration
- Docker + docker-compose for easy deployment

Setup

(Local)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Run:
uvicorn app:app --reload --port 8000

Testing

- tests/test_search_api.py # verifies Google CSE works
- tests/evaluate_age
