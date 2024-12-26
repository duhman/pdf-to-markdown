import tempfile
import os
from pdf2image import convert_from_bytes
import pytesseract
from langdetect import detect
from typing import List
import io
from fastapi import UploadFile

class PDFProcessor:
    def __init__(self):
        # Configure tesseract to use English and Norwegian
        self.languages = {
            'en': 'eng',
            'no': 'nor'
        }

    async def process_pdf(self, file: UploadFile) -> str:
        # Read the uploaded file
        content = await file.read()
        
        # Create a temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert PDF to images
            images = convert_from_bytes(content)
            
            # Process each page
            text_content = []
            for i, image in enumerate(images):
                # Save image temporarily
                image_path = os.path.join(temp_dir, f'page_{i}.png')
                image.save(image_path, 'PNG')
                
                # Perform OCR with multiple language support
                text = pytesseract.image_to_string(
                    image_path,
                    lang='+'.join(self.languages.values())
                )
                text_content.append(text)
            
            return '\n'.join(text_content)

    def detect_language(self, text: str) -> str:
        try:
            detected = detect(text)
            return 'no' if detected == 'no' else 'en'
        except:
            return 'en'  # Default to English if detection fails
