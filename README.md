# KrishiMitra AI (Capital-One-Agri)

Intelligent agricultural assistant: Next.js frontend + FastAPI backend + vector knowledge base + ML models.

---
## 1. Structure
```
Capital-One-Agri/
  agri-intelligence-backend/   # FastAPI API (auth, chat, RAG)
  frontend/                    # Next.js 15 UI (sessions, thinking animation)
  models/                      # ML / data assets
  start-platform.sh            # Convenience launcher
```

---
## 2. Prerequisites
| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Node.js | 18+ LTS |
| npm (or yarn) | latest |
| (Optional) OpenAI / HF key | for advanced LLM / embeddings |

---
## 3. Backend Setup
```bash
cd agri-intelligence-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # if present (else create)
# edit .env values (JWT_SECRET, DATABASE_URL, etc.)
uvicorn app.main:app --reload --port 8000
```
Visit: http://localhost:8000/docs for interactive API.

Minimal .env example:
```
APP_ENV=dev
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./agri_app.db
JWT_SECRET=change_me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CHROMA_DB_DIR=./agri_vectordb
OPENAI_API_KEY=
```
(Optional) ingest / prepare data before chatting:
```bash
python scripts/setup_vector_db.py        # if exists
python scripts/process_pdfs_only.py      # or ingestion script
```

---
## 4. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env 2>/dev/null || echo 'NEXT_PUBLIC_API_BASE=http://localhost:8000' > .env
npm run dev
```
Visit: http://localhost:3000

Key env var:
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

---
## 5. Using The App
1. Register a user (email + password).
2. Login – token stored (local storage / cookies depending on implementation).
3. Start typing a question; a chat session auto-creates on first send.
4. Observe multi-phase "thinking" progress bar.
5. View full response (no streaming).
6. Manage sessions in always-visible sidebar.

---
## 6. Development Commands
Backend:
```bash
ruff check .        # if configured
pytest -q           # run tests (if present)
```
Frontend:
```bash
npm run lint
npm run build
npm start           # production serve
```

---
## 7. Production Notes
| Aspect | Recommendation |
|--------|----------------|
| Backend run | uvicorn workers behind Nginx / Caddy |
| Frontend | `npm run build` then deploy (Vercel / container) |
| DB | Use PostgreSQL in production |
| Secrets | Strong JWT secret, rotate keys |
| Vector store | Persist `CHROMA_DB_DIR` volume |

---
## 8. Troubleshooting
| Issue | Fix |
|-------|-----|
| 401 Unauthorized | Re-login; check JWT_SECRET consistency |
| CORS error | Add frontend origin to FastAPI CORS middleware |
| Blank replies | Verify ingestion & API keys |
| Module not found | Activate venv / reinstall deps |
| Port busy | Change `PORT` or frontend dev port |

---
## 9. Extending
- Add answer streaming via SSE.
- Integrate real weather / market APIs.
- Add analytics & usage dashboards.
- Enhance prompt / retrieval strategies.

---
## 10. One-Line Dev Spin-Up (macOS / Linux)
```bash
( cd agri-intelligence-backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload ) & ( cd frontend && npm install && npm run dev )
```

---
## 11. Security Checklist
- Never commit real API keys.
- Restrict CORS origins.
- Rotate JWT secret periodically.
- Log authentication events.

---
## 12. Summary
KrishiMitra AI accelerates informed farming decisions with an intuitive UI, curated knowledge retrieval, and domain-focused AI reasoning.
