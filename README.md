# VERA — Verifiable Evidence & Reasoning Architecture

VERA is a local AI assistant that reads your documents and answers questions about them. It runs **100% on your computer** — no internet required after setup, no data sent anywhere, completely private.

**Two ways to get started — pick the one that fits you:**

---

## Option A — Non-Technical Users (Recommended)

No coding required. Just follow these steps.

### What you need to install first (one time only)

| Software | Why | Download |
|---|---|---|
| Python 3.10+ | Runs the app | https://www.python.org/downloads/ |
| Ollama | Powers the AI | https://ollama.com/download |
| Git (optional) | To download VERA | https://git-scm.com/download/win |

> **Important when installing Python:** Check the box that says **"Add Python to PATH"** before clicking Install.

---

### Step 1 — Download VERA

Click the green **Code** button on this page → **Download ZIP** → Extract it anywhere on your computer (Desktop is fine).

Or if you have Git:
```
git clone https://github.com/meriltitus/VERA.git
```

---

### Step 2 — Install (one time only)

Open the extracted folder. Double-click **`Install VERA.bat`**.

- It will check that Python and Ollama are installed
- If Ollama is missing, it will open the download page for you automatically
- It will download the AI models (~5GB — takes 10–15 minutes on first run)
- It will set up everything else automatically

When it says **"Installation complete"** you are done with this step forever.

---

### Step 3 — Launch VERA (every time)

Double-click **`Start VERA.bat`**.

Your browser will open automatically with VERA ready to use.

---

### How to use VERA

1. Click **Browse files** in the left sidebar
2. Upload a PDF or PowerPoint file
3. Wait for the green confirmation message
4. Type your question in the box at the bottom and click **Ask →**

**Two modes available:**
- **Researcher** — Ask questions, get answers with citations
- **Devil's Advocate** — VERA tests your understanding like a tutor

---

### Troubleshooting

| Problem | Fix |
|---|---|
| "Python is not installed" | Download from python.org. Check "Add to PATH" during install |
| "Ollama is not installed" | The installer will open the download page automatically |
| Browser doesn't open | Go to http://localhost:8501 manually |
| Slow answers | Normal — AI runs on your CPU. Takes 30–90 seconds |
| "VERA could not process" | Make sure you ran Start VERA.bat, not app.py directly |

---

## Option B — Developers

### Requirements
- Python 3.10+
- Ollama installed and running
- Git

### Setup

```bash
git clone https://github.com/meriltitus/VERA.git
cd VERA/vera

python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
pip install pydantic-settings==2.4.0 python-pptx==0.6.23
```

### Configure

Copy `.env.example` to `.env` — no changes needed for default setup.

### Download AI models

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

### Run

```bash
# Terminal 1
ollama serve

# Terminal 2
streamlit run ui/app.py
```

Open http://localhost:8501

---

## Architecture

```
vera/
├── ingestion/       # PDF + PPTX loader, chunker, embedder
├── router/          # Query classifier and handler
├── aggregator/      # LLM synthesizer, citation mapper
├── vectorstore/     # ChromaDB retriever
├── ui/              # Streamlit frontend
└── utils/           # Config, logger
```

**Stack:** Llama 3 · nomic-embed-text · ChromaDB · LangChain · Streamlit · Python

**Privacy:** All processing is local. No data leaves your machine. No API keys required.

---

## V1.1 Roadmap
- PDF page viewer on citation click
- Mastery Export — generate a study summary PDF after Devil's Advocate sessions
- Persistent document library
- Word document (.docx) support
- Image upload with OCR

---

*Built by Meril Titus — github.com/meriltitus/VERA*
