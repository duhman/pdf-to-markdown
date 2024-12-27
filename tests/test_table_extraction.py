"""Tests for table extraction functionality."""


import pytest

from app.table_extractor import TableExtractor


@pytest.fixture
def extractor():
    return TableExtractor()


@pytest.fixture
def sample_text():
    return """
Description      Amount      Tax     Total
Item 1          1000,00    250,00   1250,00
Item 2           500,00    125,00    625,00
"""


@pytest.fixture
def sample_text_with_delimiters():
    return """
Description|Amount|Tax|Total
Item 1|1000,00|250,00|1250,00
Item 2|500,00|125,00|625,00
"""


def test_split_into_cells(extractor):
    """Test cell splitting with different delimiters."""
    # Test space-based splitting
    line = "Item 1          1000,00    250,00   1250,00"
    cells = extractor._split_into_cells(line)
    assert len(cells) == 4
    assert cells == ["Item 1", "1000,00", "250,00", "1250,00"]

    # Test delimiter-based splitting
    line = "Item 1|1000,00|250,00|1250,00"
    cells = extractor._split_into_cells(line)
    assert len(cells) == 4
    assert cells == ["Item 1", "1000,00", "250,00", "1250,00"]


def test_detect_table_structure(extractor, sample_text):
    """Test table structure detection."""
    lines = sample_text.strip().split("\n")
    tables = extractor.detect_table_structure(lines)

    assert len(tables) == 1
    table = tables[0]
    assert len(table) == 3  # Header + 2 rows
    assert len(table[0]) == 4  # 4 columns


def test_identify_columns(extractor, sample_text):
    """Test column type identification."""
    lines = sample_text.strip().split("\n")
    table = extractor.detect_table_structure(lines)[0]
    column_types = extractor.identify_columns(table)

    assert len(column_types) == 4
    assert column_types[0] == "description"  # First column
    assert column_types[1] == "amount"  # Second column
    assert column_types[2] == "amount"  # Third column
    assert column_types[3] == "amount"  # Fourth column


def test_to_markdown(extractor, sample_text):
    """Test markdown conversion."""
    lines = sample_text.strip().split("\n")
    table = extractor.detect_table_structure(lines)[0]
    column_types = extractor.identify_columns(table)
    markdown = extractor.to_markdown(table, column_types)

    assert "|" in markdown
    assert "Description" in markdown
    assert "Amount" in markdown
    assert "---" in markdown  # Header separator
    assert "1000,00" in markdown
    assert "250,00" in markdown


def test_empty_table(extractor):
    """Test handling of empty tables."""
    tables = extractor.detect_table_structure([])
    assert len(tables) == 0

    markdown = extractor.to_markdown([], {})
    assert markdown == ""


def test_single_column_table(extractor):
    """Test handling of single-column tables."""
    text = """
Description
Item 1
Item 2
"""
    lines = text.strip().split("\n")
    tables = extractor.detect_table_structure(lines)

    assert len(tables) == 0  # Should not detect as table (min 2 columns)


def test_irregular_table(extractor):
    """Test handling of irregular tables."""
    text = """
Description      Amount      Tax
Item 1          1000,00    250,00   1250,00
Item 2          500,00
"""
    lines = text.strip().split("\n")
    tables = extractor.detect_table_structure(lines)

    assert len(tables) == 1
    table = tables[0]
    assert all(len(row) == len(table[0]) for row in table)  # All rows should have same length


def test_multiple_tables(extractor):
    """Test detection of multiple tables."""
    text = """
Table 1:
Description      Amount      Tax
Item 1          1000,00    250,00

Table 2:
Product         Price       VAT
Product 1       800,00     200,00
"""
    lines = text.strip().split("\n")
    tables = extractor.detect_table_structure(lines)

    assert len(tables) == 2
    assert len(tables[0]) == 2  # First table: header + 1 row
    assert len(tables[1]) == 2  # Second table: header + 1 row


def test_amount_detection(extractor):
    """Test amount pattern detection."""
    assert extractor.amount_pattern.search("1000,00")
    assert extractor.amount_pattern.search("1.000,00")
    assert extractor.amount_pattern.search("1000,00 kr")
    assert extractor.amount_pattern.search("1000,00 NOK")
    assert not extractor.amount_pattern.search("abcd")
