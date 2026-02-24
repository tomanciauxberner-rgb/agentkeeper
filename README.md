# Clara Insurance Platform

Agent IA pour courtiers en assurances — FastAPI + PostgreSQL + Claude

## Structure

```
clara-insurance/
├── backend/          # FastAPI + PostgreSQL
│   ├── app/
│   │   ├── agent/    # Clara AI agent
│   │   ├── api/      # Endpoints REST
│   │   ├── core/     # Config, DB, Security
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # Email service
│   └── requirements.txt
├── frontend/         # React dashboard
└── docker-compose.yml
```

## Démarrage

### 1. PostgreSQL via Docker
```bash
docker-compose up -d
```

### 2. Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editer .env avec vos clés
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Docs
http://localhost:8000/docs (DEBUG=True uniquement)

## Sécurité
- JWT avec expiration 24h
- Bcrypt rounds=12
- Lockout après 5 tentatives
- Audit logs immuables
- Multi-tenant isolation
- CORS configuré
