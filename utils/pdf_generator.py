import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def create_resume_pdf(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    x = 20 * mm
    y = height - 20 * mm
    name = data.get("full_name") or "My Resume"
    title = data.get("professional_title") or "Professional"
    c.setFont("Helvetica-Bold", 22)
    c.drawString(x, y, name[:60])
    y -= 9 * mm
    c.setFont("Helvetica", 10)
    contact = " | ".join(v for v in [data.get("email"), data.get("phone"), data.get("location")] if v)
    if contact:
        c.drawString(x, y, contact[:110])
        y -= 8 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, title[:80])
    y -= 10 * mm

    def section(title_text):
        nonlocal y
        if y < 35 * mm:
            c.showPage(); y = height - 20 * mm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, title_text)
        y -= 6 * mm

    def lines(text, size=9, leading=4.5):
        nonlocal y
        c.setFont("Helvetica", size)
        for raw in str(text or "").splitlines():
            if y < 20 * mm:
                c.showPage(); y = height - 20 * mm
            c.drawString(x, y, raw[:115])
            y -= leading * mm
        y -= 2 * mm

    if data.get("summary"):
        section("SUMMARY"); lines(data["summary"])
    skills = data.get("skills", [])
    if skills:
        section("SKILLS"); lines(", ".join(str(s) for s in skills))
    for key, heading in [("education", "EDUCATION"), ("experience", "EXPERIENCE"), ("projects", "PROJECTS")]:
        items = data.get(key, [])
        if items:
            section(heading)
            for item in items:
                if isinstance(item, dict):
                    primary = item.get("degree") or item.get("name") or item.get("title") or item.get("role") or ""
                    secondary = item.get("college") or item.get("company") or item.get("technologies") or ""
                    details = item.get("description") or ""
                    lines(f"{primary} | {secondary}")
                    lines(details)
                else:
                    lines(item)
    for key, heading in [("certifications", "CERTIFICATIONS"), ("achievements", "ACHIEVEMENTS"), ("languages", "LANGUAGES"), ("soft_skills", "SOFT SKILLS")]:
        value = data.get(key, [])
        if value:
            section(heading); lines(", ".join(value) if isinstance(value, list) else value)
    c.save()
    return output_path
