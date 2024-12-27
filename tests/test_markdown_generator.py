"""Test cases for markdown generation."""

from app.markdown_generator import MarkdownGenerator


def test_markdown_generator_initialization() -> None:
    """Test markdown generator initialization."""
    generator = MarkdownGenerator()
    assert generator.invoice_keywords is not None
    assert "en" in generator.invoice_keywords
    assert "no" in generator.invoice_keywords


def test_generate_markdown_english() -> str:
    """Test markdown generation in English."""
    generator = MarkdownGenerator()
    test_text = """
    Invoice #: INV-001
    Date: 2024-01-26
    Total Amount: $100.00
    VAT: $20.00
    """
    markdown = generator.generate_markdown(test_text, "en")

    assert "# Invoice Details" in markdown
    assert "## Invoice Number" in markdown
    assert "INV-001" in markdown
    assert "## Date" in markdown
    assert "2024-01-26" in markdown
    assert "## Total" in markdown
    assert "$100.00" in markdown
    assert "## Tax" in markdown
    assert "$20.00" in markdown
    return markdown


def test_generate_markdown_norwegian() -> str:
    """Test markdown generation in Norwegian."""
    generator = MarkdownGenerator()
    test_text = """
    Fakturanummer: FAK-001
    Dato: 2024-01-26
    Sum: 1000,00 kr
    MVA: 250,00 kr
    """
    markdown = generator.generate_markdown(test_text, "no")

    assert "# Invoice Details" in markdown
    assert "## Invoice Number" in markdown
    assert "FAK-001" in markdown
    assert "## Date" in markdown
    assert "2024-01-26" in markdown
    assert "## Total" in markdown
    assert "1000,00 kr" in markdown
    assert "## Tax" in markdown
    assert "250,00 kr" in markdown
    return markdown


def test_generate_markdown() -> str:
    """Test markdown generation."""
    generator = MarkdownGenerator()
    text = "Hello\nWorld"
    markdown = generator.generate_markdown(text, "en")
    assert "Hello" in markdown
    assert "World" in markdown
    return markdown
