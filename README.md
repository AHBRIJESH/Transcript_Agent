# Interview Transcript Agent

An AI-powered agent for searching and analyzing interview transcripts.

It takes raw interview transcripts, stores them in Meilisearch with embeddings, and lets you ask questions through a conversational UI. The agent uses **LangGraph + OpenRouter** and retrieves relevant transcript sections to provide evidence-based answers.

## Tech Stack

* **Python / FastAPI** – Backend APIs
* **Streamlit** – Chat UI
* **LangGraph** – Agent workflow
* **OpenRouter** – LLM (`ibm-granite/granite-4.2-8b`)
* **Meilisearch** – Hybrid search
* **Model2Vec** – Text embeddings

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your OpenRouter API key

Create a `.env` file:

```env
api_key="your_openrouter_api_key"
```

### 3. Add transcripts

Put your interview transcript files inside the `Data/` folder.

## Run

The easiest way is:

```bash
./start.sh
```

Then open:

```text
http://localhost:8501
```

### Docker

```bash
docker build -t transcript-agent .
docker run -p 8501:8501 -p 8000:8000 -p 8001:8001 -p 7700:7700 -p 7870:7870 transcript-agent

## What it can do

* Analyze interview transcripts
* Identify common themes and findings
* Search transcript content using semantic search
* Answer questions with relevant transcript evidence
* Provide timestamps and quotes
* Compare information across interviews
* Stream responses in real time
