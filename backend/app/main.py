from fastapi import FastAPI
from mangum import Mangum

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


# This is the entry point AWS Lambda calls.
# Mangum wraps our FastAPI ASGI app so Lambda's event/context format
# gets translated into a normal HTTP request FastAPI understands.
handler = Mangum(app)