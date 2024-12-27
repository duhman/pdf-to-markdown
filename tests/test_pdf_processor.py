import pytest
from app.pdf_processor import PDFProcessor
from fastapi import UploadFile
import io


def test_pdf_processor_initialization():
    processor = PDFProcessor()
    assert processor.languages is not None
    assert "en" in processor.languages
    assert "no" in processor.languages
    assert processor.languages["en"] == "eng"
    assert processor.languages["no"] == "nor"


def test_detect_language_english():
    processor = PDFProcessor()
    text = "This is an English invoice with some important details."
    language = processor.detect_language(text)
    assert language == "en"


def test_detect_language_norwegian():
    processor = PDFProcessor()
    text = "Dette er en norsk faktura med viktige detaljer."
    language = processor.detect_language(text)
    assert language == "no"


def test_detect_language_fallback():
    processor = PDFProcessor()
    text = "123 456 789"  # Numbers only
    language = processor.detect_language(text)
    assert language == "en"  # Should fallback to English
