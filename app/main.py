from fastapi import FastAPI
from app.collector import start_background_collector, manual_collect, get_dataset

app = FastAPI(
    openapi_url="/openapi.json",
    docs_url="/docs"
)

@app.on_event("startup")
async def startup_event():
    start_background_collector()

@app.get("/dataset")
async def read_dataset():
    return get_dataset()

@app.post("/collect")
async def collect_now():
    return manual_collect()
