
import json
import meilisearch

MEILI_URL = "http://127.0.0.1:7700"

MEILI_API_KEY = "password"

INDEX_NAME = "Transcript_Agent"

JSON_FILE = "transcripts.json"

client = meilisearch.Client(
    MEILI_URL,
    MEILI_API_KEY
)

index = client.index(INDEX_NAME)

def configure_meilisearch():
    print("Configuring embedder...")
    task = index.update_settings({
         "embedders": {
            "hf-inference": {
                "source": "rest",
                "url": ("http://host.docker.internal:7870/embed"),
                "dimensions": 256,
                "documentTemplate": (
    "Interviewer Timestamp: {{doc.interviewer_timestamp}}\n"
    "Interviewer Question: {{doc.interviewer_question}}\n"
    "Responder: {{doc.responder}}\n"
    "Responder Timestamp: {{doc.responder_timestamp}}\n"
    "Responder Answer: {{doc.responder_answer}}"
),
                "request": {
                    "inputs": [
                        "{{text}}",
                        "{{..}}"
                    ]
                },
                "response": {
                    "embedding": [
                        "{{embedding}}",
                        "{{..}}"
                    ]
                }
            }
        }
    })

    result = client.wait_for_task(
        task.task_uid,
        timeout_in_ms=120000,
        interval_in_ms=500
    )
    print(result)


def load_documents(json_file):
    with open(json_file, "r", encoding="utf-8") as file:
        docs = json.load(file)
    print(f"Loaded {len(docs)} documents.")
    return docs

def ingest_documents(docs):
    print(f"Ingesting {len(docs)} documents...")
    task = index.add_documents(docs)
    result = client.wait_for_task(
        task.task_uid,
        timeout_in_ms=120000,
        interval_in_ms=500
    )
    print(result)

if __name__ == "__main__":
    configure_meilisearch()
    documents = load_documents(
        JSON_FILE
    )
    ingest_documents(
        documents
    )