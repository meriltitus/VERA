import sys
import os
import tempfile
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vera_main import ask_vera
from ingestion.pipeline import run_ingestion
from vectorstore.retriever import get_chroma_collection

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="VERA",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #0f1117; color: #e2e8f0; }
[data-testid="stSidebar"] { background: #161b27; border-right: 1px solid #1e2535; }

.vera-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px; font-weight: 500;
    color: #7c9ef8; letter-spacing: 3px;
    padding: 8px 0 4px 0;
}
.vera-tagline {
    font-size: 11px; color: #4a5568;
    letter-spacing: 1px; text-transform: uppercase;
    margin-bottom: 20px;
    border-bottom: 1px solid #1e2535;
    padding-bottom: 16px;
}
.msg-user {
    background: #1a2035; border: 1px solid #1e2d4a;
    border-radius: 12px 12px 4px 12px;
    padding: 14px 18px; margin: 8px 0; margin-left: 15%;
    color: #cbd5e1; font-size: 14px; line-height: 1.6;
}
.msg-vera {
    background: #131922; border: 1px solid #1e2535;
    border-left: 3px solid #7c9ef8;
    border-radius: 4px 12px 12px 12px;
    padding: 16px 18px; margin: 8px 0; margin-right: 10%;
    color: #e2e8f0; font-size: 14px; line-height: 1.7;
}
.msg-label { font-size: 10px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; }
.label-user { color: #4a90d9; }
.label-vera { color: #7c9ef8; }

.qtype-badge {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 10px; font-weight: 600; letter-spacing: 1px;
    text-transform: uppercase; margin-bottom: 10px;
}
.qtype-factual    { background: #1a2f1a; color: #68d391; border: 1px solid #276749; }
.qtype-conceptual { background: #1a2035; color: #7c9ef8; border: 1px solid #2c4a8c; }
.qtype-summary    { background: #2d1f1a; color: #f6ad55; border: 1px solid #7b4a1e; }

.citations-block { margin-top: 14px; padding-top: 12px; border-top: 1px solid #1e2535; }
.citations-title { font-size: 10px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: #4a5568; margin-bottom: 8px; }
.citation-pill {
    display: inline-block; background: #1a2035; border: 1px solid #2d3748;
    border-radius: 20px; padding: 3px 12px; font-size: 11px;
    font-family: 'JetBrains Mono', monospace; color: #7c9ef8; margin: 3px 4px 3px 0;
}
.stat-card { background: #161b27; border: 1px solid #1e2535; border-radius: 8px; padding: 12px 16px; margin: 6px 0; }
.stat-value { font-family: 'JetBrains Mono', monospace; font-size: 20px; font-weight: 500; color: #7c9ef8; }
.stat-label { font-size: 11px; color: #4a5568; margin-top: 2px; }

.stTextInput > div > div > input {
    background: #161b27 !important; border: 1px solid #1e2535 !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #7c9ef8 !important; box-shadow: 0 0 0 1px #7c9ef8 !important;
}
.stButton > button {
    background: #1a2035 !important; border: 1px solid #2d3a5c !important;
    color: #7c9ef8 !important; border-radius: 8px !important; font-weight: 500 !important;
}
.stButton > button:hover { background: #7c9ef8 !important; color: #0f1117 !important; }
hr { border-color: #1e2535 !important; }
.upload-hint { font-size: 12px; color: #4a5568; text-align: center; padding: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ───────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ingested_files" not in st.session_state:
    st.session_state.ingested_files = []
if "last_question" not in st.session_state:
    st.session_state.last_question = ""

# ── Helpers ──────────────────────────────────────────────────
def get_chunk_count() -> int:
    try:
        return get_chroma_collection().count()
    except:
        return 0

def render_message(role: str, content: dict):
    if role == "user":
        st.markdown(f"""
        <div class="msg-user">
            <div class="msg-label label-user">You</div>
            {content['text']}
        </div>""", unsafe_allow_html=True)
    else:
        badge_class = f"qtype-{content.get('query_type', 'conceptual')}"
        badge_text = content.get('query_type', 'conceptual').upper()

        # Build citations HTML safely
        citations_html = ""
        if content.get("citations"):
            pills = "".join(
                f'<span class="citation-pill">{c}</span>'
                for c in content["citations"]
            )
            citations_html = f'<div class="citations-block"><div class="citations-title">📌 Sources</div>{pills}</div>'

        # Escape answer text to prevent HTML injection
        answer = content.get('answer', '').replace('<', '&lt;').replace('>', '&gt;')

        st.markdown(f"""
        <div class="msg-vera">
            <div class="msg-label label-vera">VERA</div>
            <span class="qtype-badge {badge_class}">{badge_text}</span>
            <div style="white-space:pre-wrap">{answer}</div>
            {citations_html}
        </div>""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="vera-logo">VERA</div>', unsafe_allow_html=True)
    st.markdown('<div class="vera-tagline">Verifiable Evidence & Reasoning</div>', unsafe_allow_html=True)

    chunk_count = get_chunk_count()
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{chunk_count}</div>
        <div class="stat-label">Chunks in knowledge base</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{len(st.session_state.ingested_files)}</div>
        <div class="stat-label">Documents loaded this session</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**Upload a document**")

    uploaded_file = st.file_uploader(
        "Drop a PDF here", type=["pdf"], label_visibility="collapsed"
    )

    if uploaded_file and uploaded_file.name not in st.session_state.ingested_files:
        with st.spinner(f"Ingesting {uploaded_file.name}..."):
            # Write to temp file but keep the real filename for citations
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            try:
                result = run_ingestion(tmp_path, real_filename=uploaded_file.name)
                st.session_state.ingested_files.append(uploaded_file.name)
                st.success(f"✅ {uploaded_file.name} — {result['chunks_stored']} chunks added")
            except Exception as e:
                st.error(f"Ingestion failed: {e}")
            finally:
                os.unlink(tmp_path)

    st.markdown("<div class='upload-hint'>PDF is processed locally.<br>Nothing leaves your machine.</div>", unsafe_allow_html=True)

    if st.session_state.ingested_files:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("**Loaded documents**")
        for f in st.session_state.ingested_files:
            st.markdown(f"📄 `{f}`")

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("🗑 Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_question = ""
        st.rerun()

    st.markdown("<div class='upload-hint'>Llama 3 · nomic-embed-text · ChromaDB<br>100% local · no cloud APIs</div>", unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────
st.markdown("""
<div style="padding: 8px 0 20px 0;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:500;color:#7c9ef8;letter-spacing:4px;">VERA</span>
    <span style="font-size:13px;color:#4a5568;margin-left:14px;">Ask anything about your documents</span>
</div>
""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#2d3748;">
        <div style="font-size:48px;margin-bottom:16px;">🔍</div>
        <div style="font-size:16px;color:#4a5568;margin-bottom:8px;">No questions yet</div>
        <div style="font-size:13px;color:#2d3748;">Upload a PDF in the sidebar, then ask a question below.</div>
    </div>
    """, unsafe_allow_html=True)

# Render chat history
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

# ── Input — using a form to prevent rerun loop ────────────────
with st.form(key="question_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Ask a question",
            placeholder="e.g. What is Kerberos? / How does mutual authentication work? / Summarize this document",
            label_visibility="collapsed",
        )
    with col2:
        submitted = st.form_submit_button("Ask →", use_container_width=True)

# Handle submission — only fires once per submit
if submitted and user_input.strip():
    question = user_input.strip()

    st.session_state.messages.append({
        "role": "user",
        "content": {"text": question}
    })

    with st.spinner("VERA is thinking..."):
        try:
            result = ask_vera(question)
            st.session_state.messages.append({
                "role": "vera",
                "content": result,
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "vera",
                "content": {
                    "answer": f"Something went wrong: {str(e)}\n\nMake sure Ollama is running (ollama serve) and a PDF has been ingested.",
                    "citations": [],
                    "query_type": "factual",
                    "chunks_used": 0,
                }
            })
    st.rerun()
