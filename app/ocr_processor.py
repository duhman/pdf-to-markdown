from typing import Dict, List, Optional, Tuple
import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_bytes
import re


class OCRProcessor:
    def __init__(self):
        self.languages = {"en": "eng", "no": "nor"}
        self.preprocessing_methods = {
            "default": self._default_preprocessing,
            "threshold": self._threshold_preprocessing,
            "adaptive": self._adaptive_preprocessing,
            "denoise": self._denoise_preprocessing,
            "deskew": self._deskew_preprocessing,
            "sharpen": self._sharpen_preprocessing,
            "contrast": self._contrast_preprocessing,
        }

    def process_pdf(self, pdf_bytes: bytes) -> Tuple[str, List[Dict[str, int]]]:
        """Process PDF and return extracted text and layout information."""
        # Convert PDF to images
        images = convert_from_bytes(pdf_bytes)

        full_text = ""
        layout_info = []

        for image in images:
            # Convert PIL image to OpenCV format
            img_array = np.array(image)
            if len(img_array.shape) == 2:  # If grayscale
                cv_image = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
            else:  # If RGB/RGBA
                cv_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

            # Process with best method
            text, confidence = self._process_with_best_method(cv_image)
            full_text += text + "\n"

            # Get layout information using the best method
            processed = self.preprocessing_methods["default"](cv_image)
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)

            layout_info.extend(
                [
                    {
                        "text": word,
                        "left": left,
                        "top": top,
                        "width": width,
                        "height": height,
                        "conf": conf,
                    }
                    for word, left, top, width, height, conf in zip(
                        data["text"],
                        data["left"],
                        data["top"],
                        data["width"],
                        data["height"],
                        data["conf"],
                    )
                    if word.strip()
                ]
            )

        return full_text, layout_info

    def _default_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Basic preprocessing."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def _threshold_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Threshold-based preprocessing."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def _adaptive_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Adaptive threshold preprocessing."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

    def _denoise_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Denoise the image."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return cv2.fastNlMeansDenoising(gray)

    def _deskew_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Deskew the image."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        coords = np.column_stack(np.where(gray > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(
            gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )

    def _sharpen_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Sharpen the image."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        return cv2.filter2D(gray, -1, kernel)

    def _contrast_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Enhance contrast."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return cv2.equalizeHist(gray)

    def _process_with_best_method(self, image: np.ndarray) -> Tuple[str, float]:
        """Try all preprocessing methods and return the best result."""
        best_text = ""
        best_confidence = 0
        best_method = None

        for method_name, method in self.preprocessing_methods.items():
            processed = method(image)
            text = pytesseract.image_to_string(
                processed, lang="+".join(self.languages.values()), config="--psm 6"
            )

            # Get confidence scores
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            confidence = sum(int(x) for x in data["conf"] if x != "-1") / len(data["conf"])

            if confidence > best_confidence:
                best_confidence = confidence
                best_text = text
                best_method = method_name

        return best_text, best_confidence

    def enhance_text(self, text: str) -> str:
        """Post-process extracted text."""
        # Fix common OCR errors
        corrections = {
            r"l(?=\d)": "1",  # Letter 'l' before numbers is probably '1'
            r"O(?=\d)": "0",  # Letter 'O' before numbers is probably '0'
            r"(?<=\d)O": "0",  # Letter 'O' after numbers is probably '0'
            r"(?<=\d),(?=\d{3})": "",  # Remove thousands separator commas
            r"(?<=\d)\.(?=\d{3})": "",  # Remove thousands separator dots
            r"(?<=\d)kr\.?": " kr",  # Standardize currency notation
            r"(?<=\d)NOK": " NOK",  # Standardize currency notation
            r"[®©™]": "",  # Remove special characters that might be misread
            r"\s+": " ",  # Normalize whitespace
        }

        enhanced = text
        for pattern, replacement in corrections.items():
            enhanced = re.sub(pattern, replacement, enhanced)

        # Fix Norwegian specific characters
        norwegian_fixes = {"ae": "æ", "oe": "ø", "aa": "å", "AE": "Æ", "OE": "Ø", "AA": "Å"}

        for wrong, correct in norwegian_fixes.items():
            enhanced = enhanced.replace(wrong, correct)

        return enhanced.strip()

    def detect_layout(self, layout_info: List[Dict[str, int]]) -> Dict[str, List[Dict[str, int]]]:
        """Detect document layout sections."""
        sections = {"header": [], "body": [], "footer": []}

        if not layout_info:
            return sections

        # Sort by vertical position
        sorted_elements = sorted(layout_info, key=lambda x: x["top"])

        # Find page boundaries
        page_height = max(elem["top"] + elem["height"] for elem in layout_info)
        header_boundary = page_height * 0.2
        footer_boundary = page_height * 0.8

        # Categorize elements
        for elem in sorted_elements:
            if elem["top"] < header_boundary:
                sections["header"].append(elem)
            elif elem["top"] > footer_boundary:
                sections["footer"].append(elem)
            else:
                sections["body"].append(elem)

        return sections
