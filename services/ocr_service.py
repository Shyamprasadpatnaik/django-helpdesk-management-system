import os
import logging
from PIL import Image

logger = logging.getLogger(__name__)

def extract_text_from_file(file_path):
    """
    Modular and optional OCR text extractor for scanned documents/images.
    Gracefully degrades if pytesseract is not installed on the host.
    """
    if not file_path or not os.path.exists(file_path):
        return ""

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
        return ""

    try:
        import pytesseract
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except ImportError:
        logger.debug("pytesseract is not installed; skipping OCR extraction.")
        return ""
    except Exception as e:
        logger.warning(f"OCR processing failed on {file_path}: {e}")
        return ""
