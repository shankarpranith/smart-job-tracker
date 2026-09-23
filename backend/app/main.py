from fastapi import FastAPI

from app.routes import applications

app = FastAPI(title="Smart Job Application Tracker")

app.include_router(applications.router)


@app.get("/")
def read_root():
    """Basic health-check endpoint."""
    return {"message": "Smart Job Application Tracker API is running"}


@app.get("/health")
def health_check():
    """Used later by monitoring tools to verify the API is alive."""
    return {"status": "ok"}