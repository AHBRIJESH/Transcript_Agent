#!/bin/sh
set -e

echo "=========================================="
echo " Starting Transcript Agent"
echo "=========================================="

echo ""
echo "Starting embedding server..."

python embeder.py &
EMBED_PID=$!

echo "Embedding PID: $EMBED_PID"
echo "Waiting for embedding server on port 7870..."

until curl -sf http://127.0.0.1:7870/health >/dev/null; do
    sleep 1
done

echo "Embedding server is ready."

echo ""
echo "Testing embedding endpoint..."

curl -s -X POST \
    http://127.0.0.1:7870/embed \
    -H "Content-Type: application/json" \
    -d '{"inputs":["test embedding"]}'

echo ""
echo "Embedding endpoint test completed."

echo ""
echo "Starting Meilisearch..."

export MEILI_EXPERIMENTAL_ALLOWED_IP_NETWORKS=any

./meilisearch \
    --http-addr 0.0.0.0:7700 &

MEILI_PID=$!

echo "Meilisearch PID: $MEILI_PID"
echo "Waiting for Meilisearch on port 7700..."

until curl -sf http://127.0.0.1:7700/health >/dev/null; do
    sleep 1
done

echo "Meilisearch is ready."

echo ""
echo "=========================================="
echo " Formatting data"
echo "=========================================="

python format_data.py

echo ""
echo "Data formatting completed."

echo ""
echo "=========================================="
echo " Starting ingestion"
echo "=========================================="

python ingest.py

echo ""
echo "Ingestion completed."

echo ""
echo "=========================================="
echo " Starting Retriever"
echo "=========================================="

python retriver.py &
RETRIEVER_PID=$!

echo "Retriever PID: $RETRIEVER_PID"
echo "Waiting for Retriever on port 8001..."

until curl -sf http://127.0.0.1:8001/health >/dev/null; do
    sleep 1
done

echo "Retriever is ready."

echo ""
echo "=========================================="
echo " Starting App"
echo "=========================================="

python app.py &
APP_PID=$!

echo "App PID: $APP_PID"
echo "Waiting for App on port 8000..."

while true; do
    APP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        http://127.0.0.1:8000/health || true)

    if [ "$APP_STATUS" != "000" ]; then
        echo "App is responding with HTTP $APP_STATUS"
        break
    fi

    sleep 1
done

echo "App is ready."

echo ""
echo "=========================================="
echo " Starting Streamlit"
echo "=========================================="

streamlit run streamlit_app.py \
    --server.address 0.0.0.0 \
    --server.port 8501 &

STREAMLIT_PID=$!

echo ""
echo "=========================================="
echo " ALL SERVICES STARTED"
echo "=========================================="
echo ""
echo "Embedding  : 7870"
echo "Meilisearch: 7700"
echo "Retriever  : 8001"
echo "App        : 8000"
echo "Streamlit  : 8501"
echo ""

trap '
kill $EMBED_PID $MEILI_PID $RETRIEVER_PID $APP_PID $STREAMLIT_PID 2>/dev/null || true
' EXIT

wait