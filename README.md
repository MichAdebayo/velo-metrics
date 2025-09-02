# sql_fast-api

Repository reorganized to use:

- `src/` for FastAPI application (`src/main.py`, routers, models, utils)
- `streamlit/` for Streamlit UI (`streamlit/app.py` and `streamlit/pages/`)

How to run

1. Install dependencies (prefer a venv):

```bash
pip install -r requirements.txt
```

2. Run Streamlit UI:

```bash
streamlit run streamlit/app.py
```

3. Run FastAPI:

```bash
uvicorn src.main:app --reload
```

Notes

- Database path is now taken from `src/config.py` `DATABASE_URL`. If not set, it defaults to `cyclist_database.db` in the project root.
- Legacy single-file apps were removed or moved to `scripts/` to avoid duplication.
