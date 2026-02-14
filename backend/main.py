
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from . import models, database
from .routers import auth, dashboard, data_receiver, profile, history, sync
from .database import engine

# Create Tables (for MVP, instead of Alembic for now)
# Create Tables (for MVP, instead of Alembic for now)
models.Base.metadata.create_all(bind=engine)

import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ABC Tax Intelligence Platform")

# CORS Setup
origins = [
    "http://localhost:5173", # Vite Frontend
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(data_receiver.router)
app.include_router(profile.router)
app.include_router(history.router)
app.include_router(sync.router)

@app.get("/")
def read_root():
    return {"message": "ABC Backend is Running"}
