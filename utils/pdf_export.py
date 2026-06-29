from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def safe_xml(text: str) -> str:
    """Escapes XML characters for ReportLab Paragraphs."""
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")

def generate_pdf_bytes(messages: list, ingested_files: list, mode: str = "Researcher") -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#3B2A2F"),
        spaceAfter=8
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#5C3A40"),
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#222222"),
        spaceAfter=6
    )
    user_style = ParagraphStyle(
        'DocUser',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1e2d4a"),
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=4
    )
    
    story = []
    story.append(Paragraph(f"VERA Study Session Summary ({safe_xml(mode)} Mode)", title_style))
    if ingested_files:
        files_str = safe_xml(", ".join(ingested_files))
        story.append(Paragraph(f"<b>Loaded Documents:</b> {files_str}", body_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#3B2A2F"), spaceAfter=15))
    
    for m in messages:
        if m["role"] == "user":
            q_text = safe_xml(m['content']['text'])
            story.append(Paragraph(f"❓ Question: {q_text}", user_style))
        elif m["role"] == "vera":
            ans_text = safe_xml(m['content'].get('answer', ''))
            story.append(Paragraph(f"💡 VERA Answer:", h2_style))
            story.append(Paragraph(ans_text, body_style))
            if m['content'].get('citations'):
                c_list = m['content']['citations']
                c_strs = []
                for c in c_list:
                    if isinstance(c, dict):
                        c_strs.append(c.get("label", ""))
                    else:
                        c_strs.append(str(c))
                story.append(Paragraph(f"<i>Sources: {safe_xml(', '.join(c_strs))}</i>", body_style))
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dddddd"), spaceAfter=10))
            
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
