from dotenv import load_dotenv
load_dotenv()

from agent.retrieval import google_search

print('Testing Google Search API...')
try:
    results = google_search('Nepal climate change', num=3)
    print(f'\n✓ Found {len(results)} results:')
    for i, r in enumerate(results, 1):
        print(f'{i}. {r.get("title")}')
        print(f'   URL: {r.get("link")}')
except Exception as e:
    print(f'✗ Error: {e}')
