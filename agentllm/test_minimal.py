from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create minimal app
test_app = FastAPI(title='Test')

test_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClaimRequest(BaseModel):
    claim: str
    lang: str = 'ne'

@test_app.get('/')
def root():
    return {"status": "ok"}

@test_app.post('/api/verify_claim')
def verify_claim_test(req: ClaimRequest):
    return {
        "result": {
            "verdict": "TEST",
            "confidence": 1.0,
            "explanation": f"Testing claim: {req.claim}",
            "evidence": []
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(test_app, host="127.0.0.1", port=8001)
