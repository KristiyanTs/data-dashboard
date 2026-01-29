from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import contracts
from .database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Procurement Data Dashboard API",
    description="API for managing procurement contracts",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contracts.router)

@app.get("/")
async def root():
    return {"message": "Procurement Data Dashboard API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
