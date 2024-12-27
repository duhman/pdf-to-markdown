"""Test cases for FastAPI application."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_main() -> None:
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 404  # No root endpoint defined


def test_convert_no_file() -> None:
    """Test convert endpoint with no file."""
    response = client.post("/convert")
    assert response.status_code == 422  # Validation error, no file provided


def test_convert_empty_file() -> None:
    """Test convert endpoint with empty file."""
    files = {"file": ("test.pdf", b"", "application/pdf")}
    response = client.post("/convert", files=files)
    assert response.status_code == 400  # Bad request, empty file
