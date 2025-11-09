import os, json, requests
seed = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'data', 'seed_dataset.json'), 'r', encoding='utf-8'))
def run_once(claim):
    url = f'http://localhost:{os.getenv("PORT","8000")}/api/verify_claim'
    try:
        r = requests.post(url, json={'claim': claim, 'lang':'ne'}, timeout=60)
        return r.json()
    except Exception as e:
        return {'error': str(e)}
def main():
    for rec in seed[:10]:
        print('---')
        print('Claim:', rec['claim_text'])
        out = run_once(rec['claim_text'])
        print('Output:', json.dumps(out, ensure_ascii=False, indent=2))
if __name__ == '__main__':
    main()
