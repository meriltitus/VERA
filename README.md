# VERA — Verifiable Evidence & Reasoning Architecture

A local-first learning pipeline that transforms unstructured PDF documentation
into verified, citation-mapped knowledge assets using local AI.

## Stack
- Inference: Ollama (Llama 3 / Mistral) — fully local, no cloud APIs
- Vector Store: ChromaDB
- Pipeline: LangChain
- Frontend: Streamlit

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3
streamlit run ui/app.py
```
