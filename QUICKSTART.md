# 🚀 Quick Start Guide — QMS Chatbot v2

> Lancez l'application en 5 minutes avec ce guide pas-à-pas.

---

## 📋 Prérequis

- ✅ **Python 3.10+** (téléchargez depuis [python.org](https://www.python.org/downloads/))
- ✅ **Node.js 18+** (téléchargez depuis [nodejs.org](https://nodejs.org/))
- ✅ **Git** (optionnel, pour cloner le repo)
- ✅ **~1 GB d'espace disque** (base de données + embedding model)
- ✅ **Accès Internet** (pour télécharger dépendances + LLM providers)

---

## 🎯 Installation Complète (5 étapes)

### Étape 1: Préparation Backend

```bash
# Naviguez dans le répertoire backend
cd backend

# Créez un environnement virtuel Python
python -m venv venv

# Activez l'environnement virtuel
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installez les dépendances
pip install -r requirements.txt
```

**Résultat attendu :** 
```
Successfully installed fastapi uvicorn sqlalchemy langchain chroma ...
```

---

### Étape 2: Configuration Backend

Créez un fichier `.env` dans le dossier `backend/` :

```bash
# Copier la template (Windows PowerShell)
@"
# ===== SECURITY =====
JWT_SECRET_KEY=your_very_long_random_secret_key_here_minimum_64_chars_hex
JWT_EXPIRE_MINUTES=480

# ===== ENCRYPTION (Optionnel mais recommandé) =====
API_KEY_ENCRYPTION_KEY=your_fernet_key_here

# ===== RAG CONFIGURATION =====
CHROMA_PERSIST_DIR=./chroma_db
RAG_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# ===== LLM DEFAULTS =====
GROQ_CHAT_MODEL=llama-3.1-8b-instant
GEMINI_CHAT_MODEL=gemini-2.0-flash
DEEPSEEK_CHAT_MODEL=deepseek-chat
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2

# ===== CORS =====
FRONTEND_URL=http://localhost:3000
"@ | Out-File -Encoding UTF8 .env
```

**Générer secrets sécurisés :**

```bash
# Générer JWT_SECRET_KEY (64-byte hex)
python -c "import secrets; print(secrets.token_hex(64))"

# Générer API_KEY_ENCRYPTION_KEY (Fernet key)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Remplacez les valeurs dans le fichier `.env` :

```bash
# Exemple complet:
JWT_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0....(64 chars)....
JWT_EXPIRE_MINUTES=480
API_KEY_ENCRYPTION_KEY=gAAAAABpZxyz....(Fernet key)....
CHROMA_PERSIST_DIR=./chroma_db
RAG_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
GROQ_CHAT_MODEL=llama-3.1-8b-instant
GEMINI_CHAT_MODEL=gemini-2.0-flash
DEEPSEEK_CHAT_MODEL=deepseek-chat
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2
FRONTEND_URL=http://localhost:3000
```

---

### Étape 3: Démarrer Backend

```bash
# Assurez-vous d'être dans le répertoire backend/ avec venv activé
cd backend
# (venv déjà activé)

# Lancez le serveur FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Résultat attendu :**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

✅ **Backend accessible à** : `http://localhost:8000`  
📖 **Swagger UI (test API)** : `http://localhost:8000/docs`

---

### Étape 4: Préparation Frontend

**Ouvert un 2e terminal** (important!)

```bash
# Naviguez dans le répertoire frontend
cd frontend

# Installez les dépendances npm
npm install
```

**Résultat attendu :**
```
added 256 packages in 45s
```

Créez le fichier `.env.local` :

```bash
# Windows PowerShell
@"
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
"@ | Out-File -Encoding UTF8 .env.local

# Linux/Mac
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
```

---

### Étape 5: Démarrer Frontend

```bash
# Assurez-vous d'être dans frontend/
cd frontend

# Lancez le serveur de développement Next.js
npm run dev
```

**Résultat attendu :**
```
  ▲ Next.js 16.2.4
  - Local:        http://localhost:3000
  - Environments: .env.local
```

✅ **Frontend accessible à** : `http://localhost:3000`  
✅ **Ouvrez dans navigateur** : http://localhost:3000

---

## 🎮 Premier Login

1. **Allez à** `http://localhost:3000`
2. **Vous verrez** : Login page
3. **Entrez** :
   - Username : `admin`
   - Password : `admin123`
4. **Cliquez** : Login

✅ **Vous êtes connecté!** Redirect vers Admin Dashboard

---

## 🔧 Premières Actions Post-Installation

### 1️⃣ Changer le Mot de Passe Admin (IMPORTANT!)

1. Allez à **Admin → Users**
2. Cliquez sur l'utilisateur `admin`
3. Changez le mot de passe
4. Sauvegardez

### 2️⃣ Configurer un LLM Provider

**Option A: Groq (Gratuit & Ultra-Rapide) — RECOMMANDÉ**

1. Allez à **Admin → LLM Config**
2. Sélectionnez **Provider: Groq**
3. Allez à https://console.groq.com/keys
4. Créez une API key gratuite
5. Collez-la dans **API Key field**
6. Cliquez **Test Connection**
7. ✅ Si "Status: Connected", vous êtes prêt!

**Option B: Ollama (Local & Gratuit)**

```bash
# 1. Téléchargez Ollama: https://ollama.com/download
# 2. Installez et lancez
ollama serve

# 3. Dans un autre terminal, téléchargez le modèle
ollama pull llama3.2

# 4. Retour à Admin → LLM Config
# 5. Sélectionnez Provider: Ollama
# 6. Base URL: http://127.0.0.1:11434
# 7. Model: llama3.2
# 8. Click Test Connection
```

**Option C: Google Gemini**

1. Allez à https://aistudio.google.com/app/apikeys
2. Créez une API key
3. Admin → LLM Config → Gemini
4. Collez API key
5. Test Connection

### 3️⃣ Upload Documents QMS

1. Allez à **Admin → Documents**
2. **Drag & drop** vos documents (PDF, DOCX, XLSX, PPTX)
3. Remplissez métadonnées :
   - **Doc Type** : Procedure, Work Instruction, Form, Policy, etc.
   - **Criticality** : Low, Medium, High
   - **Language** : en, fr, etc.
   - **Owner** : Votre nom/département
   - **Version** : 1.0
4. Cliquez **Upload**
5. ✅ Attendez "Indexed successfully"

**Exemple de documents à tester :**
- ISO 9001 procedure (PDF)
- Quality policy (DOCX)
- Audit checklist (XLSX)
- Process diagram (PPTX)

---

## 🎯 Test les Fonctionnalités

### Test 1: Chat RAG

1. Allez à **Chat page** (accueil)
2. Posez une question : 
   ```
   "What are the main requirements for ISO 9001 compliance?"
   ```
3. Observez :
   - 💬 Réponse synthétisée
   - 🟢 Confidence score (vert si >70%)
   - 📚 Sources listées
   - 📖 Details tab pour lire les passages complets

### Test 2: Audit Generation

1. Allez à **Audit**
2. Sélectionnez :
   - **Standard** : ISO 9001
   - **Process** : Design Review
   - **Depth** : Normal
3. Cliquez **Generate**
4. ✅ Checklist générée avec questions pertinentes
5. Cochez quelques questions
6. Cliquez **Save Checklist**
7. ✅ Sauvegardé dans historique

### Test 3: PFMEA Generation

1. Allez à **PFMEA**
2. Remplissez :
   - **Process** : "Plastic injection molding"
   - **Product** : "Housing component"
   - **Known Defects** : "Cracks, color variations, warping"
3. Cliquez **Generate**
4. ✅ Tableau PFMEA généré avec failure modes
5. Remplissez Severity/Occurrence/Detection (1-10)
6. ✅ RPN auto-calculé (S × O × D)
7. Cliquez **Export** pour DOCX/PDF

### Test 4: Advanced Search

1. Allez à **Search**
2. Entrez une requête : "supplier quality"
3. Appliquez filtres (optionnel)
4. Cliquez **Search**
5. ✅ Résultats sémantiques + full-text

### Test 5: Admin Controls

1. Allez à **Admin → Dashboard**
2. Observez les stats (# docs, # users, queries, LLM usage)
3. Allez à **Admin → Logs**
4. ✅ Voyez votre historique de requêtes (audit trail)

---

## 🔍 Troubleshooting Courant

### ❌ "ERR_CONNECTION_REFUSED on http://localhost:8000"

**Cause** : Backend pas lancé  
**Solution** :
```bash
cd backend
venv\Scripts\activate  # Windows or source venv/bin/activate (Mac/Linux)
uvicorn main:app --port 8000
```

### ❌ "ModuleNotFoundError: No module named 'fastapi'"

**Cause** : pip install -r requirements.txt pas exécuté  
**Solution** :
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### ❌ "LLM Status: false" ou "LLM error"

**Cause** : Provider LLM pas configuré ou API key invalide  
**Solution** :
1. Allez à **Admin → LLM Config**
2. Sélectionnez Provider
3. Vérifiez API key (copie exacte)
4. Test Connection
5. Si échoue, essayez Ollama (local, pas d'API key)

### ❌ "404: Document not found after upload"

**Cause** : Documents uploadés mais pas indexés  
**Solution** :
```bash
# Delete vector store et ré-upload
rm -rf backend/chroma_db/

# Ou réuploadez les documents via Admin
```

### ❌ "JSON.parse error" on login

**Cause** : Backend URL incorrecte  
**Solution** :
1. Vérifiez `.env.local` in frontend:
   ```
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```
2. Redémarrez frontend : `npm run dev`

### ❌ Python version error

**Cause** : Python <3.10  
**Solution** :
```bash
python --version  # Vérifiez version
# Si <3.10, téléchargez Python 3.10+ depuis python.org
```

### ❌ "Address already in use: 0.0.0.0:8000"

**Cause** : Port 8000 déjà utilisé  
**Solution** :
```bash
# Utilisez un port différent
uvicorn main:app --port 8001

# Et mettez à jour frontend .env.local:
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
```

---

## 📚 Structure Répertoires Clé

```
backend/
├── main.py                 # Entry point
├── requirements.txt        # Dépendances Python
├── .env                    # Configuration (NE PAS committer!)
├── chroma_db/              # Vector database (auto-créé)
├── uploads/                # Documents uploadés
├── database.py             # SQLAlchemy models
├── rag.py                  # RAG pipeline
├── llm_rag.py              # LLM orchestration
├── services_qms.py         # QMS domain logic
└── auth.py                 # JWT security

frontend/
├── package.json            # npm dependencies
├── next.config.ts          # Next.js config
├── .env.local              # API URL (local)
├── tsconfig.json           # TypeScript config
└── src/app/                # Routes & components
    ├── page.tsx            # Chat (main)
    ├── login/page.tsx      # Auth
    ├── admin/page.tsx      # Admin dashboard
    ├── audit/page.tsx      # Audit assistant
    ├── pfmea/page.tsx      # PFMEA generator
    └── components/         # Reusable UI
```

---

## 🎓 Prochaines Étapes

Une fois l'appli lancée :

1. **Lire** [README.md](README.md) pour aperçu complet
2. **Lire** [ARCHITECTURE.md](ARCHITECTURE.md) pour détails techniques
3. **Explorer** Swagger UI : http://localhost:8000/docs
4. **Expérimenter** les API endpoints
5. **Créer** des cas de test pour vos use cases

---

## 📞 Besoin d'Aide?

- ❓ **Questions API?** → Swagger UI: `/docs`
- 🐛 **Bug?** → Vérifiez les logs:
  - Backend: `backend/server_log.txt`
  - Frontend: Browser console (F12)
- 📖 **Documentation?** → [README.md](README.md) & [ARCHITECTURE.md](ARCHITECTURE.md)

---

## ⚡ Commandes Utiles

```bash
# Vérifier version Python
python --version

# Activer virtualenv (Windows)
backend\venv\Scripts\activate

# Activer virtualenv (Mac/Linux)
source backend/venv/bin/activate

# Réinitialiser admin password
cd backend && python reset_admin.py

# Créer nouvel admin user
cd backend && python create_admin.py

# Vérifier imports (debug)
cd backend && python check_imports.py

# Run backend tests
cd backend && pytest test_app.py

# Reset vector database
rm -rf backend/chroma_db/

# Frontend: Build for production
cd frontend && npm run build

# Frontend: Start production server
cd frontend && npm start
```

---

**Félicitations! 🎉 Votre QMS Chatbot est opérationnel!**

Commencez à explorer les fonctionnalités et adaptez-les à vos besoins!
