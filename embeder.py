
from fastapi import FastAPI
from model2vec import StaticModel
from pydantic import BaseModel

app = FastAPI()

model = StaticModel.from_pretrained(
    "minishlab/potion-base-8M"
)


class EmbeddingRequest(BaseModel):
    inputs: list[str]


@app.post("/embed")
def embed(req: EmbeddingRequest):

    vectors = model.encode(req.inputs)

    # Return one embedding vector per input
    return {
        "embedding": vectors.tolist()
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7870
    )