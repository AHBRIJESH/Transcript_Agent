import meilisearch
import requests
from fastapi import FastAPI

app = FastAPI()

EMBED_URL = "http://localhost:7870/embed"

client = meilisearch.Client('http://localhost:7700')
index = client.index('Transcript_Agent')

session = requests.Session()

@app.get("/retrive")
def retrieve(query: str):
    result = index.search(
        query,
        {
            "limit": 3,
            "hybrid": {
                "semanticRatio": 1.0,
                "embedder": "hf-inference",
            },
            "showRankingScore": True,
        },
    )
    return result["hits"]

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8001)