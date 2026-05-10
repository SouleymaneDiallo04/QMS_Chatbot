# 🏗️ Architecture Détaillée — QMS Chatbot v2

Ce document fournit une analyse technique profonde de l'architecture système.

---

## 📊 Architecture Générale

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE LAYER                               │
│                        Next.js Frontend (React 19)                          │
│  ┌──────────────┬────────────────┬─────────────┬──────────────────────────┐ │
│  │  Chat Page   │  Admin Panel   │  Audit Page │  PFMEA | Search | Logs  │ │
│  │  (main UI)   │  (6 tabs)      │  (checklist)│                         │ │
│  └──────────────┴────────────────┴─────────────┴──────────────────────────┘ │
│                          JWT Token (localStorage)                           │
└────────────────────────┬──────────────────────────────────────────────────┬─┘
                         │ HTTP/JSON + Bearer Token                         │
                         ↓                                                   │
┌─────────────────────────────────────────────────────────────────────────────┐
│                          API GATEWAY LAYER                                  │
│                       FastAPI (Python 3.10+)                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Middleware: CORS | JWT Auth | Rate Limiting (slowapi)            │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Route Groups:                                                       │  │
│  │  • /api/auth          → JWT token management                       │  │
│  │  • /api/chat          → RAG query + LLM synthesis                  │  │
│  │  • /api/search        → Vector + full-text search                  │  │
│  │  • /api/config        → LLM provider configuration (admin)         │  │
│  │  • /api/documents     → Upload/manage QMS docs (admin)             │  │
│  │  • /api/users         → User management (admin)                    │  │
│  │  • /api/audit         → Audit assistant + export                   │  │
│  │  • /api/generate      → PFMEA generation + export                  │  │
│  │  • /api/logs          → Activity audit trail (admin)               │  │
│  │  • /api/sessions      → Chat history management                    │  │
│  │  • /api/stats         → Dashboard metrics (admin)                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────────────────────────┬──┘
                   │ SQL Queries | Vector Queries                        │
                   ↓                                                      │
┌──────────────────────────────────────────────────────────────────────┐ │
│                      BUSINESS LOGIC LAYER                            │ │
│                                                                      │ │
│  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │ llm_rag.py: LLM Orchestration                               │  │ │
│  │  • invoke_llm() → Groq | Gemini | DeepSeek | Ollama         │  │ │
│  │  • synthesize_from_context() → Answer synthesis with [refs] │  │ │
│  │  • Error handling & retries                                 │  │ │
│  └─────────────────────────────────────────────────────────────┘  │ │
│                                                                      │ │
│  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │ rag.py: Vector Retrieval & Embedding                         │  │ │
│  │  • get_embeddings() → HuggingFace (multilingual 384-dim)     │  │ │
│  │  • ingest_document() → chunk + embed + store in Chroma       │  │ │
│  │  • search_similar_chunks() → vector search + re-ranking      │  │ │
│  │  • _ce_score_to_distance() → CrossEncoder relevance          │  │ │
│  └─────────────────────────────────────────────────────────────┘  │ │
│                                                                      │ │
│  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │ services_qms.py: QMS Domain Logic                            │  │ │
│  │  • audit_questions_for_standard() → ISO 9001/IATF questions  │  │ │
│  │  • pfmea_skeleton_rows() → Generate PFMEA structure          │  │ │
│  │  • audit_sampling_plan() → Calculate sample sizes            │  │ │
│  │  • verify_pfmea_row() → Validate completeness                │  │ │
│  │  • DEFAULT_TEMPLATES → Pre-built audit/PFMEA                 │  │ │
│  └─────────────────────────────────────────────────────────────┘  │ │
│                                                                      │ │
│  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │ auth.py: Security & Authentication                           │  │ │
│  │  • create_access_token(HS256, 8h expiry)                     │  │ │
│  │  • decode_access_token(validation)                           │  │ │
│  │  • Role checking (admin/user)                                │  │ │
│  │  • Criticality-based filtering                               │  │ │
│  └─────────────────────────────────────────────────────────────┘  │ │
│                                                                      │ │
│  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │ crypto_utils.py: Data Protection                             │  │ │
│  │  • encrypt_api_key(Fernet AES-128+HMAC)                      │  │ │
│  │  • decrypt_api_key()                                         │  │ │
│  └─────────────────────────────────────────────────────────────┘  │ │
│                                                                      │ │
│  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │ Export Modules:                                              │  │ │
│  │  • DOCX generation (python-docx)                             │  │ │
│  │  • PDF generation (fpdf2)                                    │  │ │
│  │  • Document formatting & styling                            │  │ │
│  └─────────────────────────────────────────────────────────────┘  │ │
└──────────────────────────────────────────────────────────────────┘ │
                   │                                                 │
                   ↓                                                 ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                        DATA PERSISTENCE LAYER                                │
│                                                                              │
│  ┌──────────────────────────────────────┐  ┌──────────────────────────────┐ │
│  │  SQLite Relational Database          │  │  Chroma Vector Database      │ │
│  │  (qms_chatbot.db)                    │  │  (./chroma_db/)              │ │
│  │                                      │  │                              │ │
│  │  Tables:                             │  │  Collections:                │ │
│  │  • users                             │  │  • documents (embeddings)    │ │
│  │  • llm_configs (encrypted keys)      │  │  • metadata (per chunk)      │ │
│  │  • document_metadata                 │  │                              │ │
│  │  • document_templates                │  │  Embedding Model:            │ │
│  │  • activity_logs (audit trail)       │  │  sentence-transformers/      │ │
│  │  • chat_sessions (persistence)       │  │  paraphrase-multilingual-    │ │
│  │  • audit_results                     │  │  MiniLM-L12-v2               │ │
│  │  • app_settings                      │  │  → 384 dimensions            │ │
│  │                                      │  │  → 50+ languages             │ │
│  │  Schema: SQLAlchemy 2.0              │  │                              │ │
│  │  • Lightweight migrations            │  │  Persistence:                │ │
│  │  • Multi-tenant (site isolation)     │  │  • SQLite backend            │ │
│  │  • Timezone-aware timestamps         │  │  • .parquet collections      │ │
│  └──────────────────────────────────────┘  └──────────────────────────────┘ │
│                                                                              │
│  ┌──────────────────────────────────────┐                                   │
│  │  File Storage                        │                                   │
│  │  (./uploads/)                        │                                   │
│  │                                      │                                   │
│  │  Supported Formats:                  │                                   │
│  │  • PDF (PyPDFLoader)                 │                                   │
│  │  • DOCX (python-docx)                │                                   │
│  │  • XLSX (openpyxl)                   │                                   │
│  │  • PPTX (python-pptx)                │                                   │
│  │                                      │                                   │
│  │  Indexing Strategy:                  │                                   │
│  │  1. Parse document                   │                                   │
│  │  2. Chunk (adaptive by doc type)     │                                   │
│  │  3. Embed (384-dim vectors)          │                                   │
│  │  4. Store in Chroma + SQLite refs    │                                   │
│  └──────────────────────────────────────┘                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 RAG Pipeline (Retrieval-Augmented Generation)

```
User Query
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ 1. QUERY EMBEDDING                                              │
│    • Vectorize user query (HuggingFace multilingual)            │
│    • Output: 384-dim vector                                     │
└──────────────────┬──────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. VECTOR SEARCH (Chroma)                                       │
│    • Cosine similarity search                                   │
│    • Return k=10-20 candidate chunks                            │
│    • Each chunk: {text, doc_id, filename, page, metadata}       │
│    • Filter by: doc_type, criticality, language, owner          │
└──────────────────┬──────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. RE-RANKING (CrossEncoder)                                    │
│    • Score candidates against original query                    │
│    • Keep top-5 most relevant                                   │
│    • Convert logits → pseudo-distances                          │
│    • Sort by relevance descending                               │
└──────────────────┬──────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. CONTEXT ASSEMBLY                                             │
│    • Format: "[1] excerpt1 [source: doc1.pdf p.5]"              │
│    •         "[2] excerpt2 [source: doc2.docx]"                 │
│    •         "[3] excerpt3 [source: doc3.xlsx]"                 │
│    • Numbered for citation in answer                            │
└──────────────────┬──────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. LLM SYNTHESIS (Multi-Provider)                               │
│    invoke_llm():                                                │
│      Provider = Groq | Gemini | DeepSeek | Ollama               │
│      SystemPrompt = QMS-specific instructions                   │
│      UserPrompt = Context + Query + Language mode               │
│      Output = Structured response                               │
└──────────────────┬──────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. RESPONSE FORMATTING                                          │
│    synthesize_from_context() → {                                │
│      "summary": "2-4 sentence brief",                           │
│      "summary_bullets": ["point1", "point2"],                   │
│      "details": "Full answer [1] [2] [3]",                      │
│      "answer_in_context": true/false,                           │
│      "sources": [                                               │
│        {filename, doc_type, criticality, language, relevance}   │
│      ]                                                          │
│    }                                                            │
└──────────────────┬──────────────────────────────────────────────┘
                   ↓
            Return to Frontend
```

---

## 🤖 LLM Provider Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    LLM ORCHESTRATION LAYER                           │
│                                                                      │
│  invoke_llm(provider, api_key, base_url, model, system_prompt, ...) │
│                          │                                           │
│          ┌───────────────┼───────────────┬───────────────────────┐   │
│          ↓               ↓               ↓                       ↓   │
│    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────────┐│
│    │   GROQ      │ │   GEMINI    │ │  DEEPSEEK   │ │   OLLAMA     ││
│    │             │ │             │ │             │ │              ││
│    │ API:        │ │ API:        │ │ API:        │ │ API:         ││
│    │ groq.com    │ │ google.com  │ │ deepseek.com│ │ localhost    ││
│    │             │ │             │ │             │ │ :11434       ││
│    │ Model:      │ │ Model:      │ │ Model:      │ │ Model:       ││
│    │ llama-3.1   │ │ gemini-2.0  │ │ deepseek    │ │ llama3.2     ││
│    │ -8b-instant │ │ -flash      │ │ -chat       │ │ (local)      ││
│    │             │ │             │ │             │ │              ││
│    │ Temp: 0.15  │ │ Temp: 0.15  │ │ Temp: 0.15  │ │ Temp: 0.15   ││
│    │ Speed: ⚡⚡⚡ │ │ Speed: ✅   │ │ Speed: ✅   │ │ Speed: ⏱️    ││
│    │ Cost: FREE  │ │ Cost: $$$   │ │ Cost: $$    │ │ Cost: FREE   ││
│    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └───────┬──────┘│
│           │               │               │                │      │
│           └───────────────┴───────────────┴────────────────┘      │
│                           ↓                                        │
│                  ┌─────────────────────────────────────┐           │
│                  │  Error Handling & Retries           │           │
│                  │  • Timeout → Fallback to next LLM   │           │
│                  │  • API error → Log + retry          │           │
│                  │  • Graceful degradation             │           │
│                  └──────────────┬──────────────────────┘           │
│                                 ↓                                  │
│                        LLM Response Stream                         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW                             │
│                                                                    │
│  Client                           Server                          │
│     │                               │                             │
│     │ 1. POST /api/auth/login       │                             │
│     │────────────────────────────→  │                             │
│     │    {username, password}       │                             │
│     │                               ├─ Lookup user in DB          │
│     │                               ├─ bcrypt.checkpw()           │
│     │                               │  (password vs hash)          │
│     │                               │                             │
│     │ 2. ← {token, username, role}  │                             │
│     │←────────────────────────────  │                             │
│     │                               │                             │
│     │ 3. Store locally:             │                             │
│     │    • localStorage["token"]    │                             │
│     │    • localStorage["user"]     │                             │
│     │                               │                             │
│     │ 4. GET /api/docs (protected)  │                             │
│     │────────────────────────────→  │                             │
│     │    Header: Authorization:     │                             │
│     │    Bearer eyJhbGciOiJIUzI1...  │                             │
│     │                               ├─ JWT validation             │
│     │                               ├─ Decode token              │
│     │                               ├─ Check expiry (8h)         │
│     │                               ├─ Verify signature          │
│     │                               ├─ Extract user_id, role     │
│     │                               │                             │
│     │ 5. ← {documents}              │                             │
│     │←────────────────────────────  │                             │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│              AUTHORIZATION & ROLE-BASED ACCESS                    │
│                                                                    │
│  Role: admin                                                       │
│    ✅ /api/config (GET/POST) — LLM provider setup                 │
│    ✅ /api/documents (POST) — Upload documents                    │
│    ✅ /api/users (POST) — Create users                            │
│    ✅ /api/logs (GET) — View activity logs                        │
│    ✅ /api/stats (GET) — Dashboard stats                          │
│    ❌ CANNOT access "Critical" docs (same as user)               │
│                                                                    │
│  Role: user                                                        │
│    ✅ /api/chat (POST) — Query + RAG synthesis                    │
│    ✅ /api/search (POST) — Vector search                          │
│    ✅ /api/audit (POST) — Generate audit                          │
│    ✅ /api/generate/pfmea (POST) — Generate PFMEA                 │
│    ❌ /api/documents (DELETE) — Cannot delete docs               │
│    ❌ /api/config (POST) — Cannot modify LLM config              │
│    ❌ /api/users (POST) — Cannot create users                    │
│    ❌ Criticality filtering: Hidden if criticality="Critical"    │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│               DATA ENCRYPTION IN TRANSIT & AT REST                │
│                                                                    │
│  At Rest:                                                          │
│    • API keys: Fernet encrypted (AES-128 + HMAC-SHA256)           │
│    • Passwords: Bcrypt hashed (salt ~10 rounds)                   │
│    • DB: SQLite3 (unencrypted by default; TDE optional)           │
│    • Files: Plaintext in ./uploads/                               │
│                                                                    │
│  In Transit:                                                       │
│    • Frontend ↔ Backend: HTTPS (reverse proxy, ngninx/Apache)     │
│    • Backend → LLM Provider: HTTPS (provider API)                 │
│    • Backend → Chroma: Local TCP (unencrypted, same machine)      │
│                                                                    │
│  Secrets Management:                                               │
│    • JWT_SECRET_KEY: 64-byte random hex (stored in .env)          │
│    • API_KEY_ENCRYPTION_KEY: Fernet key (stored in .env)          │
│    • Never commit .env to Git                                     │
│    • Rotate keys periodically                                     │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                    AUDIT TRAIL LOGGING                             │
│                                                                    │
│  Every User Action → activity_logs Table:                         │
│    {                                                              │
│      "username": "john_doe",                                      │
│      "action": "chat_query",                                      │
│      "query": "[first 500 chars of user query]",                  │
│      "document_ids": "[1, 3, 5]",  # Sources used                 │
│      "confidence": "High",                                        │
│      "confidence_score": 78.5,                                    │
│      "language_mode": "document_language",                        │
│      "response_summary": "[first 300 chars]",                     │
│      "created_at": "2025-05-10T14:32:00Z"                         │
│    }                                                              │
│                                                                    │
│  Compliance: ISO 9001 audit trail (full traceability)             │
│  Retention: Permanent (consider auto-archival for >2 years)       │
└────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema (Logical Model)

```sql
-- Users Table
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,      -- Login identifier
  password_hash TEXT NOT NULL,        -- Bcrypt hash
  role TEXT DEFAULT 'user',           -- 'admin' | 'user'
  site TEXT DEFAULT 'default',        -- Multi-tenant isolation
  created_at TIMESTAMP DEFAULT NOW
);

-- LLM Configuration (Encrypted API Keys)
CREATE TABLE llm_configs (
  id INTEGER PRIMARY KEY,
  provider TEXT UNIQUE NOT NULL,      -- 'groq'|'gemini'|'deepseek'|'ollama'
  api_key TEXT,                       -- Fernet encrypted
  base_url TEXT,                      -- Custom endpoint (optional)
  model_name TEXT,                    -- e.g., 'llama-3.1-8b-instant'
  is_active BOOLEAN DEFAULT 0,
  updated_at TIMESTAMP DEFAULT NOW
);

-- Document Metadata (Indexed in Chroma Vector DB)
CREATE TABLE document_metadata (
  id INTEGER PRIMARY KEY,
  filename TEXT NOT NULL,             -- Original filename
  file_path TEXT,                     -- Path in ./uploads/
  doc_type TEXT,                      -- 'Procedure'|'Work Instruction'|'Form'
  criticality TEXT,                   -- 'Low'|'Medium'|'High'|'Critical'
  language TEXT DEFAULT 'en',         -- ISO 639-1 code
  version TEXT,                       -- Document version
  owner TEXT,                         -- Department/person
  site TEXT DEFAULT 'default',        -- Multi-tenant
  uploaded_at TIMESTAMP,
  indexed_chunks INTEGER,             -- Count in vector DB
  file_size_bytes INTEGER
);

-- Pre-built Document Templates
CREATE TABLE document_templates (
  id INTEGER PRIMARY KEY,
  key TEXT UNIQUE NOT NULL,           -- 'pfmea_blank', 'audit_iso9001'
  name TEXT,                          -- Display name
  doc_type TEXT,                      -- Document type
  language TEXT,                      -- 'en' | 'fr'
  version TEXT,
  body TEXT                           -- Template content (Markdown/HTML)
);

-- Activity Audit Trail (ISO 9001 Compliance)
CREATE TABLE activity_logs (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL,             -- Who performed action
  action TEXT NOT NULL,               -- 'chat_query', 'audit_created', ...
  query TEXT,                         -- User query (first 500 chars)
  document_ids TEXT,                  -- JSON array of used doc IDs
  confidence TEXT,                    -- 'High'|'Medium'|'Low'
  confidence_score REAL,              -- 0-100
  language_mode TEXT,                 -- RAG language mode
  response_summary TEXT,              -- First 300 chars of response
  created_at TIMESTAMP DEFAULT NOW
);

-- Chat Session History (Persistent)
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY,                -- UUID
  username TEXT NOT NULL,             -- Session owner
  title TEXT,                         -- e.g., "Supplier Audit Q1"
  messages_json TEXT,                 -- JSON array of messages
  updated_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW
);

-- Saved Audit Checklists
CREATE TABLE audit_results (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL,             -- Audit creator
  standard TEXT,                      -- 'ISO 9001' | 'IATF 16949'
  process TEXT,                       -- Process audited
  checklist_json TEXT,                -- JSON array of {question, checked, note}
  created_at TIMESTAMP DEFAULT NOW,
  updated_at TIMESTAMP
);

-- Application Settings
CREATE TABLE app_settings (
  id INTEGER PRIMARY KEY,
  key TEXT UNIQUE NOT NULL,           -- Setting name
  value TEXT                          -- JSON value
);
```

---

## 🧩 Frontend Component Hierarchy

```
Layout (layout.tsx)
├─ Toast Container (Toast.tsx)
├─ Navigation (global)
└─ <Route Pages>
   │
   ├─ Page (page.tsx) — MAIN CHAT
   │  ├─ MessageList
   │  │  └─ MessageItem
   │  │     ├─ Role badge (User/Assistant)
   │  │     ├─ Message content
   │  │     ├─ Confidence bar (green/amber/red)
   │  │     ├─ Summary vs Details toggle
   │  │     └─ Source citations
   │  ├─ FilterPanel
   │  │  ├─ DocType selector
   │  │  ├─ Criticality selector
   │  │  ├─ Language selector
   │  │  └─ Date range picker
   │  └─ InputBox
   │     └─ Textarea + Send button
   │
   ├─ Admin (admin/page.tsx) — ADMIN DASHBOARD
   │  ├─ TabBar (6 tabs)
   │  │
   │  ├─ Tab 1: Dashboard
   │  │  └─ StatsPanel
   │  │     ├─ Document count card
   │  │     ├─ User stats card
   │  │     ├─ Query volume chart
   │  │     └─ LLM provider usage
   │  │
   │  ├─ Tab 2: Users
   │  │  ├─ UserList
   │  │  │  └─ UserRow (each user: role, delete btn)
   │  │  └─ CreateUserForm
   │  │     ├─ Username input
   │  │     ├─ Password input
   │  │     └─ Role selector
   │  │
   │  ├─ Tab 3: Documents
   │  │  ├─ DropZone (drag-and-drop upload)
   │  │  ├─ MetadataForm
   │  │  │  ├─ DocType selector
   │  │  │  ├─ Criticality selector
   │  │  │  ├─ Language selector
   │  │  │  └─ Owner input
   │  │  └─ DocumentList
   │  │     └─ DocRow (each doc: name, type, delete btn)
   │  │
   │  ├─ Tab 4: LLM Config
   │  │  ├─ ProviderSelector (Groq|Gemini|DeepSeek|Ollama)
   │  │  ├─ ConfigForm (depends on provider)
   │  │  │  ├─ API key input (masked)
   │  │  │  ├─ Base URL input
   │  │  │  └─ Model name selector
   │  │  ├─ TestButton (verify connectivity)
   │  │  └─ ActiveProviderBadge
   │  │
   │  ├─ Tab 5: Logs
   │  │  ├─ FilterBar
   │  │  │  └─ Action type selector
   │  │  └─ LogTable
   │  │     ├─ Username col
   │  │     ├─ Action col
   │  │     ├─ Query col (truncated)
   │  │     ├─ Confidence col
   │  │     └─ Timestamp col
   │  │
   │  └─ Tab 6: Audit
   │     ├─ AuditGeneratorForm
   │     │  ├─ Standard selector
   │     │  ├─ Process input
   │     │  └─ Depth selector (Light|Normal|Deep)
   │     └─ ExportButtons (DOCX|PDF)
   │
   ├─ Login (login/page.tsx) — AUTH
   │  ├─ Logo
   │  ├─ LoginForm
   │  │  ├─ Username input
   │  │  ├─ Password input
   │  │  └─ Submit button
   │  └─ ErrorMessage
   │
   ├─ Audit (audit/page.tsx) — AUDIT ASSISTANT
   │  ├─ AuditGeneratorForm
   │  │  ├─ Standard selector
   │  │  ├─ Process input
   │  │  ├─ Depth selector
   │  │  └─ Generate button
   │  ├─ ChecklistView
   │  │  ├─ Completion counter
   │  │  └─ ChecklistItems
   │  │     └─ Item (checkbox + note textarea)
   │  ├─ SaveButton
   │  └─ ExportButtons (DOCX|PDF)
   │
   ├─ PFMEA (pfmea/page.tsx) — RISK ANALYSIS
   │  ├─ ProcessInputForm
   │  │  ├─ Process description textarea
   │  │  ├─ Defect list textarea
   │  │  └─ Generate button
   │  ├─ PfmeaTable
   │  │  ├─ Line#
   │  │  ├─ Process Step (editable)
   │  │  ├─ Failure Mode (editable)
   │  │  ├─ Severity slider (1-10)
   │  │  ├─ Occurrence slider (1-10)
   │  │  ├─ Detection slider (1-10)
   │  │  ├─ RPN (auto-calculated)
   │  │  ├─ Recommended Actions (editable)
   │  │  ├─ RAG Context (expandable)
   │  │  └─ Validation warnings
   │  ├─ ExportButtons (DOCX|PDF)
   │  └─ AddRowButton
   │
   ├─ Search (search/page.tsx) — ADVANCED SEARCH
   │  ├─ SearchForm
   │  │  ├─ Query input
   │  │  ├─ FilterPanel (doc_type, criticality, language, date)
   │  │  └─ Search button
   │  └─ ResultsList
   │     └─ ResultItem
   │        ├─ Snippet (highlighted)
   │        ├─ Source metadata
   │        └─ ViewButton
   │
   └─ Logs (logs/page.tsx) — ACTIVITY LOGS
      ├─ FilterBar
      │  └─ Action type selector
      └─ LogTable
         ├─ Username
         ├─ Action
         ├─ Query (truncated)
         ├─ Confidence
         └─ Timestamp
```

---

## 🔁 API Request/Response Examples

### Chat Query (RAG)

**Request:**
```json
POST /api/chat
Authorization: Bearer <jwt_token>

{
  "query": "How to ensure supplier compliance?",
  "language_mode": "document_language",
  "respond_english": false,
  "filters": {
    "doc_types": ["Procedure", "Work Instruction"],
    "criticalities": ["Low", "Medium", "High"],
    "languages": ["en", "fr"],
    "owner": null,
    "date_range": {"start": "2024-01-01", "end": null}
  }
}
```

**Response:**
```json
{
  "summary": "Supplier compliance is ensured through regular audits, quality agreements, and performance metrics...",
  "summary_bullets": [
    "Conduct annual supplier audits",
    "Define quality acceptance criteria",
    "Monitor key performance indicators (KPIs)"
  ],
  "details": "Supplier compliance is ensured through [1] regular audits based on [2] quality agreements. [1] Procedures require annual assessments of supplier process capability. [2] Quality agreements define specific requirements...",
  "answer_in_context": true,
  "sources": [
    {"filename": "Supplier_Management.pdf", "doc_type": "Procedure", "criticality": "High", "language": "en"},
    {"filename": "Quality_Agreement_Template.docx", "doc_type": "Form", "criticality": "Medium", "language": "fr"}
  ],
  "rag_synthesis": {
    "chunks_found": 12,
    "chunks_reranked": 5,
    "embedding_time_ms": 45,
    "search_time_ms": 120,
    "llm_time_ms": 3200
  }
}
```

### Audit Generation

**Request:**
```json
POST /api/audit/assistant
Authorization: Bearer <jwt_token>

{
  "standard": "ISO 9001",
  "process": "Supplier Management",
  "depth": "normal"
}
```

**Response:**
```json
{
  "checklist_normative": [
    {"question": "Does the organization identify and assess supplier requirements?", "checked": false, "note": ""},
    {"question": "Are supplier audits conducted based on risk assessment?", "checked": false, "note": ""},
    {"question": "Are supplier performance metrics tracked and reviewed?", "checked": false, "note": ""}
  ],
  "control_plan_note": "Implement quarterly supplier performance reviews. Establish escalation procedures for non-conformances.",
  "nonconformity_examples": [
    "Missing supplier quality agreement",
    "Supplier audit overdue (>12 months)",
    "No evidence of performance KPI monitoring"
  ],
  "rag_context": {
    "relevant_documents": [
      {"filename": "Supplier_Management.pdf", "page": 3},
      {"filename": "Quality_Policy.docx"}
    ],
    "reference_excerpts": ["...suppliers shall be evaluated...", "...annual audit schedule..."]
  }
}
```

### PFMEA Generation

**Request:**
```json
POST /api/generate/pfmea
Authorization: Bearer <jwt_token>

{
  "process_description": "Molding process for plastic housing",
  "product_name": "Plastic housing",
  "known_defects": "Crack formation, color variation, warping"
}
```

**Response:**
```json
{
  "pfmea_rows": [
    {
      "line": 1,
      "process_step": "Molding",
      "product": "Plastic housing",
      "failure_mode": "Crack formation",
      "effects": "Product leak, customer complaint, warranty claim",
      "severity": null,
      "occurrence": null,
      "detection": null,
      "rpn": null,
      "recommended_actions": "",
      "rag_context_excerpt": "Pressure parameters must be maintained between 800-900 bar. Temperature control ±5°C...",
      "_missing": ["severity", "occurrence", "detection"]
    }
  ]
}
```

---

## 🌐 Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│              PRODUCTION DEPLOYMENT                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │         INTERNET (Users)                        │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │ HTTPS                            │
│                     ↓                                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │   Load Balancer (ALB / NLB)                     │   │
│  │   • SSL/TLS termination                        │   │
│  │   • Route to backend + frontend instances      │   │
│  └──────────────────┬──────────────────────────────┘   │
│         │           │                                   │
│    ┌────┴──────┬────┴────┐                             │
│    ↓           ↓         ↓                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │      Nginx Reverse Proxy (x2 instances)        │   │
│  │  • Routing: /api → Backend | / → Frontend      │   │
│  │  • SSL offloading                              │   │
│  │  • Rate limiting                               │   │
│  └──────────────────┬──────────────────────────────┘   │
│         │           │                                   │
│    ┌────┴──────────┴────┐                             │
│    ↓                     ↓                             │
│  ┌────────────────┐  ┌──────────────┐                │
│  │  Backend API   │  │  Frontend    │                │
│  │  (Gunicorn +   │  │  (Next.js    │                │
│  │   Uvicorn)     │  │   SSR)       │                │
│  │  x3 instances  │  │  x2 instances│                │
│  └────────┬───────┘  └──────┬───────┘                │
│           │                 │                         │
│           └────────┬────────┘                         │
│                    ↓                                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │     PostgreSQL Database (RDS / Managed)         │   │
│  │  • Multi-AZ for HA                              │   │
│  │  • Automated backups                            │   │
│  │  • Connection pooling                           │   │
│  └─────────────────────────────────────────────────┘   │
│                    │                                   │
│           ┌────────┴────────┐                        │
│           ↓                 ↓                        │
│  ┌─────────────────────┐  ┌──────────────────────┐  │
│  │  Chroma Vector DB   │  │  S3 File Storage     │  │
│  │  (Redis VectorDB)   │  │  (Backup & Archive)  │  │
│  │  or ElasticSearch   │  │                      │  │
│  └─────────────────────┘  └──────────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │     Monitoring & Logging                        │   │
│  │  • CloudWatch (AWS) / Application Insights      │   │
│  │  • ELK Stack (Elasticsearch/Kibana)             │   │
│  │  • APM (Application Performance Monitoring)     │   │
│  │  • Alerting (PagerDuty)                         │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Performance Optimization Strategies

| Layer | Current | Optimization |
|-------|---------|---------------|
| **Embedding** | 15s startup (HF download) | Pre-download model, Docker layer caching |
| **Vector Search** | 50-200ms (k=10-20) | Redis caching for popular queries |
| **LLM** | 3-15s (network I/O) | Ollama local (no latency), batch requests |
| **DB Queries** | <50ms (SQLite) | Migrate to PostgreSQL + connection pool |
| **Frontend** | 3s initial load (SSR) | Next.js ISR, React.lazy(), code splitting |
| **File Upload** | Variable (PDF parsing) | Async task queue (Celery), S3 pre-signed URLs |

---

## 🔄 Deployment & CI/CD Pipeline

```
GitHub Push → GitHub Actions
    ↓
┌─────────────────────────────────────┐
│ 1. Lint & Format Check              │
│    • ESLint (frontend)              │
│    • Pylint (backend)               │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. Unit Tests                       │
│    • Frontend: Jest                 │
│    • Backend: pytest                │
│    • Coverage >80%                  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. Build Artifacts                  │
│    • Docker image (backend)         │
│    • Next.js export (frontend)      │
│    • Push to ECR/GCR                │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. Staging Deployment               │
│    • Deploy to staging env          │
│    • Smoke tests                    │
│    • Performance tests              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 5. Production Deployment (manual)   │
│    • Blue-green deployment          │
│    • Canary releases (5% → 100%)    │
│    • Health checks & auto-rollback  │
└─────────────────────────────────────┘
```

---

## 📚 Additional References

- **RAG**: Retrieval-Augmented Generation (context from documents before LLM)
- **Vector DB**: Similarity search using embeddings (384-dim multilingual)
- **CrossEncoder**: Neural re-ranker for relevance scoring
- **PFMEA**: Failure Mode & Effects Analysis (risk assessment)
- **ISO 9001**: Quality Management System standard
- **IATF 16949**: Automotive supplier quality standard
- **JWT**: JSON Web Token (stateless authentication)
- **Fernet**: Symmetric encryption (AES + HMAC)
- **Bcrypt**: Password hashing with salt
- **Multi-tenancy**: Isolation by "site" field

---

**Last Updated:** May 10, 2025  
**Architecture Version:** 2.0  
**Status:** Production-Ready
