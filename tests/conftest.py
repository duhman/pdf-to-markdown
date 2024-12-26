import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_pdf_bytes():
    # Create a minimal PDF for testing
    return b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"

@pytest.fixture
def sample_english_text():
    return """
    Invoice #: INV-001
    Date: 2024-01-26
    Total Amount: $100.00
    VAT: $20.00
    """

@pytest.fixture
def sample_norwegian_text():
    return """
    Fakturanummer: FAK-001
    Dato: 2024-01-26
    Sum: 1000,00 kr
    MVA: 250,00 kr
    """