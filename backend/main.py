from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Ensure the `src` package folder is importable as top-level when this file
# is executed directly (for example: `streamlit run src/main.py`). This
# makes modules like `routers`, `models`, and `utils` importable without
# the `src.` prefix.
sys.path.insert(0, os.path.dirname(__file__))

from .routers import user, athlete, performance, auth
from .database import initialize_database
from contextlib import asynccontextmanager
import uvicorn
import threading


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize the database (runs before the app starts)
    initialize_database()
    yield
    # Shutdown: add cleanup here if needed

app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router)
app.include_router(athlete.router)
app.include_router(performance.router, prefix="/performance")
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__" and threading.current_thread() is threading.main_thread():
    # Only start the server when running in the main interpreter thread.
    # Streamlit executes modules in worker threads which causes
    # `ValueError: signal only works in main thread of the main interpreter`
    # when uvicorn attempts to set signal handlers for reloading.
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)

