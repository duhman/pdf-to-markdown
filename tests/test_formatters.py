"""Test cases for formatters."""

import pytest
from typing import Union
from app.formatters.csv_formatter import CSVFormatter
from app.formatters.html_formatter import HTMLFormatter
from app.formatters.yaml_formatter import YAMLFormatter
from app.formatters.base_formatter import BaseFormatter


@pytest.fixture
def sample_data() -> dict[str, str]:
    """Sample invoice data for testing."""
    return {
        "invoice_number": "1122",
        "customer_name": "Øystein Åsen",
        "amount": "1000,00",
        "vat": "250,00",
    }


@pytest.fixture
def sample_tables() -> list[list[list[str]]]:
    """Sample table data for testing."""
    return [[["Description", "Amount", "Tax", "Total"], ["Item 1", "1000,00", "250,00", "1250,00"]]]


def test_csv_formatter(sample_data: dict[str, str], sample_tables: list[list[list[str]]]) -> None:
    """Test CSV formatter."""
    formatter = CSVFormatter()
    result = formatter.format_output(sample_data, sample_tables)

    assert "1122" in result
    assert "Øystein Åsen" in result
    assert "1000,00" in result
    assert "250,00" in result


def test_html_formatter(sample_data: dict[str, str], sample_tables: list[list[list[str]]]) -> None:
    """Test HTML formatter."""
    formatter = HTMLFormatter()
    result = formatter.format_output(sample_data, sample_tables)

    assert "<html>" in result
    assert "1122" in result
    assert "Øystein Åsen" in result
    assert "1000,00" in result
    assert "250,00" in result
    assert "</html>" in result


def test_yaml_formatter(sample_data: dict[str, str], sample_tables: list[list[list[str]]]) -> None:
    """Test YAML formatter."""
    formatter = YAMLFormatter()
    result = formatter.format_output(sample_data, sample_tables)

    assert "invoice_number: '1122'" in result
    assert "customer_name: Øystein Åsen" in result
    assert "amount: '1000,00'" in result
    assert "vat: '250,00'" in result


def test_empty_input() -> None:
    """Test formatters with empty input."""
    empty_data: dict[str, str] = {}
    empty_tables: list[list[list[str]]] = []

    # Test each formatter
    formatters = [CSVFormatter(), HTMLFormatter(), YAMLFormatter()]

    for formatter in formatters:
        result = formatter.format_output(empty_data, empty_tables)
        assert isinstance(result, str)


def test_base_formatter() -> None:
    """Test base formatter functionality."""
    class TestFormatter(BaseFormatter):
        def format_output(self, data: dict[str, str], tables: list[list[list[str]]]) -> str:
            return "test"

    formatter = TestFormatter()
    assert formatter.format_currency(1234.56) == "1234.56"
    assert formatter.format_currency(1000) == "1000.00"
    assert formatter.format_currency("1234.56") == "1234.56"


def test_currency_formatting() -> None:
    """Test currency formatting in formatters."""
    formatters = [HTMLFormatter(), CSVFormatter(), YAMLFormatter()]
    test_values: list[Union[str, float, int]] = [1000.00, 1000, "1000.00"]
    
    for formatter in formatters:
        for value in test_values:
            result = formatter.format_currency(value)
            assert isinstance(result, str)
            assert "." in result or "," in result


def test_html_table_formatting() -> None:
    """Test HTML table formatting."""
    formatter = HTMLFormatter()
    tables = [[["Header 1", "Header 2"], ["Value 1", "Value 2"]]]
    result = formatter.format_output({}, tables)
    assert "<table>" in result
    assert "<th>Header 1</th>" in result
    assert "<td>Value 1</td>" in result
    assert "</table>" in result
