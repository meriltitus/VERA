# VERA — Verifiable Evidence & Reasoning Architecture

VERA is an advanced local AI assistant that reads your documents and answers questions about them. It runs **100% on your computer** — no internet required after setup, no data sent anywhere, completely private and local-first.

**Supported File Formats (9 Formats):**
`PDF` · `PPTX` · `PPT` · `DOCX` · `TXT` · `MD` · `PNG` · `JPG` · `JPEG` (Image OCR)

---

## 🚀 Features in VERA 

- **⚡ Fast Response Engine (`llama3.2:3b`)**: 3-4x faster answer generation under 40 seconds.
- **🌊 Real-Time Token Streaming**: Watch words stream live on screen in 1–2 seconds.
- **🎯 Dynamic Devil's Advocate Mode**: Adaptive AI tutor that tests your understanding and tracks study progress.
- **📌 Citation Hover Snippet Preview**: Rich tooltips displaying exact extracted document text excerpts.
- **📑 Claude-Style Collapsible Attachments**: Clean, expandable document indicators in chat.
- **📥 Mastery PDF Exporter**: One-click export to download complete study session guides as PDFs.
- **🖥️ Right-Side Split-Screen Panel**: Side-by-side split screen viewer for chat and study material.
- **⚡ Zero-Duplication Vector Storage**: MD5 content hashing preventing duplicate chunk storage.
- **📷 Image Upload OCR**: Automatic text extraction from photos, notes, and diagrams (`.png`, `.jpg`, `.jpeg`).

---

## Option A — Non-Technical Users (Recommended)

No coding required. Just follow these steps.

### What you need to install first (one time only)

| Software | Why | Download |
|---|---|---|
| Python 3.10+ | Runs the app | https://www.python.org/downloads/ |
| Ollama | Powers the local AI models | https://ollama.com/download |
| Git (optional) | To download VERA | https://git-scm.com/download/win |

> **Important when installing Python:** Check the box that says **"Add Python to PATH"** before clicking Install.

---

### Step 1 — Download VERA

Click the green **Code** button on this page → **Download ZIP** → Extract it anywhere on your computer (Desktop is fine).

Or if you have Git:
```bash
git clone https://github.com/meriltitus/VERA.git
```

---

### Step 2 — Install (one time only)

Open the extracted folder. Double-click **`Install VERA.bat`**.

- It will check that Python and Ollama are installed
- It will download the fast AI models (`llama3.2:3b` and `nomic-embed-text`)
- It will set up all dependencies automatically

When it says **"Installation complete"** you are done with this step forever.

---

### Step 3 — Launch VERA (every time)

Double-click **`Start VERA.bat`**. Your browser will open automatically at `http://localhost:8501`.

---

## Option B — Developers

### Requirements
- Python 3.10+
- Ollama installed and running
- Git

### Setup

```bash
git clone https://github.com/meriltitus/VERA.git
cd VERA

python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### Download AI models

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### Run

```bash
streamlit run ui/app.py
```

Open http://localhost:8501

---

## Architecture

```
vera/
├── ingestion/       # PDF, PPTX, DOCX, TXT, MD, OCR loader & chunker
├── router/          # Query classifier and handler
├── aggregator/      # Real-time LLM synthesizer & citation mapper
├── vectorstore/     # ChromaDB retriever & zero-duplication engine
├── ui/              # Streamlit frontend & split-screen panel
└── utils/           # Config, logger, PDF export generator
```

**Stack:** Llama 3.2 (3B) · nomic-embed-text · ChromaDB · LangChain · ReportLab · Streamlit · Python

**Privacy:** All processing is local. No data leaves your machine. No API keys required.

---

*Built by Meril Titus — github.com/meriltitus/VERA*

