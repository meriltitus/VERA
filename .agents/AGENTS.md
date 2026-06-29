# VERA Project Rules & Architecture Safeguards

To prevent past installation and user-experience issues reported by Andrew and testing users, all future modifications to VERA must strictly adhere to the following rules:

## 1. Zero-Friction Setup for Non-Technical Users
- **Automated Batch Launchers**: Always maintain `Install VERA.bat` and `Start VERA.bat` for 1-click execution on Windows.
- **Dependency Integrity**: Always ensure any new Python library added to the codebase is recorded in `requirements.txt` with minimum versions.
- **Fast Local Models**: Default model must remain lightweight and high-speed (`llama3.2:3b` and `nomic-embed-text`) to ensure CPU response times stay under 40 seconds on standard laptops.

## 2. Robust Error Handling & Ollama Protection
- **Ollama Guard**: Never crash the UI if Ollama is offline or un-served. Always catch connection errors gracefully and display user-friendly instructions.
- **Empty Document Safety**: Block queries cleanly with friendly notice if no documents are uploaded in ChromaDB.

## 3. Persistent UI & Split-Screen Stability
- **Layout Order Stability**: Document Viewer Panel (`doc_panel_col`) rendering code MUST be executed early in the Streamlit script lifecycle before streaming or reruns to prevent panel vanishing during question processing.
- **Multi-Format Ingestion**: Support all 9 document formats (`PDF, PPTX, PPT, DOCX, TXT, MD, PNG, JPG, JPEG`) directly in memory.
- **Responsive Typography & Spacing**: Keep chat cards compact (`max-width: 80-85%`), center-aligned main workspace (`max-width: 850px`), and preserve original theme colors (`#121013`, `#2A2326`, `#3B2A2F`, `#C8A4A8`, `#d4b8bc`).

## 4. Native Browser Downloads
- Always use `st.download_button` with in-memory byte streams (e.g. ReportLab PDF bytes) so browser native download dialogs handle file paths cleanly without OneDrive desktop confusion.
