import tempfile
import os
from pdf2image import convert_from_bytes
import pytesseract
from langdetect import detect
from typing import List, Union
import io
from fastapi import UploadFile
import logging
import numpy as np
import cv2
from fastapi import HTTPException

# Initialize logger
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        # Configure tesseract to use English and Norwegian
        self.languages = {
            'en': 'eng',
            'no': 'nor'
        }
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
                # Convert PIL image to numpy array for OpenCV
                image_np = np.array(image)
                
                # Process with OCR
                page_text = self.ocr.image_to_string(
                    image_np,
                    lang='+'.join(self.languages.values())
                )
                text_content.append(page_text)

            return "\n".join(text_content)

        except Exception as e:
            logger.error(f"Error converting PDF: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid PDF file")

    def detect_language(self, text: str) -> str:
        try:
            detected = detect(text)
            return 'no' if detected == 'no' else 'en'
        except:
            return 'en'  # Default to English if detection fails
