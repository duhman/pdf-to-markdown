"""Performance tests for the application."""

import asyncio
import time
from typing import Any, Callable, List, Tuple

import pytest

from app.markdown_generator import MarkdownGenerator
from app.pdf_processor import PDFProcessor


@pytest.fixture
def sample_english_text() -> str:
    """Sample English text for testing."""
    return """
    Invoice #: 12345
    Date: 2024-01-01
    Amount: 1000.00
    Customer: John Doe
    """


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Sample PDF content for testing."""
    return b"%PDF-1.4\nTest PDF content"


def test_markdown_generator_performance(sample_english_text: str, benchmark: Callable) -> None:
    """Test the performance of markdown generation."""
    generator = MarkdownGenerator()

    def generate() -> str:
        return generator.generate_markdown(sample_english_text, "en")

    result = benchmark(generate)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_pdf_processor_performance(sample_pdf_bytes: bytes) -> None:
    """Test the performance of PDF processing."""
    processor = PDFProcessor()

    start_time = time.time()
    result = await processor.process_pdf(sample_pdf_bytes)
    end_time = time.time()

    assert (end_time - start_time) < 5.0  # Should process within 5 seconds
    assert result is not None


def test_language_detection_performance(benchmark: Callable) -> None:
    """Test the performance of language detection."""
    processor = PDFProcessor()
    texts = [
        "This is an English text with some numbers 123456.",
        "Dette er en norsk tekst med noen tall 123456.",
        "En annen norsk tekst med noen tall 123456.",
    ]

    def detect_languages() -> List[str]:
        return [processor.detect_language(text) for text in texts]

    results = benchmark(detect_languages)
    assert all(lang in ["en", "no"] for lang in results)


@pytest.mark.asyncio
async def test_concurrent_processing_performance() -> None:
    """Test performance under concurrent load."""
    processor = PDFProcessor()
    generator = MarkdownGenerator()
    texts = ["Sample text"] * 10

    async def process_and_generate(text: str) -> str:
        language = processor.detect_language(text)
        return generator.generate_markdown(text, language)

    start_time = time.time()
    tasks = [process_and_generate(text) for text in texts]
    results = await asyncio.gather(*tasks)
    end_time = time.time()

    assert (end_time - start_time) < 10.0  # Should complete within 10 seconds
    assert all(isinstance(result, str) for result in results)
