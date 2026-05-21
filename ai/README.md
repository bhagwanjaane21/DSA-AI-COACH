# AI DSA Coach — Intelligence Layer

AI microservice that powers the DSA Coach app with Gemini-based roadmap generation, code review, revision recommendations, and workload adaptation.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file with your Gemini API key
# Get a key from https://aistudio.google.com/apikey
GEMINI_API_KEY=your_key_here

# 3. Start the server
python main.py
```

Server runs at **http://localhost:8000**

Swagger docs at **http://localhost:8000/docs**

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/roadmap` | Generate weekly study plan |
| `POST` | `/api/review-code` | Analyze code submission |
| `POST` | `/api/recommend-revision` | Get concept-based revision suggestion |
| `POST` | `/api/adjust-workload` | Adapt plan for schedule changes |

## Tech Stack

- **FastAPI** — API framework
- **Google Gemini 2.5 Flash** — LLM (via `google-genai` SDK)
- **Pydantic** — Structured I/O validation
