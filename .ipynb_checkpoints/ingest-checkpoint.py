import json
import os
import requests
import meilisearch

MEILI_URL = "http://127.0.0.1:7700"
INDEX_NAME = "Industry_Data"

client = meilisearch.Client(MEILI_URL,"password")
index = client.index(INDEX_NAME)

print("Configuring embedder...")

task = index.update_settings({
    "embedders": {
        "hf-inference": {
            "source": "rest",
            "url":  "http://host.docker.internal:7870/embed",
            "dimensions": 256,
            "documentTemplate": "{{doc.title}}\n{{doc.text}}",
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

print("Embedder configured.")

with open("website_data_clean.json", "r") as f:
    docs = json.load(f)

print(f"Ingesting {len(docs)} documents...")

task = index.add_documents(docs)

result = client.wait_for_task(
    task.task_uid,
    timeout_in_ms=120000,
    interval_in_ms=500
)

print(result)
print("Documents indexed successfully.")