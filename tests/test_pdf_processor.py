"""Test cases for PDF processing."""

from app.pdf_processor import PDFProcessor


def test_pdf_processor_initialization():
    """Test PDF processor initialization."""
    processor = PDFProcessor()
    assert processor.languages is not None
    assert "en" in processor.languages
    assert "no" in processor.languages
    assert processor.languages["en"] == "eng"
    assert processor.languages["no"] == "nor"


def test_detect_language():
    """Test language detection."""
    processor = PDFProcessor()

    # Test Norwegian text
    norwegian_text = "Dette er en norsk tekst med æøå"
    assert processor.detect_language(norwegian_text) == "no"

    # Test English text
    english_text = "This is an English text"
    assert processor.detect_language(english_text) == "en"

    # Test empty text
    assert processor.detect_language("") == "en"


def test_detect_language_english():
    """Test language detection for English text."""
    processor = PDFProcessor()
    text = "This is an English invoice with some important details."
    language = processor.detect_language(text)
    assert language == "en"


def test_detect_language_norwegian():
    """Test language detection for Norwegian text."""
    processor = PDFProcessor()
    text = "Dette er en norsk faktura med viktige detaljer."
    language = processor.detect_language(text)
    assert language == "no"


def test_detect_language_fallback():
    """Test language detection fallback."""
    processor = PDFProcessor()
    text = "123 456 789"  # Numbers only
    language = processor.detect_language(text)
    assert language == "en"  # Should fallback to English
