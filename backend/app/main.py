from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.routes import applications

app = FastAPI(title="Smart Job Application Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)


@app.get("/")
def read_root():
    """Basic health-check endpoint."""
    return {"message": "Smart Job Application Tracker API is running"}


@app.get("/health")
def health_check():
    """Used later by monitoring tools to verify the API is alive."""
    return {"status": "ok"}


handler = Mangum(app)