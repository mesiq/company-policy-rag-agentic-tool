# Employee AI Portal

A local Flask and SQLite employee self-service demo with a browser UI and a separate command-line policy RAG tool.

## Setup (Windows)

In PowerShell from the project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DEMO_DEFAULT_PASSWORD` to the demo password shown on the login page, and set a persistent `FLASK_SECRET_KEY` in `.env`. Never commit `.env`. All seeded employees share the demo password; changing it does not update existing database credentials.

Start the web app:

```powershell
python app.py
```

Open <http://127.0.0.1:5000>. On first run, the app creates `employee.db` and seeds demo employees and leave balances if the employee table is empty.

## Policy RAG

The RAG tool is currently separate from the web app. It indexes `policies/leave_policy.pdf` and `policies/company_policy.pdf` into a local ChromaDB using CPU-based sentence-transformer embeddings. First ingestion may download the embedding model.

```powershell
python rag.py --ingest
python rag.py --ask "What is the annual leave policy?"
python rag.py --ask "What are work from home rules?" --category company
python rag.py --test
```

Semantic search needs no LLM key. To generate cited answers, add either `GROQ_API_KEY` or `GEMINI_API_KEY` to `.env`, then run:

```powershell
python rag.py --answer "How much annual leave is available?" --provider groq
```

Use `--provider gemini` to select Gemini. RAG is not connected to the browser chat or Flask API.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Portal page |
| GET | `/api/health` | Flask/SQLite health check |
| POST | `/api/login` | Sign in with JSON `employee_id` and `password` |
| GET | `/api/me` | Current employee profile (session required) |
| GET | `/api/leave-balance?year=YYYY` | Leave balances (session required; year optional) |
| POST | `/api/logout` | Sign out |

## Current scope

- The web chat uses simple keyword matching; it only retrieves profiles and leave balances.
- Policy search and answers are CLI-only. Leave applications and HR-ticket workflows are not implemented.
- The HR-admin role is stored but does not grant separate permissions.
- This is a local demo. The Flask server runs in debug mode; do not deploy it as-is.

## Main files

- `app.py` — Flask app and API
- `database.py` — SQLite schema, demo data, and database functions
- `rag.py` — PDF ingestion, semantic search, and optional LLM answers
- `policies/` — Source policy PDFs
- `templates/index.html` — Browser UI
- `requirements.txt` — Python dependencies
