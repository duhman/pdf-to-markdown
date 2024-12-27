"""OCR processor for extracting text from PDFs."""

import re
from typing import Any, Dict, List, Tuple, Union, cast

import cv2  # type: ignore
import numpy as np  # type: ignore
import numpy.typing as npt
import pytesseract  # type: ignore
from pdf2image import convert_from_bytes  # type: ignore


class OCRProcessor:
    """OCR processor for extracting text from PDFs."""

    def __init__(self) -> None:
        """Initialize OCR processor."""
        self.languages = {"en": "eng", "no": "nor"}
        self.language = "eng+nor"
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

    def _default_preprocessing(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        """Basic preprocessing."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def _threshold_preprocessing(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        """Threshold-based preprocessing."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def _adaptive_preprocessing(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        """Adaptive threshold preprocessing."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

    def _denoise_preprocessing(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        """Denoise the image."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return cv2.fastNlMeansDenoising(gray)

    def _deskew_preprocessing(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
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

    def _sharpen_preprocessing(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        """Sharpen the image."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        return cv2.filter2D(gray, -1, kernel)

    def _contrast_preprocessing(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        """Enhance contrast."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        return cv2.equalizeHist(gray)

    def _process_with_best_method(self, image: npt.NDArray[np.uint8]) -> Tuple[str, float]:
        """Try all preprocessing methods and return the best result."""
        best_text = ""
        best_confidence = 0

        for method_name, method in self.preprocessing_methods.items():
            processed = method(image)
            text = pytesseract.image_to_string(processed, lang=self.language, config="--psm 6")

            # Get confidence scores
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            confidence = sum(int(x) for x in data["conf"] if x != "-1") / len(data["conf"])

            if confidence > best_confidence:
                best_confidence = confidence
                best_text = text

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

    def detect_layout(
        self, layout_info: List[Dict[str, Union[int, str]]]
    ) -> Dict[str, List[Dict[str, Union[int, str]]]]:
        """Detect document layout sections."""
        sections: Dict[str, List[Dict[str, Union[int, str]]]] = {
            "header": [],
            "body": [],
            "footer": [],
        }

        if not layout_info:
            return sections

        # Sort by vertical position
        sorted_elements = sorted(layout_info, key=lambda x: cast(int, x["top"]))

        # Get page height
        max_y = max(
            cast(int, elem["top"]) + cast(int, elem.get("height", 0)) for elem in layout_info
        )

        # Define section boundaries
        header_height = float(max_y) * 0.2  # Top 20%
        footer_start = float(max_y) * 0.8  # Bottom 20%

        # Categorize elements
        for elem in sorted_elements:
            y = cast(int, elem["top"])
            if float(y) < header_height:
                sections["header"].append(elem)
            elif float(y) > footer_start:
                sections["footer"].append(elem)
            else:
                sections["body"].append(elem)

        return sections

    def detect_text_orientation(self, image: npt.NDArray[np.uint8]) -> float:
        """Detect the orientation of text in the image."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Apply Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)

        if lines is not None:
            angles: list[float] = []
            for rho, theta in lines[:, 0]:
                angle = float(theta * 180 / np.pi)  # Convert to float
                # Normalize angle to -90 to 90 degrees
                if angle > 90:
                    angle = angle - 180
                angles.append(angle)

            # Return median angle
            if angles:
                median_angle = float(np.median(angles))
                return median_angle

        return 0.0

    def process_image(self, image: npt.NDArray[np.uint8], method: str = "default") -> str:
        """Process an image and extract text using the specified preprocessing method."""
        if method not in self.preprocessing_methods:
            raise ValueError(f"Unknown preprocessing method: {method}")

        processed = self.preprocessing_methods[method](image)
        text = pytesseract.image_to_string(processed, lang=self.language)
        return str(text)

    def detect_text_regions(self, image: npt.NDArray[np.uint8]) -> List[Tuple[int, int, int, int]]:
        """Detect regions containing text in the image."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply thresholding
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Get bounding rectangles for text regions
        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter out very small regions
            if w > 20 and h > 20:
                regions.append((x, y, w, h))

        return regions

    def enhance_contrast(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        """Enhance image contrast using histogram equalization."""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)

        # Merge channels
        limg = cv2.merge((cl, a, b))

        # Convert back to BGR
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    def remove_noise(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        """Remove noise from the image."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply median blur
        denoised = cv2.medianBlur(gray, 3)

        # Apply bilateral filter
        return cv2.bilateralFilter(denoised, 9, 75, 75)

    def deskew_image(self, image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        """Deskew the image based on detected text orientation."""
        angle = self.detect_text_orientation(image)

        # Get image dimensions
        height, width = image.shape[:2]
        center = (width // 2, height // 2)

        # Create rotation matrix
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Perform rotation
        return cv2.warpAffine(
            image, matrix, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
