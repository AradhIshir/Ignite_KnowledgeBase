"""Service for exporting knowledge items to various formats."""
from typing import List, Dict, Any
from io import BytesIO
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def to_csv(rows: List[Dict[str, Any]]) -> str:
    """Convert list of dictionaries to CSV format."""
    if not rows:
        return ""
    
    headers = list(rows[0].keys())
    out = [",".join([str(h) for h in headers])]
    
    for row in rows:
        out.append(
            ",".join([
                str(row.get(h, "")).replace("\n", " ").replace(",", ";")
                for h in headers
            ])
        )
    
    return "\n".join(out)


def to_pdf(items: List[Dict[str, Any]]) -> bytes:
    """Convert list of dictionaries to PDF format."""
    buffer = BytesIO()
    canvas_obj = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER
    
    def write_line(text: str, x: float, y: float, font_size: int = 11) -> float:
        """Write a line of text and return new y position."""
        canvas_obj.setFont("Helvetica", font_size)
        canvas_obj.drawString(x, y, text)
        return y
    
    y = height - 50
    canvas_obj.setFont("Helvetica-Bold", 16)
    canvas_obj.setFillColorRGB(0.115, 0.455, 0.961)  # #1D74F5
    canvas_obj.drawString(50, y, "Knowledge Export")
    canvas_obj.setFillColorRGB(0, 0, 0)
    y -= 24
    
    for item in items:
        if y < 100:
            canvas_obj.showPage()
            y = height - 50
        
        # Summary
        canvas_obj.setFont("Helvetica-Bold", 12)
        y = write_line(str(item.get("summary", "—")), 50, y)
        y -= 14
        
        # Metadata
        meta = (
            f"Project: {item.get('project', '—')} | "
            f"Source: {item.get('source', '—')} | "
            f"Date: {item.get('date', '—')}"
        )
        canvas_obj.setFont("Helvetica", 10)
        y = write_line(meta, 50, y)
        y -= 10
        
        # Topics
        topics = item.get("topics") or []
        if topics:
            y = write_line("Topics: " + ", ".join(map(str, topics)), 50, y)
            y -= 12
        
        # Decisions
        decisions = item.get("decisions") or []
        if decisions:
            y = write_line("Decisions:", 50, y)
            y -= 12
            for decision in decisions:
                y = write_line(f"• {decision}", 60, y)
                y -= 12
        
        # FAQs
        faqs = item.get("faqs") or []
        if faqs:
            y = write_line("FAQs:", 50, y)
            y -= 12
            for faq in faqs:
                y = write_line(f"• {faq}", 60, y)
                y -= 12
        
        # Raw text
        raw_text = item.get("raw_text")
        if raw_text:
            y = write_line("Original Content:", 50, y)
            y -= 12
            for line in str(raw_text).splitlines():
                if y < 80:
                    canvas_obj.showPage()
                    y = height - 50
                y = write_line(line[:110], 60, y)
                y -= 12
        
        y -= 16
    
    canvas_obj.save()
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

