from fastapi import FastAPI

app = FastAPI(
    title="BI Recommendation API",
    description="API for adaptive BI recommendation engine",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the BI Recommendation API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}