"""PDF processing module."""

import logging
from typing import Union

import langdetect  # type: ignore
import pytesseract  # type: ignore
from fastapi import HTTPException, UploadFile  # type: ignore
from pdf2image import convert_from_bytes  # type: ignore

# Initialize logger
logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self) -> None:
        # Configure tesseract to use English and Norwegian
        self.languages = {"en": "eng", "no": "nor"}
        self.ocr = pytesseract

    async def process_pdf(self, file: Union[UploadFile, bytes]) -> str:
        """Process PDF file and extract text."""
        try:
            if isinstance(file, UploadFile):
                content = await file.read()
            else:
                content = file

            if not content:
                raise HTTPException(status_code=400, detail="Empty PDF file")

            # Convert PDF to images
            images = convert_from_bytes(content)
            if not images:
                raise HTTPException(status_code=400, detail="Invalid PDF file")

            # Process each page
            text_content = []
            for image in images:
                # Process with OCR
                page_text = self.ocr.image_to_string(image, lang="+".join(self.languages.values()))
                text_content.append(page_text)

            return "\n".join(text_content)

        except pytesseract.TesseractError as e:
            logger.error(f"Tesseract error: {str(e)}")
            raise HTTPException(status_code=400, detail="Tesseract error")
        except Exception as e:
            logger.error(f"Error converting PDF: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid PDF file")

    def detect_language(self, text: str) -> str:
        try:
            detected = langdetect.detect(text)
            return "no" if detected == "no" else "en"
        except langdetect.lang_detect_exception.LangDetectException:
            return "en"  # Default to English if detection fails
