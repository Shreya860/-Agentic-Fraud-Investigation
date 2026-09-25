from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.actions import router as actions_router
from api.routes.cases import router as cases_router
from api.routes.investigations import router as investigations_router
from api.routes.transactions import router as transactions_router

from api.routes.benchmark import router as benchmark_router
app = FastAPI(
    title="TigerGraph Agentic Fraud Investigation API",
    description="Backend API for agentic fraud investigation and next-best action.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "fraud-investigation-api",
    }

app.include_router(benchmark_router)
app.include_router(investigations_router)
app.include_router(cases_router)
app.include_router(actions_router)
app.include_router(transactions_router)