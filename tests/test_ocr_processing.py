import pytest
import numpy as np
import cv2
from app.ocr_processor import OCRProcessor

@pytest.fixture
def processor():
    return OCRProcessor()

@pytest.fixture
def sample_image():
    # Create a sample image with text
    img = np.zeros((100, 300), dtype=np.uint8)
    cv2.putText(img, "Test 123", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    return img

def test_preprocessing_methods(processor, sample_image):
    """Test all preprocessing methods."""
    methods = [
        'default',
        'threshold',
        'adaptive',
        'denoise',
        'deskew',
        'sharpen',
        'contrast'
    ]
    
    for method in methods:
        processed = processor.preprocessing_methods[method](sample_image)
        assert isinstance(processed, np.ndarray)
        assert processed.shape == sample_image.shape
        assert processed.dtype == np.uint8

def test_denoise_preprocessing(processor, sample_image):
    """Test denoise preprocessing method."""
    processed = processor._denoise_preprocessing(sample_image)
    assert isinstance(processed, np.ndarray)
    assert processed.shape == sample_image.shape
    
    # Check if noise is reduced
    noise_level = np.std(processed)
    original_noise = np.std(sample_image)
    assert noise_level <= original_noise

def test_deskew_preprocessing(processor):
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

def test_sharpen_preprocessing(processor, sample_image):
    """Test sharpen preprocessing method."""
    processed = processor._sharpen_preprocessing(sample_image)
    assert isinstance(processed, np.ndarray)
    assert processed.shape == sample_image.shape
    
    # Check if edges are enhanced
    edges_original = cv2.Canny(sample_image, 100, 200)
    edges_processed = cv2.Canny(processed, 100, 200)
    assert np.sum(edges_processed) >= np.sum(edges_original)

def test_contrast_preprocessing(processor, sample_image):
    """Test contrast preprocessing method."""
    processed = processor._contrast_preprocessing(sample_image)
    assert isinstance(processed, np.ndarray)
    assert processed.shape == sample_image.shape
    
    # Check if contrast is enhanced
    hist_original = cv2.calcHist([sample_image], [0], None, [256], [0, 256])
    hist_processed = cv2.calcHist([processed], [0], None, [256], [0, 256])
    assert np.std(hist_processed) >= np.std(hist_original)

def test_process_with_best_method(processor, sample_image):
    """Test best method selection."""
    text, confidence = processor._process_with_best_method(sample_image)
    assert isinstance(text, str)
    assert isinstance(confidence, float)
    assert 0 <= confidence <= 100

def test_enhance_text(processor):
    """Test text enhancement."""
    test_cases = [
        ("l23456", "123456"),  # Fix 'l' to '1'
        ("O123", "0123"),      # Fix 'O' to '0'
        ("123O", "1230"),      # Fix 'O' to '0'
        ("1,234", "1234"),     # Remove thousands separator
        ("1.234", "1234"),     # Remove thousands separator
        ("1234kr", "1234 kr"), # Fix currency notation
        ("1234NOK", "1234 NOK"), # Fix currency notation
        ("ae oe aa", "æ ø å"), # Fix Norwegian characters
        ("AE OE AA", "Æ Ø Å"), # Fix Norwegian characters
    ]
    
    for input_text, expected in test_cases:
        assert processor.enhance_text(input_text) == expected

def test_detect_layout(processor):
    """Test layout detection."""
    layout_info = [
        {'text': 'Header', 'top': 10, 'height': 20},
        {'text': 'Body', 'top': 100, 'height': 20},
        {'text': 'Footer', 'top': 190, 'height': 20}
    ]
    
    sections = processor.detect_layout(layout_info)
    assert 'header' in sections
    assert 'body' in sections
    assert 'footer' in sections
    
    # Check section assignment
    assert any(item['text'] == 'Header' for item in sections['header'])
    assert any(item['text'] == 'Body' for item in sections['body'])
    assert any(item['text'] == 'Footer' for item in sections['footer'])
