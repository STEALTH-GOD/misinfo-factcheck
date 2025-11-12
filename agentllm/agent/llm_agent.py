import os, requests, json, re

GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'

SYSTEM_PROMPT = open(os.path.join(os.path.dirname(__file__), 'prompts', 'system_prompt.txt'), 'r', encoding='utf-8').read()
CLASSIFY_PROMPT = open(os.path.join(os.path.dirname(__file__), 'prompts', 'classify_prompt.txt'), 'r', encoding='utf-8').read()

def build_messages(claim, evidence_items, lang='ne'):
    evidence_block = []
    for idx, e in enumerate(evidence_items, start=1):
        src = e.get('source') or e.get('url') or ''
        snippet = e.get('snippet','').replace('\n',' ')
        evidence_block.append(f"{idx}) {src} | {snippet}")
    user_text = CLASSIFY_PROMPT.replace('{CLAIM_TEXT}', claim).replace('{EVIDENCE_BLOCK}', '\n'.join(evidence_block)).replace('{LANG}', lang)
    messages = [
        {'role':'system', 'content': SYSTEM_PROMPT},
        {'role':'user', 'content': user_text}
    ]
    return messages

def call_groq(claim, evidence_items, lang='ne', model=None):
    GROQ_KEY = os.getenv('GROQ_API_KEY','')
    GROQ_MODEL = model or os.getenv('GROQ_MODEL', None)
    if not GROQ_KEY:
        return {'verdict':'UNCLEAR','confidence':0,'explanation':'GROQ_API_KEY not set','evidence': []}
    if not GROQ_MODEL:
        return {'verdict':'UNCLEAR','confidence':0,'explanation':'GROQ_MODEL not configured in .env','evidence': []}

    payload = {
        'model': GROQ_MODEL,
        'messages': build_messages(claim, evidence_items, lang),
        'max_tokens': 512,
        'temperature': 0.0
    }
    headers = {'Authorization': f'Bearer {GROQ_KEY}', 'Content-Type': 'application/json'}
    try:
        r = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
    except Exception as e:
        return {'verdict':'UNCLEAR','confidence':0,'explanation':f'Network error calling Groq: {e}','evidence': []}

    if r.status_code != 200:
        text = r.text
        return {'verdict':'UNCLEAR','confidence':0,'explanation':f'Groq API error: {r.status_code} {text}','evidence': []}

    data = r.json()
    try:
        text = data['choices'][0]['message']['content']
    except Exception:
        text = r.text

    # Try to parse JSON response the model is instructed to return
    try:
        return json.loads(text.strip())
    except Exception:
        m = re.search(r'\{.*\}', text, flags=re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except:
                pass
        return {'verdict':'UNCLEAR','confidence':0,'explanation':'LLM response parse failed','raw': text}
