import os
from agent.retrieval import google_search
def run():
    try:
        res = google_search('काठमाडौंमा भूकम्प', num=3)
        print('Found', len(res), 'results')
        for r in res:
            print(r.get('title'), '-', r.get('link'))
    except Exception as e:
        print('Error:', e)
if __name__ == '__main__':
    run()
