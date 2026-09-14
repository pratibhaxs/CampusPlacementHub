# Campus Placement Experience Hub

A full-stack platform for college students to browse real placement/interview
experiences shared by seniors and alumni, searchable by company, college,
role, year, branch, and difficulty — with a question repository, frequency
analysis, and a star-rated recommendation feature.

**Stack:** React (Vite) + **FastAPI** (REST API) + MySQL, JWT auth,
role-based access control (student / alumni / admin).

---

## Quick start

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set DB_PASSWORD to your local MySQL password

# in MySQL: CREATE DATABASE campus_placement_hub;

# create tables (no migration tooling — same as before)
python3 -c "from app.database import Base, engine; from app import models; Base.metadata.create_all(bind=engine)"

python run.py
# or equivalently: uvicorn app.main:app --reload
```

Visit `http://localhost:5000/api/health/db` — should return
`{"status": "ok", "message": "MySQL connection successful"}`.


### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` 

### Run the test

```bash
cd backend
pip install pytest httpx   # httpx powers FastAPI's TestClient
pytest tests/ -v
```

---

## Project structure

```
backend/
  app/
    models/       SQLAlchemy models (one file per table)
    schemas/       Pydantic request/response models
    routers/       FastAPI APIRouters (one file per resource)
    database.py    engine, SessionLocal, Base, get_db dependency
    security.py     password hashing, JWT, auth dependencies
    config.py       Settings (pydantic-settings, reads .env)
    main.py         create_app() factory, CORS, exception handlers
  tests/          99 pytest tests across 12 files, using TestClient
  run.py, requirements.txt

frontend/                unchanged by the backend conversion
  src/
    api/, components/, context/, pages/, routes/
```


