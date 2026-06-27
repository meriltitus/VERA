import sys
import os
import tempfile
import shutil
from pathlib import Path
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vera_main import ask_vera
from ingestion.pipeline import run_ingestion
from vectorstore.retriever import get_chroma_collection

st.set_page_config(
    page_title="VERA",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #1E1A1B; color: #d4b8bc; }
[data-testid="stSidebar"] { background: #2A2326; border-right: 1px solid #3B2A2F; }

/* Hide "Press Enter to submit" */
.stForm small, [data-testid="InputInstructions"] { display: none !important; }

.vera-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px; font-weight: 500;
    color: #C8A4A8; letter-spacing: 3px; padding: 8px 0 2px 0;
}
.vera-tagline {
    font-size: 11px; color: #5C3A40; letter-spacing: 1px;
    text-transform: uppercase; padding-bottom: 16px;
    border-bottom: 1px solid #3B2A2F; margin-bottom: 16px;
}

/* Dashboard cards */
.dash-section { margin-bottom: 20px; }
.dash-title { font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: #5C3A40; margin-bottom: 10px; }
.doc-card {
    background: #2A2326; border: 1px solid #3B2A2F; border-radius: 10px;
    padding: 10px 14px; margin: 6px 0; display: flex; align-items: center; gap: 10px;
}
.doc-icon { font-size: 18px; }
.doc-info { flex: 1; }
.doc-name { font-size: 13px; color: #C8A4A8; font-weight: 500; }
.doc-meta { font-size: 11px; color: #5C3A40; margin-top: 2px; }

/* Status badge */
.status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.status-ready { background: #68d391; box-shadow: 0 0 6px #68d391; }
.status-empty { background: #f6ad55; box-shadow: 0 0 6px #f6ad55; }
.status-bar {
    display: flex; align-items: center; gap: 8px;
    font-size: 12px; color: #8A5A61; padding: 8px 0;
}

/* Chat messages */
.msg-user {
    background: #3B2A2F; border: 1px solid #1e2d4a;
    border-radius: 12px 12px 4px 12px;
    padding: 14px 18px; margin: 8px 0; margin-left: 20%;
    color: #C8A4A8; font-size: 14px; line-height: 1.6;
}
.msg-vera {
    background: #231f20; border: 1px solid #3B2A2F;
    border-left: 3px solid #C8A4A8;
    border-radius: 4px 12px 12px 12px;
    padding: 16px 20px; margin: 8px 0; margin-right: 10%;
    color: #d4b8bc; font-size: 14px; line-height: 1.8;
}
.msg-error {
    background: #1a1020; border: 1px solid #4a2035;
    border-left: 3px solid #fc8181;
    border-radius: 4px 12px 12px 12px;
    padding: 14px 18px; margin: 8px 0; margin-right: 10%;
    color: #fc8181; font-size: 13px; line-height: 1.6;
}
.msg-thinking {
    background: #231f20; border: 1px solid #3B2A2F;
    border-left: 3px solid #5C3A40;
    border-radius: 4px 12px 12px 12px;
    padding: 14px 18px; margin: 8px 0; margin-right: 10%;
    color: #5C3A40; font-size: 13px;
}
.msg-label { font-size: 10px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; }
.label-user { color: #8A5A61; }
.label-vera { color: #C8A4A8; }
.label-error { color: #fc8181; }

/* Citations */
.citations-block { margin-top: 14px; padding-top: 12px; border-top: 1px solid #3B2A2F; }
.citations-title { font-size: 10px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: #5C3A40; margin-bottom: 8px; }
.citation-wrap { position: relative; display: inline-block; margin: 3px 4px 3px 0; }
.citation-pill {
    display: inline-block; background: #3B2A2F; border: 1px solid #5C3A40;
    border-radius: 20px; padding: 3px 12px; font-size: 11px;
    font-family: 'JetBrains Mono', monospace; color: #C8A4A8; cursor: default;
}
.citation-tooltip {
    display: none; position: absolute; bottom: 130%; left: 50%;
    transform: translateX(-50%);
    background: #3B2A2F; border: 1px solid #5C3A40; border-radius: 8px;
    padding: 8px 12px; font-size: 11px; color: #C8A4A8;
    white-space: nowrap; z-index: 100;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
.citation-tooltip::after {
    content: ''; position: absolute; top: 100%; left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent; border-top-color: #5C3A40;
}
.citation-wrap:hover .citation-pill { background: #5C3A40; border-color: #C8A4A8; }
.citation-wrap:hover .citation-tooltip { display: block; }

/* Input area */
.stTextInput > div > div > input {
    background: #2A2326 !important; border: 1px solid #3B2A2F !important;
    border-radius: 10px !important; color: #d4b8bc !important;
    font-size: 14px !important; padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus { border-color: #C8A4A8 !important; box-shadow: none !important; }
.stTextInput > div > div > input::placeholder { color: #5C3A40 !important; }

/* Ask button — small */
.stFormSubmitButton > button {
    background: #C8A4A8 !important; border: none !important;
    color: #1E1A1B !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 13px !important;
    padding: 8px 16px !important; height: 44px !important;
    width: auto !important;
}
.stFormSubmitButton > button:hover { background: #a0b4ff !important; }

.stButton > button {
    background: #2A2326 !important; border: 1px solid #3B2A2F !important;
    color: #8A5A61 !important; border-radius: 8px !important;
    font-size: 12px !important;
}
.stButton > button:hover { border-color: #C8A4A8 !important; color: #C8A4A8 !important; }

hr { border-color: #3B2A2F !important; }
.stToggle { font-size: 12px !important; }
/* Scroll to bottom arrow */
.scroll-btn {
    position: fixed; bottom: 90px; right: 24px;
    width: 36px; height: 36px; border-radius: 50%;
    background: #3B2A2F; border: 0.5px solid #5C3A40;
    color: #C8A4A8; font-size: 16px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    z-index: 999; box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    transition: all 0.15s;
}
.scroll-btn:hover { background: #5C3A40; }
/* Tighten radio button spacing */
[data-testid="stRadio"] > div { gap: 4px !important; }
[data-testid="stRadio"] label { padding: 4px 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
# Wipe ChromaDB on every fresh app start

for key, default in [
    ("messages", []),
    ("ingested_files", []),
    ("save_session", False),
    ("pending_question", None),
    ("last_mode", "Researcher"),
    ("da_active", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Helpers ───────────────────────────────────────────────────
def get_chunk_count() -> int:
    try:
        return get_chroma_collection().count()
    except:
        return 0

def clear_vectorstore():
    from utils.config import get_settings
    cfg = get_settings()
    try:
        persist_path = Path(cfg.chroma_persist_dir).resolve()
        if persist_path.exists():
            shutil.rmtree(persist_path)
            persist_path.mkdir(parents=True, exist_ok=True)
    except:
        pass
    
if "app_initialized" not in st.session_state:
    clear_vectorstore()
    st.session_state["app_initialized"] = True


def safe_html(text: str) -> str:
    """Escape text so it never breaks HTML rendering."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_citations(citations):
    if not citations:
        return ""
    pills = ""
    for c in citations:
        tip = c.split("] ", 1)[-1] if "] " in c else c
        pills += f'''<span class="citation-wrap">
            <span class="citation-pill">{safe_html(c)}</span>
            <span class="citation-tooltip">📄 {safe_html(tip)}</span>
        </span>'''
    return f'<div class="citations-block"><div class="citations-title">📌 Sources — hover for details</div>{pills}</div>'

def render_message(role: str, content: dict):
    if role == "user":
        st.markdown(f'<div class="msg-user"><div class="msg-label label-user">You</div>{safe_html(content["text"])}</div>', unsafe_allow_html=True)
    elif role == "thinking":
        thinking_placeholder = st.empty()
        for frame in ["⏳", "⌛", "⏳", "⌛"]:
            thinking_placeholder.markdown(f'<div class="msg-thinking"><div class="msg-label label-vera">VERA</div>{frame} Thinking about your question...</div>', unsafe_allow_html=True)
            import time; time.sleep(0.4)
    elif role == "error":
        st.markdown(f'<div class="msg-error"><div class="msg-label label-error">VERA</div>{safe_html(content["text"])}</div>', unsafe_allow_html=True)
    else:
        citations_html = render_citations(content.get("citations", []))
        answer = safe_html(content.get("answer", ""))
        st.markdown(f'<div class="msg-vera"><div class="msg-label label-vera">VERA</div><div style="white-space:pre-wrap">{answer}</div>{citations_html}</div>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="vera-logo">VERA</div>', unsafe_allow_html=True)
    st.markdown('<div class="vera-tagline">Verifiable Evidence &amp; Reasoning Architecture</div>', unsafe_allow_html=True)

    # Status indicator
    has_docs = len(st.session_state.ingested_files) > 0
    if has_docs:
        status_html = '<div class="status-bar"><span class="status-dot status-ready"></span>Ready to answer questions</div>'
    else:
        status_html = '<div class="status-bar"><span class="status-dot status-empty"></span>Upload a document to get started</div>'
    st.markdown(status_html, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Mode toggle
    st.markdown('<div class="dash-title">Mode</div>', unsafe_allow_html=True)
    mode = st.radio(
    "mode",
    options=["Researcher", "Devil's Advocate"],
    label_visibility="collapsed",
    key="vera_mode",
    )
    # Detect mode switch
    current_mode = st.session_state.get("vera_mode", "Researcher")
    prev_mode = st.session_state.get("last_mode", "Researcher")
    if current_mode != prev_mode:
        st.session_state.last_mode = current_mode
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.session_state.da_active = (current_mode == "Devil's Advocate")
        st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)

    # Loaded documents dashboard
    if st.session_state.ingested_files:
        st.markdown('<div class="dash-title">📂 Your documents</div>', unsafe_allow_html=True)
        for f in st.session_state.ingested_files:
            ext = Path(f).suffix.lower()
            icon = "📄" if ext == ".pdf" else "📊"
            type_label = "PDF Document" if ext == ".pdf" else "PowerPoint"
            st.markdown(f'''<div class="doc-card">
                <div class="doc-icon">{icon}</div>
                <div class="doc-info">
                    <div class="doc-name">{safe_html(f)}</div>
                    <div class="doc-meta">{type_label} · Ready</div>
                </div>
            </div>''', unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

    # Upload
    st.markdown('<div class="dash-title">➕ Add documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload",
        type=["pdf", "pptx", "ppt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        for uf in uploaded_files:
            if uf.name not in st.session_state.ingested_files:
                with st.spinner(f"Reading {uf.name}..."):
                    suffix = Path(uf.name).suffix
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uf.read())
                        tmp_path = tmp.name
                    try:
                        result = run_ingestion(tmp_path, real_filename=uf.name)
                        st.session_state.ingested_files.append(uf.name)
                        st.success(f"✅ {uf.name} added")
                    except Exception as e:
                        st.error(f"❌ Could not read {uf.name}")
                    finally:
                        os.unlink(tmp_path)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Session settings
    st.session_state.save_session = False

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑 Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.rerun()
    with col2:
        if st.button("🔄 New session", use_container_width=True):
            if not st.session_state.save_session:
                clear_vectorstore()
            st.session_state.messages = []
            st.session_state.ingested_files = []
            st.session_state.pending_question = None
            st.rerun()

# ── Main ──────────────────────────────────────────────────────
st.markdown('''<div style="padding:8px 0 24px 0; border-bottom: 1px solid #3B2A2F; margin-bottom: 24px; display:flex; align-items:center; justify-content:space-between;">
    <span style="font-size:13px;color:#5C3A40;">Ask anything about your documents</span>
    <span style="font-size:10px;padding:3px 12px;border-radius:20px;background:#3B2A2F;color:#C8A4A8;border:0.5px solid #5C3A40;">{}</span>
</div>'''.format(st.session_state.get("vera_mode", "Researcher")), unsafe_allow_html=True)

# Welcome / empty state
if not st.session_state.messages and not st.session_state.pending_question:
    if not has_docs:
        st.markdown('''<div style="text-align:center;padding:80px 20px;">
            <div style="font-size:52px;margin-bottom:20px;">📂</div>
            <div style="font-size:18px;color:#5C3A40;font-weight:500;margin-bottom:10px;">No documents uploaded yet</div>
            <div style="font-size:13px;color:#5C3A40;">Upload a PDF or PowerPoint in the sidebar to get started.<br>VERA will read it and answer your questions.</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown('''<div style="text-align:center;padding:80px 20px;">
            <div style="font-size:52px;margin-bottom:20px;">💬</div>
            <div style="font-size:18px;color:#5C3A40;font-weight:500;margin-bottom:10px;">Ready for your questions</div>
            <div style="font-size:13px;color:#5C3A40;">Type a question below about your uploaded documents.</div>
        </div>''', unsafe_allow_html=True)

# Devil's Advocate opening message
if st.session_state.get("da_active") and not st.session_state.messages:
    docs = st.session_state.ingested_files
    if docs:
        doc_list = ", ".join(docs)
        opener = f"I've read your documents: **{doc_list}**. What topic would you like to be tested on? You can name a specific concept, or I can pick one for you."
    else:
        opener = "No documents are uploaded yet. Please upload a PDF or PowerPoint first, then switch to Devil's Advocate mode."
    st.session_state.messages.append({
        "role": "vera",
        "content": {
            "answer": opener,
            "citations": [],
            "chunks_used": 0,
        }
    })
    st.session_state.da_active = False
    st.rerun()

# Render chat history
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

# Handle pending question
if st.session_state.pending_question:
    question = st.session_state.pending_question

    render_message("user", {"text": question})
    render_message("thinking", {})

    # Check if any documents are loaded
    if get_chunk_count() == 0:
        st.session_state.messages.append({"role": "user", "content": {"text": question}})
        st.session_state.messages.append({"role": "error", "content": {
            "text": "No documents have been uploaded yet. Please upload a PDF or PowerPoint file using the sidebar before asking questions."
        }})
    else:
        try:
            result = ask_vera(
                question,
                mode=st.session_state.get("vera_mode", "Researcher"),
                chat_history=st.session_state.messages,
            )
            st.session_state.messages.append({"role": "user", "content": {"text": question}})
            st.session_state.messages.append({"role": "vera", "content": result})
        except Exception as e:
            err = str(e)
            st.session_state.messages.append({"role": "user", "content": {"text": question}})
            st.session_state.messages.append({"role": "error", "content": {
                "text": "VERA could not process your question. Please make sure Ollama is running in the background."
            }})

    st.session_state.pending_question = None
    st.rerun()

# Input
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
with st.form(key="qform", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_input(
            "q",
            placeholder="Ask a question about your documents...",
            label_visibility="collapsed",
        )
    with col2:
        submitted = st.form_submit_button("Ask →")

if submitted and user_input.strip():
    st.session_state.pending_question = user_input.strip()
    st.rerun()

# Auto-scroll to bottom + scroll arrow
st.markdown("""
<button class="scroll-btn" onclick="
    var container = window.parent.document.querySelector('.main');
    if(container) container.scrollTop = container.scrollHeight;
">↓</button>
<script>
    setTimeout(function() {
        var container = window.parent.document.querySelector('.main');
        if(container) container.scrollTop = container.scrollHeight;
    }, 300);
</script>
""", unsafe_allow_html=True)