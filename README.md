# VERA — Verifiable Evidence & Reasoning Architecture

VERA is a local AI assistant that reads your PDF documents and answers questions about them.
It runs **100% on your computer** — no internet required, no data sent anywhere.

---

## What you need before starting

| Requirement | Download link |
|---|---|
| Python 3.10 or higher | https://www.python.org/downloads/ |
| Git | https://git-scm.com/download/win |
| Ollama (local AI engine) | https://ollama.com/download |

---

## Setup (do this once)

### Step 1 — Download VERA

Open PowerShell and run:

```powershell
git clone https://github.com/meriltitus/VERA.git
cd VERA/vera
```

### Step 2 — Create the config file

In the `vera` folder, create a file called `.env` and paste this inside:

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_EMBED_MODEL=nomic-embed-text
CHROMA_PERSIST_DIR=./data/vectorstore
CHUNK_SIZE=512
CHUNK_OVERLAP=64
TOP_K_RESULTS=5
LOG_LEVEL=INFO
```

### Step 3 — Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If you get a security error, run this first then try again:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4 — Install dependencies

```powershell
pip install -r requirements.txt
pip install pydantic-settings==2.4.0
```

### Step 5 — Download the AI models (one time only, needs internet)

```powershell
ollama pull llama3
ollama pull nomic-embed-text
```

This downloads about 5GB total. Wait for both to finish.

---

## Running VERA

### Every time you want to use VERA:

**Terminal 1 — Start the AI engine:**
```powershell
ollama serve
```
Leave this running. Open a second PowerShell window for the next step.

**Terminal 2 — Start VERA:**
```powershell
cd C:\path\to\VERA\vera
.venv\Scripts\Activate.ps1
streamlit run ui/app.py
```

Your browser will open automatically at `http://localhost:8501`

---

## Using VERA

1. Click **Browse files** in the left sidebar
2. Upload any PDF (textbook, report, research paper)
3. Wait for the green "✅ chunks added" message
4. Type your question in the box at the bottom
5. Click **Ask →**

VERA will answer your question and show exactly which page of which PDF it got the answer from.

---

## Example questions

- `What is Kerberos?`
- `How does mutual authentication work?`
- `Summarize this document`
- `What are the types of encryption mentioned?`

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "ollama is not recognized" | Install Ollama from https://ollama.com/download and reopen PowerShell |
| "Something went wrong" in VERA | Make sure `ollama serve` is running in a separate terminal |
| Slow responses | Normal — Llama 3 runs on your CPU. Responses take 30–90 seconds |
| Port already in use | Run `streamlit run ui/app.py --server.port 8502` |

---

## Tech stack

- **LLM:** Llama 3 via Ollama (fully local)
- **Embeddings:** nomic-embed-text via Ollama
- **Vector store:** ChromaDB
- **Pipeline:** LangChain
- **Frontend:** Streamlit
- **Language:** Python

