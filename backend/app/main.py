from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import orjson
from io import BytesIO
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from fastapi.responses import RedirectResponse


class ExportRequest(BaseModel):
    filename: str
    format: str  # 'pdf' or 'csv'
    items: list[dict]


def to_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    headers = list(rows[0].keys())
    out = [",".join([str(h) for h in headers])]
    for row in rows:
        out.append(
            ",".join([str(row.get(h, "")).replace("\n", " ").replace(",", ";") for h in headers])
        )
    return "\n".join(out)


app = FastAPI(title="Ignite Knowledge Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    # Redirect to interactive docs for convenience
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/export")
def export_items(req: ExportRequest):
    if req.format not in {"pdf", "csv"}:
        raise HTTPException(status_code=400, detail="Unsupported format")

    if req.format == "csv":
        csv_body = to_csv(req.items)
        return {
            "filename": req.filename if req.filename.endswith(".csv") else f"{req.filename}.csv",
            "mime": "text/csv",
            "body": csv_body,
        }

    # PDF render via ReportLab (no system deps)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    def write_line(text: str, x: float, y: float, font_size: int = 11):
        c.setFont("Helvetica", font_size)
        c.drawString(x, y, text)
        return y

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0.115, 0.455, 0.961)  # #1D74F5
    c.drawString(50, y, "Knowledge Export")
    c.setFillColorRGB(0, 0, 0)
    y -= 24

    for it in req.items:
        if y < 100:
            c.showPage()
            y = height - 50
        c.setFont("Helvetica-Bold", 12)
        y = write_line(str(it.get("summary", "—")), 50, y)
        y -= 14
        meta = f"Project: {it.get('project','—')} | Source: {it.get('source','—')} | Date: {it.get('date','—')}"
        c.setFont("Helvetica", 10)
        y = write_line(meta, 50, y)
        y -= 10
        topics = it.get("topics") or []
        if topics:
            y = write_line("Topics: " + ", ".join(map(str, topics)), 50, y)
            y -= 12
        decisions = it.get("decisions") or []
        if decisions:
            y = write_line("Decisions:", 50, y)
            y -= 12
            for d in decisions:
                y = write_line(f"• {d}", 60, y)
                y -= 12
        faqs = it.get("faqs") or []
        if faqs:
            y = write_line("FAQs:", 50, y)
            y -= 12
            for f in faqs:
                y = write_line(f"• {f}", 60, y)
                y -= 12
        raw_text = it.get("raw_text")
        if raw_text:
            y = write_line("Original Content:", 50, y)
            y -= 12
            for line in str(raw_text).splitlines():
                if y < 80:
                    c.showPage()
                    y = height - 50
                y = write_line(line[:110], 60, y)
                y -= 12
        y -= 16

    c.save()
    pdf_data = buffer.getvalue()
    buffer.close()
    return {
        "filename": req.filename if req.filename.endswith(".pdf") else f"{req.filename}.pdf",
        "mime": "application/pdf",
        "body_b64": pdf_data.hex(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

