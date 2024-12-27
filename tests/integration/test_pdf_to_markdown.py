"""Integration tests for PDF to Markdown conversion."""

import asyncio
import io
import os
import tempfile
from pathlib import Path
from PIL import Image

from app.pdf_processor import PDFProcessor
from fastapi.testclient import TestClient


def create_test_pdf(text: str, output_path: str):
    """Create a test PDF with the given text."""
    img = Image.new("RGB", (800, 400), color="white")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        img.save(f.name, "PDF", resolution=300.0, save_all=True)
        with open(f.name, "rb") as pdf:
            with open(output_path, "wb") as out:
                out.write(pdf.read())


def test_full_conversion_workflow(client: TestClient, tmp_path):
    """Test the complete PDF to Markdown conversion workflow."""
    # Create a test PDF
    pdf_path = os.path.join(tmp_path, "test.pdf")
    create_test_pdf("Test Invoice\nInvoice #: 12345", pdf_path)

    # Send PDF for conversion
    with open(pdf_path, "rb") as f:
        response = client.post("/convert", files={"file": ("test.pdf", f, "application/pdf")})

    assert response.status_code == 200
    data = response.json()
    assert "markdown" in data
    assert "detected_language" in data
    assert data["detected_language"] in ["en", "no"]


def test_large_pdf_handling(client: TestClient, tmp_path):
    """Test handling of larger PDFs."""
    # Create a larger test PDF
    pdf_path = os.path.join(tmp_path, "large.pdf")
    create_test_pdf("A" * 10000, pdf_path)  # Large content

    with open(pdf_path, "rb") as f:
        response = client.post("/convert", files={"file": ("large.pdf", f, "application/pdf")})

    assert response.status_code == 200


def test_invalid_pdf_handling(client: TestClient):
    """Test handling of invalid PDF files."""
    # Test with non-PDF file
    fake_pdf = io.BytesIO(b"This is not a PDF file")
    response = client.post("/convert", files={"file": ("fake.pdf", fake_pdf, "application/pdf")})
    assert response.status_code == 400


def test_concurrent_requests(client: TestClient, tmp_path):
    """Test handling multiple concurrent requests."""
    pdf_path = os.path.join(tmp_path, "test.pdf")
    create_test_pdf("Test content", pdf_path)

    import httpx

    async def make_request():
        async with httpx.AsyncClient(base_url="http://testserver") as ac:
            with open(pdf_path, "rb") as f:
                files = {"file": ("test.pdf", f.read(), "application/pdf")}
                return await ac.post("/convert", files=files)

    async def test_concurrent():
        """Test concurrent PDF processing."""
        tasks = [make_request() for _ in range(5)]
        responses = await asyncio.gather(*tasks)
        return all(r.status_code == 200 for r in responses)

    success = asyncio.run(test_concurrent())
    assert success


def test_pdf_to_markdown_conversion():
    """Test end-to-end PDF to Markdown conversion."""
    processor = PDFProcessor()
    test_pdf_path = Path(__file__).parent / "test_files" / "sample.pdf"

    with open(test_pdf_path, "rb") as f:
        content = f.read()
        result = processor.process_pdf(content)

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


async def test_concurrent_pdf_processing():
    """Test concurrent PDF processing."""
    processor = PDFProcessor()
    test_pdf_path = Path(__file__).parent / "test_files" / "sample.pdf"

    with open(test_pdf_path, "rb") as f:
        content = f.read()

    tasks = []
    for _ in range(5):
        tasks.append(asyncio.create_task(processor.process_pdf_async(content)))

    results = await asyncio.gather(*tasks)
    return all(r is not None for r in results)
