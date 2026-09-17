import base64
import io
import os
import zipfile
import pdfplumber
from docx import Document
from PIL import Image


def extract_pdf_text(path):
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    text = "\n".join(pages).strip()
    return text or _extract_scanned_pdf_text(path)


def _extract_scanned_pdf_text(path):
    try:
        import fitz
        import pytesseract
    except ImportError as exc:
        raise RuntimeError("This scanned PDF needs OCR. Install PyMuPDF and pytesseract, then install Tesseract OCR on Windows.") from exc

    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for executable in tesseract_paths:
        if os.path.exists(executable):
            pytesseract.pytesseract.tesseract_cmd = executable
            break
    try:
        pytesseract.get_tesseract_version()
    except Exception as exc:
        raise RuntimeError("This scanned PDF needs Tesseract OCR. Install Tesseract OCR on Windows and upload the PDF again.") from exc

    pages = []
    document = fitz.open(path)
    try:
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            pages.append(pytesseract.image_to_string(image, config="--psm 6"))
    finally:
        document.close()
    return "\n".join(pages).strip()


def extract_docx_text(path):
    document = Document(path)
    return "\n".join(p.text for p in document.paragraphs if p.text.strip()).strip()


def extract_resume_text(path, extension=None):
    ext = (extension or os.path.splitext(path)[1].lstrip(".")).lower()
    if ext == "pdf":
        return extract_pdf_text(path)
    if ext == "docx":
        return extract_docx_text(path)
    raise ValueError("Unsupported resume format")


def _image_data_url(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()
    except Exception:
        return ""
    output = io.BytesIO()
    image.convert("RGB").save(output, format="JPEG", quality=90)
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _select_portrait(candidates):
    if not candidates:
        return ""
    candidates.sort(reverse=True, key=lambda item: (item[0], item[1]))
    return _image_data_url(candidates[0][2])


def _docx_photo(path):
    candidates = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.startswith("word/media/"):
                continue
            raw = archive.read(name)
            try:
                with Image.open(io.BytesIO(raw)) as image:
                    width, height = image.size
                ratio = width / height if height else 0
                score = width * height if 0.45 <= ratio <= 1.0 else 0
                candidates.append((score, width * height, raw))
            except Exception:
                continue
    return _select_portrait(candidates)


def _pdf_photo(path):
    try:
        import fitz
    except ImportError:
        return ""
    candidates = []
    document = fitz.open(path)
    try:
        for page in document:
            for image_info in page.get_images(full=True):
                try:
                    image = document.extract_image(image_info[0])
                    raw = image["image"]
                    with Image.open(io.BytesIO(raw)) as decoded:
                        width, height = decoded.size
                    rects = page.get_image_rects(image_info[0])
                    rect = rects[0] if rects else None
                    page_area = page.rect.width * page.rect.height
                    displayed_area = rect.width * rect.height if rect else page_area
                    coverage = displayed_area / page_area if page_area else 1
                    ratio = width / height if height else 0
                    portrait_shape = 0.45 <= ratio <= 1.4
                    score = width * height if portrait_shape and coverage < 0.55 else 0
                    candidates.append((score, width * height, raw))
                except Exception:
                    continue
    finally:
        document.close()
    return _select_portrait(candidates)


def extract_resume_photo(path, extension=None):
    ext = (extension or os.path.splitext(path)[1].lstrip(".")).lower()
    if ext == "pdf":
        return _pdf_photo(path)
    if ext == "docx":
        return _docx_photo(path)
    return ""
