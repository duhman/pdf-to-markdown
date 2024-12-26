import pytest
import time
from app.markdown_generator import MarkdownGenerator
from app.pdf_processor import PDFProcessor
import asyncio

def test_markdown_generator_performance(sample_english_text, benchmark):
    """Test the performance of markdown generation."""
    generator = MarkdownGenerator()
    
    def generate():
        return generator.generate_markdown(sample_english_text, 'en')
    
    result = benchmark(generate)
    assert result is not None
    assert isinstance(result, str)

@pytest.mark.asyncio
async def test_pdf_processor_performance(sample_pdf_bytes):
    """Test the performance of PDF processing."""
    processor = PDFProcessor()
    
    start_time = time.time()
    result = await processor.process_pdf(sample_pdf_bytes)
    end_time = time.time()
    
    processing_time = end_time - start_time
    assert processing_time < 5.0  # Should process within 5 seconds
    assert result is not None

def test_language_detection_performance(benchmark):
    """Test the performance of language detection."""
    processor = PDFProcessor()
    texts = [
        "This is an English text for testing performance.",
        "Dette er en norsk tekst for å teste ytelse.",
        "Another English text with some numbers 123456.",
        "En annen norsk tekst med noen tall 123456."
    ]
    
    def detect_languages():
        return [processor.detect_language(text) for text in texts]
    
    results = benchmark(detect_languages)
    assert len(results) == len(texts)
    assert all(lang in ['en', 'no'] for lang in results)

@pytest.mark.asyncio
async def test_concurrent_processing_performance():
    """Test performance under concurrent load."""
    processor = PDFProcessor()
    generator = MarkdownGenerator()
    
    async def process_and_generate(text):
        language = processor.detect_language(text)
        return generator.generate_markdown(text, language)
    
    texts = [
        "Invoice #1",
        "Faktura #2",
        "Receipt #3",
        "Kvittering #4"
    ] * 5  # 20 concurrent operations
    
    start_time = time.time()
    tasks = [process_and_generate(text) for text in texts]
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    total_time = end_time - start_time
    assert total_time < 2.0  # Should handle 20 concurrent operations within 2 seconds
    assert len(results) == len(texts)
    assert all(isinstance(r, str) for r in results)
