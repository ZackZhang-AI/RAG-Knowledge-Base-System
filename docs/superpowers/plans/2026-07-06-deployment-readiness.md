# RAG Demo Deployment Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare this RAG PDF system for a controlled public demo deployment suitable for internship/job applications.

**Architecture:** Deploy the frontend as static assets behind Nginx, proxy `/api` to FastAPI, and keep Milvus, MinIO, Redis, RabbitMQ, and Celery on an internal Docker network. Expose only HTTPS to the public internet, use a demo account with limited capabilities, and keep all infrastructure consoles private.

**Tech Stack:** Vue 3 + Vite, FastAPI, SQLAlchemy/SQLite or managed PostgreSQL later, Celery, RabbitMQ, Redis, MinIO, Milvus, Docker Compose, Nginx, DashScope/Qwen.

---

## Deployment Scope

Recommended target: **controlled demo deployment**, not open production.

Publicly exposed:
- Frontend site: `https://your-domain.example`
- Backend API through Nginx: `https://your-domain.example/api/v1/*`

Private only:
- FastAPI direct port `8000`
- MinIO console `9001`
- MinIO API `9000`
- RabbitMQ `5672` and `15672`
- Redis `6379`
- Milvus `19530` and `9091`
- Flower `5555`

Demo limits:
- One seeded demo user
- Registration disabled or invite-only
- Upload size limited
- File types limited to safe demo formats
- LLM usage guarded by rate limits and daily budget
- Demo documents contain no personal or confidential data

## File Structure To Prepare

- Modify: `src/settings.py`  
  Add production-safe environment variables for CORS, debug mode, registration, upload limits, API rate limits, and service credentials.

- Modify: `src/main.py`  
  Replace wildcard CORS with configured origins and disable debug behavior in production.

- Modify: `src/api/routers/auth.py`  
  Add registration toggle so public visitors cannot create unlimited accounts.

- Modify: `src/api/routers/loadfile.py`, `src/api/routers/storage.py`, `src/api/routers/query.py`  
  Require authentication and apply upload/query limits.

- Create: `.env.production.example`  
  Document all required deployment variables without real secrets.

- Create: `docker/docker-compose.prod.yml`  
  Production-oriented compose file with internal-only service ports.

- Create: `docker/nginx.conf`  
  Serve frontend assets and reverse proxy API requests.

- Create: `scripts/create_demo_user.py`  
  Seed a single demo user for portfolio reviewers.

- Create: `docs/deployment-demo.md`  
  Human-readable deployment and rollback guide.

- Create: `docs/demo-script.md`  
  Interview/demo walkthrough: what to click, what to explain, and what technical points to highlight.

---

### Task 1: Decide Demo Deployment Policy

**Files:**
- Create: `docs/deployment-demo.md`

- [ ] **Step 1: Write the deployment policy section**

Add this section to `docs/deployment-demo.md`:

```markdown
# RAG PDF System Demo Deployment

## Deployment Goal

This deployment is a controlled portfolio demo for internship/job applications. It is not an open production SaaS.

## Public Surface

- Public frontend: `https://your-domain.example`
- Public API: proxied under `/api/v1`

## Private Surface

The following services must not be reachable from the public internet:

- FastAPI direct port `8000`
- MinIO `9000`, `9001`
- RabbitMQ `5672`, `15672`
- Redis `6379`
- Milvus `19530`, `9091`
- Flower `5555`

## Demo Constraints

- Disable public registration.
- Provide one demo account.
- Use only non-sensitive sample documents.
- Limit uploads to `10 MB`.
- Allow only `.pdf`, `.txt`, `.md`, `.docx`.
- Keep DashScope API keys in server-side environment variables only.
- Rotate the demo password after sharing it widely.
```

- [ ] **Step 2: Commit the policy document**

Run:

```bash
git add docs/deployment-demo.md
git commit -m "docs: define demo deployment policy"
```

Expected: commit succeeds with only documentation changes.

---

### Task 2: Create Production Environment Template

**Files:**
- Create: `.env.production.example`

- [ ] **Step 1: Add production environment template**

Create `.env.production.example` with:

```dotenv
APP_NAME=RAG-PDF-System
APP_ENV=production
DEBUG=False
API_PREFIX=/api/v1

SECRET_KEY=replace-with-64-random-characters
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOW_REGISTRATION=False
BACKEND_CORS_ORIGINS=https://your-domain.example

DASHSCOPE_API_KEY=replace-with-real-key-on-server
LLM_MODEL=qwen-max
EMBEDDING_MODEL=text-embedding-v1

MAX_UPLOAD_SIZE_MB=10
ALLOWED_UPLOAD_EXTENSIONS=.pdf,.txt,.md,.docx
MAX_QUERY_LENGTH=1000
DAILY_QUERY_LIMIT_PER_USER=50

MILVUS_HOST=milvus-standalone
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=rag_documents_demo
MILVUS_DIMENSION=1536

REDIS_URL=redis://redis:6379/0
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=rag_user
RABBITMQ_PASSWORD=replace-with-strong-password

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=replace-with-strong-access-key
MINIO_SECRET_KEY=replace-with-strong-secret-key
MINIO_BUCKET_NAME=rag-documents-demo
MINIO_SECURE=False

DATABASE_URL=sqlite:///./data/rag_system.db

CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=20
ENABLE_RERANK=True
RERANK_MODEL=gte-rerank
RERANK_TOP_N=5
ENABLE_MULTI_HOP=True
MAX_HOP=3
SHORT_TERM_MEMORY_TTL=3600
LONG_TERM_MEMORY_COLLECTION=user_memory
MEMORY_HISTORY_LIMIT=10
```

- [ ] **Step 2: Verify real secrets are not committed**

Run:

```bash
git diff -- .env.production.example
```

Expected: file contains only placeholders, no real API key, no real password.

- [ ] **Step 3: Commit**

Run:

```bash
git add .env.production.example
git commit -m "chore: add production environment template"
```

---

### Task 3: Harden Runtime Settings

**Files:**
- Modify: `src/settings.py`

- [ ] **Step 1: Add production settings fields**

In `src/settings.py`, add these fields to `Settings`:

```python
from typing import List, Optional

BACKEND_CORS_ORIGINS: str = "http://localhost:5173"
ALLOW_REGISTRATION: bool = True
MAX_UPLOAD_SIZE_MB: int = 10
ALLOWED_UPLOAD_EXTENSIONS: str = ".pdf,.txt,.md,.docx"
MAX_QUERY_LENGTH: int = 1000
DAILY_QUERY_LIMIT_PER_USER: int = 50

@property
def cors_origins(self) -> List[str]:
    return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

@property
def allowed_upload_extensions(self) -> set[str]:
    return {ext.strip().lower() for ext in self.ALLOWED_UPLOAD_EXTENSIONS.split(",") if ext.strip()}

@property
def max_upload_size_bytes(self) -> int:
    return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024
```

- [ ] **Step 2: Run import check**

Run:

```bash
python -c "from src.settings import settings; print(settings.cors_origins); print(settings.max_upload_size_bytes)"
```

Expected: prints a list of origins and `10485760` when `MAX_UPLOAD_SIZE_MB=10`.

- [ ] **Step 3: Commit**

Run:

```bash
git add src/settings.py
git commit -m "chore: add production runtime settings"
```

---

### Task 4: Replace Wildcard CORS

**Files:**
- Modify: `src/main.py`

- [ ] **Step 1: Update CORS middleware**

Replace:

```python
allow_origins=["*"],
```

with:

```python
allow_origins=settings.cors_origins,
```

- [ ] **Step 2: Verify app imports**

Run:

```bash
python -c "from src.main import app; print(app.title)"
```

Expected: prints `RAG-PDF-System`.

- [ ] **Step 3: Commit**

Run:

```bash
git add src/main.py
git commit -m "fix: restrict cors origins"
```

---

### Task 5: Disable Public Registration For Demo

**Files:**
- Modify: `src/api/routers/auth.py`

- [ ] **Step 1: Guard the register endpoint**

At the start of `register`, add:

```python
if not settings.ALLOW_REGISTRATION:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Public registration is disabled for this demo.",
    )
```

- [ ] **Step 2: Verify syntax**

Run:

```bash
python -m py_compile src/api/routers/auth.py
```

Expected: no output and exit code `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add src/api/routers/auth.py
git commit -m "fix: allow disabling public registration"
```

---

### Task 6: Protect Risky API Endpoints

**Files:**
- Modify: `src/api/routers/loadfile.py`
- Modify: `src/api/routers/storage.py`
- Modify: `src/api/routers/query.py`

- [ ] **Step 1: Add authentication imports**

For each router that currently lacks authentication, add:

```python
from src.api.dependencies import get_current_user
from src.database.models import User
```

- [ ] **Step 2: Require current user on upload, storage, and query routes**

Add this parameter to each public route function:

```python
current_user: User = Depends(get_current_user)
```

Keep existing `db: Session = Depends(get_db)` parameters unchanged.

- [ ] **Step 3: Verify route modules compile**

Run:

```bash
python -m py_compile src/api/routers/loadfile.py src/api/routers/storage.py src/api/routers/query.py
```

Expected: no output and exit code `0`.

- [ ] **Step 4: Commit**

Run:

```bash
git add src/api/routers/loadfile.py src/api/routers/storage.py src/api/routers/query.py
git commit -m "fix: require auth for risky demo endpoints"
```

---

### Task 7: Add Upload And Query Limits

**Files:**
- Modify: `src/api/routers/loadfile.py`
- Modify: `src/api/routers/storage.py`
- Modify: `src/api/routers/query.py`

- [ ] **Step 1: Validate upload extension**

Before saving uploaded files, check:

```python
suffix = Path(file.filename or "").suffix.lower()
if suffix not in settings.allowed_upload_extensions:
    raise HTTPException(
        status_code=400,
        detail=f"Unsupported file type: {suffix}",
    )
```

- [ ] **Step 2: Validate upload size**

After reading upload bytes or before writing to disk when size is available, check:

```python
if len(content) > settings.max_upload_size_bytes:
    raise HTTPException(
        status_code=413,
        detail=f"File is larger than {settings.MAX_UPLOAD_SIZE_MB} MB.",
    )
```

- [ ] **Step 3: Validate query length**

Before calling retrieval or LLM services, check:

```python
if len(request.query.strip()) > settings.MAX_QUERY_LENGTH:
    raise HTTPException(
        status_code=400,
        detail=f"Query is longer than {settings.MAX_QUERY_LENGTH} characters.",
    )
```

- [ ] **Step 4: Verify syntax**

Run:

```bash
python -m py_compile src/api/routers/loadfile.py src/api/routers/storage.py src/api/routers/query.py
```

Expected: no output and exit code `0`.

- [ ] **Step 5: Commit**

Run:

```bash
git add src/api/routers/loadfile.py src/api/routers/storage.py src/api/routers/query.py
git commit -m "fix: add demo upload and query limits"
```

---

### Task 8: Create Production Docker Compose

**Files:**
- Create: `docker/docker-compose.prod.yml`

- [ ] **Step 1: Add production compose file**

Create `docker/docker-compose.prod.yml` with these principles:

```yaml
version: "3.8"

services:
  app:
    build:
      context: ../
      dockerfile: docker/Dockerfile
    env_file:
      - ../.env.production
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000
    expose:
      - "8000"
    volumes:
      - ../data:/app/data
      - ../logs:/app/logs
    depends_on:
      - milvus-standalone
      - redis
      - rabbitmq
      - minio
    networks:
      - rag_net

  worker:
    build:
      context: ../
      dockerfile: docker/Dockerfile
    env_file:
      - ../.env.production
    command: celery -A src.worker.celery_app worker --loglevel=info
    volumes:
      - ../data:/app/data
      - ../logs:/app/logs
    depends_on:
      - rabbitmq
      - redis
      - milvus-standalone
      - minio
    networks:
      - rag_net

  nginx:
    image: nginx:1.27-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ../frontend/dist:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./certbot/www:/var/www/certbot
      - ./certbot/conf:/etc/letsencrypt
    depends_on:
      - app
    networks:
      - rag_net

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    expose:
      - "5672"
    networks:
      - rag_net

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    expose:
      - "6379"
    networks:
      - rag_net

  minio:
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
    command: minio server /minio_data --console-address ":9001"
    volumes:
      - minio_data:/minio_data
    expose:
      - "9000"
      - "9001"
    networks:
      - rag_net

  etcd:
    image: quay.io/coreos/etcd:v3.5.5
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
      - ETCD_SNAPSHOT_COUNT=50000
    volumes:
      - milvus_etcd_data:/etcd
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls=http://0.0.0.0:2379 --data-dir /etcd
    networks:
      - rag_net

  milvus-standalone:
    image: milvusdb/milvus:v2.3.4
    command: ["milvus", "run", "standalone"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
      MINIO_ACCESS_KEY_ID: ${MINIO_ACCESS_KEY}
      MINIO_SECRET_ACCESS_KEY: ${MINIO_SECRET_KEY}
    volumes:
      - milvus_data:/var/lib/milvus
    expose:
      - "19530"
      - "9091"
    depends_on:
      - etcd
      - minio
    networks:
      - rag_net

networks:
  rag_net:
    driver: bridge

volumes:
  milvus_etcd_data:
  milvus_data:
  minio_data:
  redis_data:
  rabbitmq_data:
```

- [ ] **Step 2: Validate compose config**

Run:

```bash
docker compose -f docker/docker-compose.prod.yml --env-file .env.production.example config
```

Expected: Docker renders the config without YAML errors.

- [ ] **Step 3: Commit**

Run:

```bash
git add docker/docker-compose.prod.yml
git commit -m "chore: add production compose file"
```

---

### Task 9: Add Nginx Reverse Proxy

**Files:**
- Create: `docker/nginx.conf`

- [ ] **Step 1: Add Nginx config**

Create `docker/nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;

    client_max_body_size 10m;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://app:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }
}
```

- [ ] **Step 2: Validate Nginx config in container**

Run:

```bash
docker run --rm -v "${PWD}/docker/nginx.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.27-alpine nginx -t
```

Expected: output includes `syntax is ok` and `test is successful`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docker/nginx.conf
git commit -m "chore: add nginx reverse proxy config"
```

---

### Task 10: Build Frontend For Production

**Files:**
- Verify: `frontend/package.json`
- Verify: `frontend/src/api/index.js`

- [ ] **Step 1: Confirm frontend uses same-origin API**

`frontend/src/api/index.js` should keep:

```js
const api = axios.create({
  baseURL: '/api/v1',
})
```

- [ ] **Step 2: Build frontend**

Run:

```bash
cd frontend
npm run build
```

Expected: Vite creates `frontend/dist`.

- [ ] **Step 3: Commit only source/config changes**

Run:

```bash
git status --short
```

Expected: do not commit `frontend/dist` unless the deployment strategy intentionally serves committed static files.

---

### Task 11: Seed Demo User

**Files:**
- Create: `scripts/create_demo_user.py`

- [ ] **Step 1: Create seed script**

Create `scripts/create_demo_user.py`:

```python
import os

from src.database.sql_session import SessionLocal, Base, engine
from src.database.models import User
from src.utils.security import get_password_hash


def main() -> None:
    username = os.getenv("DEMO_USERNAME", "demo")
    email = os.getenv("DEMO_EMAIL", "demo@example.com")
    password = os.getenv("DEMO_PASSWORD")

    if not password:
        raise RuntimeError("Set DEMO_PASSWORD before creating the demo user.")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.email = email
            user.password_hash = get_password_hash(password)
            user.is_active = True
            print(f"Updated demo user: {username}")
        else:
            db.add(
                User(
                    username=username,
                    email=email,
                    password_hash=get_password_hash(password),
                    is_active=True,
                )
            )
            print(f"Created demo user: {username}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run locally with a temporary password**

Run:

```bash
$env:DEMO_PASSWORD="change-me-locally"
python scripts/create_demo_user.py
```

Expected: prints `Created demo user: demo` or `Updated demo user: demo`.

- [ ] **Step 3: Commit**

Run:

```bash
git add scripts/create_demo_user.py
git commit -m "chore: add demo user seed script"
```

---

### Task 12: Prepare Demo Data

**Files:**
- Create: `docs/demo-script.md`

- [ ] **Step 1: Select safe documents**

Use only documents that meet all criteria:

```text
- No private personal information
- No company confidential information
- No paid or copyrighted textbook excerpts
- Small enough to process quickly
- Good enough to demonstrate citation and retrieval
```

- [ ] **Step 2: Write the demo walkthrough**

Create `docs/demo-script.md`:

```markdown
# Demo Script

## Login

- Open `https://your-domain.example`
- Login with the shared demo account.

## Knowledge Base

- Create or open the demo knowledge base.
- Upload one safe PDF or use the preloaded sample.
- Wait for processing to finish.

## Chat

Ask:

> Summarize the document in three points and cite the source pages.

Then ask:

> Compare two sections of the document and explain the difference.

## Evaluation

- Generate QA pairs for the demo document.
- Run evaluation.
- Show faithfulness, relevance, and recall-style metrics.

## Interview Talking Points

- Document parsing and chunking strategy
- Embedding and vector retrieval
- Reranking
- Source citation
- Async processing with Celery
- Object storage with MinIO
- Why the public demo is intentionally restricted
```

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/demo-script.md
git commit -m "docs: add demo walkthrough"
```

---

### Task 13: Server Provisioning Checklist

**Files:**
- Modify: `docs/deployment-demo.md`

- [ ] **Step 1: Add server checklist**

Append:

```markdown
## Server Checklist

Recommended minimum for demo:

- 2 vCPU
- 4 GB RAM minimum, 8 GB preferred for Milvus
- 40 GB disk
- Ubuntu 22.04 or 24.04
- Docker and Docker Compose installed
- Domain DNS A record pointing to the server

Firewall:

- Allow `22/tcp` from your IP only if possible
- Allow `80/tcp`
- Allow `443/tcp`
- Deny direct access to `8000`, `9000`, `9001`, `15672`, `19530`, `6379`, `5555`
```

- [ ] **Step 2: Add deployment commands**

Append:

```markdown
## Deployment Commands

```bash
git clone <repo-url> ragPdfSystem
cd ragPdfSystem
cp .env.production.example .env.production
# Edit .env.production on the server and fill real secrets.

cd frontend
npm ci
npm run build
cd ..

docker compose -f docker/docker-compose.prod.yml --env-file .env.production up -d --build
docker compose -f docker/docker-compose.prod.yml --env-file .env.production ps
```

Expected:

- `nginx` is running
- `app` is running
- `worker` is running
- `redis`, `rabbitmq`, `minio`, `etcd`, `milvus-standalone` are running
```

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/deployment-demo.md
git commit -m "docs: add server deployment checklist"
```

---

### Task 14: Verification Before Sharing

**Files:**
- Modify: `docs/deployment-demo.md`

- [ ] **Step 1: Add verification checklist**

Append:

```markdown
## Verification Checklist

Run before sending the link to interviewers:

```bash
curl -I https://your-domain.example
curl https://your-domain.example/api/v1/health
```

Expected:

- Frontend returns `200`
- Health endpoint returns healthy status

Manual checks:

- Login works with demo account.
- Public registration is disabled.
- Upload rejects files larger than `10 MB`.
- Upload rejects unsupported file extensions.
- Chat works on the demo document.
- Answers include source references.
- Evaluation page can run on demo data.
- Direct MinIO, RabbitMQ, Redis, Milvus, and Flower ports are not reachable publicly.
- Browser devtools show no leaked API keys.
- `.env.production` is not committed.
```

- [ ] **Step 2: Commit**

Run:

```bash
git add docs/deployment-demo.md
git commit -m "docs: add demo verification checklist"
```

---

### Task 15: Portfolio Packaging

**Files:**
- Modify: `README.md`
- Modify: `docs/demo-script.md`

- [ ] **Step 1: Add demo link section to README**

Add:

```markdown
## Online Demo

This project has a restricted online demo for interview review.

- Demo URL: `https://your-domain.example`
- Demo account: shared privately during interview/review
- Deployment type: controlled portfolio demo, not open production

The public demo restricts registration, upload size, file types, and infrastructure console access to reduce privacy and cost risks.
```

- [ ] **Step 2: Add architecture talking points**

Add:

```markdown
## Architecture Highlights

- FastAPI backend with modular routers
- Vue 3 frontend with same-origin API proxying
- Celery worker for asynchronous document processing
- Milvus for vector retrieval
- MinIO for object storage
- Redis and RabbitMQ for cache/task queue support
- DashScope/Qwen for embedding, reranking, and LLM responses
```

- [ ] **Step 3: Commit**

Run:

```bash
git add README.md docs/demo-script.md
git commit -m "docs: add online demo portfolio notes"
```

---

## Final Go/No-Go Gate

Only share the deployed link when every item below is true:

- [ ] `.env.production` exists on the server and is not committed.
- [ ] `SECRET_KEY`, RabbitMQ password, MinIO keys, and DashScope key are real strong secrets.
- [ ] Public registration is disabled.
- [ ] Demo account works.
- [ ] Upload size and extension limits work.
- [ ] CORS allows only the real frontend origin.
- [ ] Infrastructure ports are not public.
- [ ] HTTPS works.
- [ ] Demo data has no sensitive content.
- [ ] LLM/API usage has a cost ceiling.
- [ ] README explains that this is a controlled demo.

## Production Upgrade Backlog

Do these only if the project becomes a real service:

- Replace SQLite with PostgreSQL and migrations.
- Add per-user storage quotas and daily LLM budget enforcement.
- Add request rate limiting through Nginx or application middleware.
- Add structured logs and error monitoring.
- Add backups for database, MinIO, and Milvus volumes.
- Add admin-only observability instead of public Flower/RabbitMQ consoles.
- Add CI tests for auth, upload validation, and query limits.
- Add automated deployment with rollback.
- Add privacy policy and data deletion flow.
