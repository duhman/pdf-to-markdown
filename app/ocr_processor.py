from typing import Dict, List, Optional, Tuple
import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_bytes
import re

class OCRProcessor:
    def __init__(self):
        self.languages = {
            'en': 'eng',
            'no': 'nor'
        }
        self.preprocessing_methods = {
            'default': self._default_preprocessing,
            'threshold': self._threshold_preprocessing,
            'adaptive': self._adaptive_preprocessing
        }

    def process_pdf(self, pdf_bytes: bytes) -> Tuple[str, List[Dict[str, int]]]:
        """Process PDF and return extracted text and layout information."""
        # Convert PDF to images
        images = convert_from_bytes(pdf_bytes)
        
        full_text = ""
        layout_info = []
        
        for image in images:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Try different preprocessing methods
            best_text = ""
            best_confidence = 0
            
            for method_name, method in self.preprocessing_methods.items():
                processed = method(cv_image)
                text = pytesseract.image_to_string(
                    processed,
                    lang='+'.join(self.languages.values()),
                    config='--psm 6'
                )
                
                # Get confidence scores
                data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
                confidence = sum(int(x) for x in data['conf'] if x != '-1') / len(data['conf'])
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_text = text
                    
                    # Store layout information
                    layout_info.extend([{
                        'text': word,
                        'left': left,
                        'top': top,
                        'width': width,
                        'height': height,
                        'conf': conf
                    } for word, left, top, width, height, conf in zip(
                        data['text'],
                        data['left'],
                        data['top'],
                        data['width'],
                        data['height'],
                        data['conf']
                    ) if word.strip()])
            
            full_text += best_text + "\n"
        
        return full_text, layout_info

    def _default_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Basic preprocessing."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.medianBlur(gray, 3)

    def _threshold_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Threshold-based preprocessing."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        return cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def _adaptive_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Adaptive threshold preprocessing."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        return cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

    def enhance_text(self, text: str) -> str:
        """Post-process extracted text."""
        # Fix common OCR errors
        corrections = {
            r'l(?=\d)': '1',  # Letter 'l' before numbers is probably '1'
            r'O(?=\d)': '0',  # Letter 'O' before numbers is probably '0'
            r'(?<=\d)O': '0', # Letter 'O' after numbers is probably '0'
            r'(?<=\d),(?=\d{3})': '',  # Remove thousands separator commas
            r'(?<=\d)\.(?=\d{3})': '',  # Remove thousands separator dots
        }
        
        enhanced = text
        for pattern, replacement in corrections.items():
            enhanced = re.sub(pattern, replacement, enhanced)
        
        return enhanced

    def detect_layout(self, layout_info: List[Dict[str, int]]) -> Dict[str, List[Dict[str, int]]]:
        """Detect document layout sections."""
        sections = {
            'header': [],
            'body': [],
            'footer': []
        }
        
        if not layout_info:
            return sections
            
        # Sort by vertical position
        sorted_elements = sorted(layout_info, key=lambda x: x['top'])
        
        # Find page boundaries
        page_height = max(elem['top'] + elem['height'] for elem in layout_info)
        header_boundary = page_height * 0.2
        footer_boundary = page_height * 0.8
        
        # Categorize elements
        for elem in sorted_elements:
            if elem['top'] < header_boundary:
                sections['header'].append(elem)
            elif elem['top'] > footer_boundary:
                sections['footer'].append(elem)
            else:
                sections['body'].append(elem)
        
        return sections
