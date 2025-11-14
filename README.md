# MisInfo FactCheck Application

AI-powered fact-checking application for detecting and verifying misinformation in Nepali news.

## Features

- 🔍 Claim verification using multiple authoritative sources
- 📰 Latest news aggregation from trusted Nepali sources
- 🤖 AI-powered analysis using Groq LLM
- 🎯 Real-time fact-checking with evidence

## Tech Stack

- **Backend**: FastAPI, Python 3.11, Groq LLM
- **Frontend**: React, Tailwind CSS
- **Deployment**: Docker, Google Cloud Run
- **APIs**: Google Custom Search, Groq AI

## Local Development

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Setup

1. Clone the repository
```bash
git clone <your-repo-url>
cd misinfo-factcheck
```

2. Set up environment variables
```bash
# Backend
cp agentllm/.env.example agentllm/.env
# Edit agentllm/.env with your API keys

# Frontend
cp frontend/.env.example frontend/.env
```

3. Run with Docker Compose
```bash
docker-compose up --build
```

4. Access the application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development Mode

**Backend:**
```bash
cd agentllm
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

## Deployment to Google Cloud

See [deployment guide](./docs/DEPLOYMENT.md) for detailed instructions.

```bash
# Quick deploy
gcloud builds submit --config=cloudbuild.yaml .
```

## Project Structure

```
misinfo-factcheck/
├── agentllm/          # Backend FastAPI service
├── frontend/          # React frontend
├── docker-compose.yml # Local development orchestration
└── cloudbuild.yaml    # Google Cloud Build config
```

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

## License

MIT