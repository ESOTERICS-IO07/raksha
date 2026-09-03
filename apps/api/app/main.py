from fastapi import FastAPI

app = FastAPI(
    title="RAKSHA API",
    description="Fraud intelligence and adaptive friction platform",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "service": "raksha-api",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "raksha-api",
    }