"""Integration tests for PDF to Markdown conversion."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.pdf_processor import PDFProcessor


@pytest.fixture
def test_app() -> FastAPI:
    """Create test FastAPI application.

    Returns:
        FastAPI test application
    """
    return app


@pytest.fixture
def client(test_app: FastAPI) -> Generator[TestClient, None, None]:
    """Create test client.

    Args:
        test_app: FastAPI test application

    Returns:
        Test client
    """
    with TestClient(test_app) as client:
        yield client


@pytest.fixture
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client.

    Args:
        test_app: FastAPI test application

    Returns:
        Async test client
    """
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_invalid_file_type(client: TestClient) -> None:
    """Test uploading invalid file type."""
    files = {"file": ("test.txt", b"test content", "text/plain")}
    response = client.post("/convert", files=files)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_concurrent_pdf_processing(async_client: AsyncClient, tmp_path: Path) -> None:
    """Test concurrent PDF processing."""
    # Create test PDF files
    test_files = []
    for i in range(3):
        pdf_path = tmp_path / f"test_{i}.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n")  # Minimal valid PDF
        test_files.append(pdf_path)

    # Process PDFs concurrently
    tasks = []
    for pdf_path in test_files:
        with open(pdf_path, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            tasks.append(async_client.post("/convert", files=files))

    responses = await asyncio.gather(*tasks)
    assert all(response.status_code == 200 for response in responses)


@pytest.mark.asyncio
async def test_large_pdf_processing(async_client: AsyncClient, tmp_path: Path) -> None:
    """Test processing large PDF file."""
    # Create large test PDF
    large_pdf = tmp_path / "large.pdf"
    with open(large_pdf, "wb") as f:
        f.write(b"%PDF-1.4\n" * 1000)  # 5KB PDF

    with open(large_pdf, "rb") as f:
        files = {"file": ("large.pdf", f, "application/pdf")}
        response = await async_client.post("/convert", files=files)

    assert response.status_code == 200
    assert "markdown" in response.json()


def test_pdf_processor_error_handling(tmp_path: Path) -> None:
    """Test PDF processor error handling."""
    processor = PDFProcessor()
    invalid_pdf = tmp_path / "invalid.pdf"
    invalid_pdf.write_bytes(b"Not a PDF file")

    with pytest.raises(Exception):
        processor.process_pdf(str(invalid_pdf))
