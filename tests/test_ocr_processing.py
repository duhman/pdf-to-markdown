"""Test cases for OCR processing."""

import cv2  # type: ignore
import numpy as np  # type: ignore
import pytest  # type: ignore
from numpy.typing import NDArray  # type: ignore

from app.ocr_processor import OCRProcessor


@pytest.fixture
def processor() -> OCRProcessor:
    """Create an OCR processor instance."""
    return OCRProcessor()


@pytest.fixture
def sample_image() -> NDArray[np.uint8]:
    """Create a sample image for testing."""
    img = np.zeros((300, 400), dtype=np.uint8)
    # Create white text on black background
    text_img = cv2.putText(
        img=img.copy(),
        text="Test Text",
        org=(50, 150),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1.0,
        color=(255,),
        thickness=2,
        lineType=cv2.LINE_AA,
    )
    return text_img


def test_ocr_processor_initialization() -> None:
    """Test OCR processor initialization."""
    processor = OCRProcessor()
    assert processor is not None
    assert processor.language == "eng+nor"


def test_preprocess_image(sample_image: NDArray[np.uint8]) -> None:
    """Test image preprocessing."""
    processor = OCRProcessor()
    processed = processor.preprocess_image(sample_image)

    # Check that preprocessing maintains image dimensions
    assert processed.shape == sample_image.shape
    # Check that preprocessing results in a binary image
    assert np.max(processed) in (0, 255)
    assert np.min(processed) in (0, 255)


def test_deskew_image(sample_image: NDArray[np.uint8]) -> None:
    """Test image deskewing."""
    processor = OCRProcessor()
    # Create a rotated image
    rows, cols = sample_image.shape
    matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), 15, 1)
    rotated = cv2.warpAffine(sample_image, matrix, (cols, rows))

    # Deskew the image
    deskewed = processor.deskew_image(rotated)

    # Check that deskewing maintains image dimensions
    assert deskewed.shape == rotated.shape


def test_detect_text_orientation(sample_image: NDArray[np.uint8]) -> None:
    """Test text orientation detection."""
    processor = OCRProcessor()
    angle = processor.detect_text_orientation(sample_image)
    assert isinstance(angle, float)
    assert -180 <= angle <= 180


def test_remove_noise(sample_image: NDArray[np.uint8]) -> None:
    """Test noise removal."""
    processor = OCRProcessor()
    # Add some noise to the image
    noisy = sample_image.copy()
    noise = np.random.normal(0, 25, sample_image.shape).astype(np.uint8)
    noisy = cv2.add(noisy, noise)

    # Remove noise
    denoised = processor.remove_noise(noisy)

    # Check that noise removal reduces image variance
    assert float(np.std(denoised)) < float(np.std(noisy))


def test_enhance_contrast(sample_image: NDArray[np.uint8]) -> None:
    """Test contrast enhancement."""
    processor = OCRProcessor()
    enhanced = processor.enhance_contrast(sample_image)

    # Check that contrast enhancement maintains image dimensions
    assert enhanced.shape == sample_image.shape
    # Check that enhancement increases image variance
    assert float(np.std(enhanced)) >= float(np.std(sample_image))


def test_detect_text_regions(sample_image: NDArray[np.uint8]) -> None:
    """Test text region detection."""
    processor = OCRProcessor()
    regions = processor.detect_text_regions(sample_image)

    # Check that regions are returned as a list of coordinates
    assert isinstance(regions, list)
    if regions:
        assert len(regions[0]) == 4  # x, y, width, height


def test_process_image(sample_image: NDArray[np.uint8]) -> None:
    """Test complete image processing pipeline."""
    processor = OCRProcessor()
    text = processor.process_image(sample_image)

    # Check that OCR returns a string
    assert isinstance(text, str)
    # Check that some text was detected
    assert len(text.strip()) > 0


def test_preprocessing_methods(processor: OCRProcessor) -> None:
    """Test preprocessing method configuration."""
    result = processor.process_image(sample_image(), "default")
    assert isinstance(result, str)
    assert len(result) > 0


def test_denoise_preprocessing(processor: OCRProcessor, sample_image: NDArray[np.uint8]) -> None:
    """Test denoise preprocessing method."""
    processed = processor._denoise_preprocessing(sample_image)
    assert isinstance(processed, np.ndarray)
    assert processed.shape == sample_image.shape

    # Check if noise is reduced
    noise_level = np.std(processed)
    original_noise = np.std(sample_image)
    assert noise_level <= original_noise


def test_deskew_preprocessing(processor: OCRProcessor) -> None:
    """Test deskew preprocessing method."""
    # Create a skewed image
    img = np.zeros((200, 200), dtype=np.uint8)
    cv2.putText(img, "Skewed", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)

    # Rotate image
    M = cv2.getRotationMatrix2D((100, 100), 15, 1.0)
    skewed = cv2.warpAffine(img, M, (200, 200))

    processed = processor._deskew_preprocessing(skewed)
    assert isinstance(processed, np.ndarray)
    assert processed.shape == skewed.shape


def test_sharpen_preprocessing(processor: OCRProcessor, sample_image: NDArray[np.uint8]) -> None:
    """Test sharpen preprocessing method."""
    processed = processor._sharpen_preprocessing(sample_image)
    assert isinstance(processed, np.ndarray)
    assert processed.shape == sample_image.shape

    # Check if edges are enhanced
    edges_original = cv2.Canny(sample_image, 100, 200)
    edges_processed = cv2.Canny(processed, 100, 200)
    assert np.sum(edges_processed) >= np.sum(edges_original)


def test_contrast_preprocessing(processor: OCRProcessor, sample_image: NDArray[np.uint8]) -> None:
    """Test contrast preprocessing method."""
    processed = processor._contrast_preprocessing(sample_image)
    assert isinstance(processed, np.ndarray)
    assert processed.shape == sample_image.shape

    # Check if contrast is enhanced
    hist_original = cv2.calcHist([sample_image], [0], None, [256], [0, 256])
    hist_processed = cv2.calcHist([processed], [0], None, [256], [0, 256])
    assert np.std(hist_processed) >= np.std(hist_original)


def test_process_with_best_method(processor: OCRProcessor, sample_image: NDArray[np.uint8]) -> None:
    """Test best method selection."""
    text, confidence = processor._process_with_best_method(sample_image)
    assert isinstance(text, str)
    assert isinstance(confidence, float)
    assert 0 <= confidence <= 100


def test_enhance_text(processor: OCRProcessor) -> None:
    """Test text enhancement."""
    test_cases = [
        ("l23456", "123456"),  # Fix 'l' to '1'
        ("O123", "0123"),  # Fix 'O' to '0'
        ("123O", "1230"),  # Fix 'O' to '0'
        ("1,234", "1234"),  # Remove thousands separator
        ("1.234", "1234"),  # Remove thousands separator
        ("1234kr", "1234 kr"),  # Fix currency notation
        ("1234NOK", "1234 NOK"),  # Fix currency notation
        ("ae oe aa", "æ ø å"),  # Fix Norwegian characters
        ("AE OE AA", "Æ Ø Å"),  # Fix Norwegian characters
    ]

    for input_text, expected in test_cases:
        assert processor.enhance_text(input_text) == expected


def test_detect_layout(processor: OCRProcessor) -> None:
    """Test layout detection."""
    layout_info = [
        {"y": 10, "height": 50, "text": "Header", "width": 100},
        {"y": 100, "height": 200, "text": "Body", "width": 100},
        {"y": 350, "height": 50, "text": "Footer", "width": 100},
    ]
    sections = processor.detect_layout(layout_info)
    assert "header" in sections
    assert "body" in sections
    assert "footer" in sections

    # Check section assignment
    assert any(item["text"] == "Header" for item in sections["header"])
    assert any(item["text"] == "Body" for item in sections["body"])
    assert any(item["text"] == "Footer" for item in sections["footer"])


def test_language_support(processor: OCRProcessor) -> None:
    """Test language support configuration."""
    assert "eng" in processor.languages.values()
    assert "nor" in processor.languages.values()


def test_image_processing(processor: OCRProcessor, sample_image: NDArray[np.uint8]) -> None:
    """Test image processing with default method."""
    result = processor.process_image(sample_image)
    assert isinstance(result, str)
    assert len(result) > 0


def test_layout_detection(processor: OCRProcessor) -> None:
    """Test layout detection."""
    layout_info = [
        {"y": 10, "height": 50, "text": "Header", "width": 100},
        {"y": 100, "height": 200, "text": "Body", "width": 100},
        {"y": 350, "height": 50, "text": "Footer", "width": 100},
    ]
    # Cast the layout info to the correct type
    typed_layout_info = [
        {k: int(v) if k in ("y", "height", "width") else str(v) for k, v in item.items()}
        for item in layout_info
    ]
    sections = processor.detect_layout(typed_layout_info)
    assert "header" in sections
    assert "body" in sections
    assert "footer" in sections


def test_contrast_enhancement(processor: OCRProcessor, sample_image: NDArray[np.uint8]) -> None:
    """Test contrast enhancement."""
    enhanced = processor.enhance_contrast(sample_image)
    assert enhanced.shape == sample_image.shape
    assert isinstance(enhanced, np.ndarray)


def test_noise_removal(processor: OCRProcessor, sample_image: NDArray[np.uint8]) -> None:
    """Test noise removal."""
    denoised = processor.remove_noise(sample_image)
    assert denoised.shape[:2] == sample_image.shape[:2]
    assert isinstance(denoised, np.ndarray)


def test_text_orientation(processor: OCRProcessor, sample_image: NDArray[np.uint8]) -> None:
    """Test text orientation detection."""
    angle = processor.detect_text_orientation(sample_image)
    assert isinstance(angle, float)
    assert -90 <= angle <= 90


def test_image_deskewing(processor: OCRProcessor, sample_image: NDArray[np.uint8]) -> None:
    """Test image deskewing."""
    deskewed = processor.deskew_image(sample_image)
    assert deskewed.shape == sample_image.shape
    assert isinstance(deskewed, np.ndarray)


def test_layout_analysis(processor: OCRProcessor) -> None:
    """Test layout analysis with sample data."""
    layout_info = [
        {"x": 10, "y": 10, "width": 100, "height": 50, "text": "Header"},
        {"x": 10, "y": 100, "width": 100, "height": 200, "text": "Body"},
        {"x": 10, "y": 350, "width": 100, "height": 50, "text": "Footer"},
    ]

    sections = processor.detect_layout(layout_info)
    assert "header" in sections
    assert "body" in sections
    assert "footer" in sections
    assert any(item["text"] == "Header" for item in sections["header"])
    assert any(item["text"] == "Body" for item in sections["body"])
    assert any(item["text"] == "Footer" for item in sections["footer"])
