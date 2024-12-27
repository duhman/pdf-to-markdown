"""Property-based tests for pdf-to-markdown."""

from hypothesis import given
from hypothesis import strategies as st

from app.markdown_generator import MarkdownGenerator
from app.pdf_processor import PDFProcessor

# Custom strategies
invoice_numbers = st.from_regex(r"[A-Z0-9]{3,10}-?\d{3,5}")
amounts = st.decimals(min_value=0, max_value=1000000, places=2)
dates = st.dates().map(lambda d: d.strftime("%Y-%m-%d"))


@given(
    invoice_number=invoice_numbers,
    amount=amounts,
    date=dates,
    language=st.sampled_from(["en", "no"]),
)
def test_markdown_generator_properties(invoice_number, amount, date, language):
    """Test MarkdownGenerator with property-based testing."""
    generator = MarkdownGenerator()

    # Create test text based on language
    if language == "en":
        text = f"""
        Invoice #: {invoice_number}
        Date: {date}
        Amount: ${amount}
        """
    else:
        text = f"""
        Fakturanummer: {invoice_number}
        Dato: {date}
        Sum: {amount} kr
        """

    result = generator.generate_markdown(text, language)

    # Properties that should always hold
    assert isinstance(result, str)
    assert "# Invoice Details" in result
    assert str(invoice_number) in result
    assert str(date) in result
    assert str(float(amount)).rstrip("0").rstrip(".") in result


@given(st.text(min_size=1))
def test_language_detection_properties(text):
    """Test language detection with property-based testing."""
    processor = PDFProcessor()
    language = processor.detect_language(text)

    # Properties that should always hold
    assert language in ["en", "no"]
    assert isinstance(language, str)


@given(st.lists(st.text(min_size=1), min_size=1, max_size=10))
def test_batch_processing_properties(texts):
    """Test batch processing with property-based testing."""
    processor = PDFProcessor()
    generator = MarkdownGenerator()

    for text in texts:
        # Should never raise an exception
        language = processor.detect_language(text)
        result = generator.generate_markdown(text, language)

        # Properties that should always hold
        assert isinstance(language, str)
        assert isinstance(result, str)
        assert "# Invoice Details" in result


@given(
    invoice_number=invoice_numbers,
    amount=amounts,
    vat_rate=st.decimals(min_value=0, max_value=0.25, places=2),
)
def test_vat_calculation_properties(invoice_number, amount, vat_rate):
    """Test VAT calculations with property-based testing."""
    generator = MarkdownGenerator()

    vat_amount = float(amount) * float(vat_rate)
    text = f"""
    Invoice #: {invoice_number}
    Amount: ${amount}
    VAT: ${vat_amount}
    """

    result = generator.generate_markdown(text, "en")

    # Properties that should always hold
    assert isinstance(result, str)
    assert str(float(amount)).rstrip("0").rstrip(".") in result
    assert str(float(vat_amount)).rstrip("0").rstrip(".") in result


@given(st.text())
def test_markdown_generation_property(text):
    """Test that markdown generation works for any input text."""
    generator = MarkdownGenerator()
    result = generator.generate_markdown(text, "en")
    assert isinstance(result, str)
    assert len(result) >= 0
