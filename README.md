# Employee AI Portal

A local Flask and SQLite employee self-service demo with a browser UI and a policy RAG tool available in both the portal chat and command line.

## Setup (Windows)

In PowerShell from the project folder:

```powershell
winget install --exact --id Python.Python.3.12
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If `py` is not available after installation, close and reopen PowerShell, then run the commands again.

In `.env`, set `DEMO_DEFAULT_PASSWORD` to `Demo@12345` to use the credentials shown on the login page (`EMP1001 / Demo@12345`), and replace `FLASK_SECRET_KEY` with a persistent random secret. Never commit `.env`. All seeded employees share the demo password; changing it after the database has been seeded does not update existing database credentials.

Start the web app:

```powershell
python app.py
```

Open <http://127.0.0.1:5000>. On first run, the app creates `employee.db` and seeds demo employees and leave balances if the employee table is empty.

## Policy RAG

The RAG tool indexes `policies/leave_policy.pdf` and `policies/company_policy.pdf` into a local ChromaDB using CPU-based sentence-transformer embeddings. Before using policy questions in the portal, create the index once:

```powershell
python rag.py --ingest
```

First ingestion may download the embedding model. After indexing, sign in to the portal and ask policy questions in the chat. Without an LLM provider configured, the app returns relevant passages and citations.

To generate concise answers, add the API key for your chosen provider to `.env` and set `LLM_PROVIDER` to `groq` or `gemini`:

```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
```

Or, to use Groq:

```dotenv
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key
```

The portal uses only the provider named by `LLM_PROVIDER`; the API key for that provider must be set. If `LLM_PROVIDER` is missing or is not `groq` or `gemini`, the portal falls back to retrieval-only answers. The agent CLI uses `LLM_PROVIDER` as its default provider (`gemini` when unset), and `--provider` overrides it. Set `GEMINI_MODEL` and `GROQ_MODEL` to override the default model IDs (`gemini-3.1-flash-lite` and `openai/gpt-oss-20b`).

The CLI can also be used directly:

```powershell
python rag.py --ask "What is the annual leave policy?"
python rag.py --ask "What are work from home rules?" --category company
python rag.py --test
```

To generate a cited CLI answer:

```powershell
python rag.py --answer "How much annual leave is available?" --provider groq
```

Use `--provider gemini` to select Gemini in the CLI.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Portal page |
| GET | `/api/health` | Flask/SQLite health check |
| POST | `/api/login` | Sign in with JSON `employee_id` and `password` |
| GET | `/api/me` | Current employee profile (session required) |
| GET | `/api/leave-balance?year=YYYY` | Leave balances (session required; year optional) |
| POST | `/api/policy-answer` | Answer a policy question (session required; JSON `question`) |
| POST | `/api/logout` | Sign out |

## Current scope

- The web chat uses simple keyword matching for employee profile and leave-balance requests; policy questions use the RAG index.
- Leave applications and HR-ticket workflows are not implemented.
- The HR-admin role is stored but does not grant separate permissions.
- This is a local demo. The Flask server runs in debug mode; do not deploy it as-is.

## Main files

- `app.py` — Flask app and API
- `database.py` — SQLite schema, demo data, and database functions
- `rag.py` — PDF ingestion, semantic search, and optional LLM answers
- `policies/` — Source policy PDFs
- `templates/index.html` — Browser UI
- `requirements.txt` — Python dependencies
