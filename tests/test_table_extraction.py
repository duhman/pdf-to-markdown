"""Tests for table extraction functionality."""

import cv2  # type: ignore
import numpy as np  # type: ignore
import pytest  # type: ignore
from numpy.typing import NDArray  # type: ignore

from app.table_extractor import TableExtractor


@pytest.fixture
def extractor() -> TableExtractor:
    """Create a table extractor instance."""
    return TableExtractor()


@pytest.fixture
def sample_text() -> str:
    return """
Description      Amount      Tax     Total
Item 1          1000,00    250,00   1250,00
Item 2           500,00    125,00    625,00
"""


@pytest.fixture
def sample_text_with_delimiters() -> str:
    return """
Description|Amount|Tax|Total
Item 1|1000,00|250,00|1250,00
Item 2|500,00|125,00|625,00
"""


@pytest.fixture
def sample_table_image() -> NDArray[np.uint8]:
    """Create a sample table image for testing."""
    # Create a simple table image
    img = np.zeros((400, 600), dtype=np.uint8)
    # Add horizontal lines
    img[50:52, :] = 255  # Header line
    img[100:102, :] = 255  # Row line
    img[150:152, :] = 255  # Row line
    # Add vertical lines
    img[:, 100:102] = 255  # Column line
    img[:, 300:302] = 255  # Column line
    img[:, 500:502] = 255  # Column line
    return img


def test_split_into_cells(extractor: TableExtractor) -> None:
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


def test_detect_table_structure(extractor: TableExtractor, sample_text: str) -> None:
    """Test table structure detection."""
    lines = sample_text.strip().split("\n")
    tables = extractor.detect_table_structure(lines)

    assert len(tables) == 1
    table = tables[0]
    assert len(table) == 3  # Header + 2 rows
    assert len(table[0]) == 4  # 4 columns


def test_identify_columns(extractor: TableExtractor, sample_text: str) -> None:
    """Test column type identification."""
    lines = sample_text.strip().split("\n")
    table = extractor.detect_table_structure(lines)[0]
    column_types = extractor.identify_column_types(table)

    assert len(column_types) == 4
    assert column_types[0] == "description"  # First column
    assert column_types[1] == "amount"  # Second column
    assert column_types[2] == "amount"  # Third column
    assert column_types[3] == "amount"  # Fourth column


def test_empty_table(extractor: TableExtractor) -> None:
    """Test handling of empty tables."""
    tables = extractor.detect_table_structure([])
    assert len(tables) == 0


def test_single_column_table(extractor: TableExtractor) -> None:
    """Test handling of single-column tables."""
    text = """
Description
Item 1
Item 2
"""
    lines = text.strip().split("\n")
    tables = extractor.detect_table_structure(lines)

    assert len(tables) == 0  # Should not detect as table (min 2 columns)


def test_irregular_table(extractor: TableExtractor) -> None:
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


def test_multiple_tables(extractor: TableExtractor) -> None:
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


def test_amount_detection(extractor: TableExtractor) -> None:
    """Test amount pattern detection."""
    assert extractor.amount_pattern.search("1000,00")
    assert extractor.amount_pattern.search("1.000,00")
    assert extractor.amount_pattern.search("1000,00 kr")
    assert extractor.amount_pattern.search("1000,00 NOK")
    assert not extractor.amount_pattern.search("abcd")


def test_detect_lines(extractor: TableExtractor) -> None:
    """Test line detection in table image."""
    # TODO: implement test_detect_lines


def test_detect_cells(extractor: TableExtractor) -> None:
    """Test cell detection in table."""
    # TODO: implement test_detect_cells


def test_extract_cell_content(extractor: TableExtractor) -> None:
    """Test cell content extraction."""
    # TODO: implement test_extract_cell_content


def test_process_table(extractor: TableExtractor) -> None:
    """Test complete table processing."""
    # TODO: implement test_process_table


def test_noisy_image(extractor: TableExtractor, sample_table_image: NDArray[np.uint8]) -> None:
    """Test handling of noisy image."""
    noise = np.random.normal(0, 25, sample_table_image.shape).astype(np.uint8)
    noisy_image = cv2.add(sample_table_image, noise)
    structure = extractor.detect_table_structure(noisy_image)
    assert isinstance(structure, list)


def test_identify_column_types(extractor: TableExtractor) -> None:
    """Test column type identification."""
    table_data = [
        ["ID", "Name", "Age", "Salary"],
        ["1", "John Doe", "30", "50000"],
        ["2", "Jane Smith", "25", "60000"],
    ]
    column_types = extractor.identify_column_types(table_data)
    assert len(column_types) == 4
    assert column_types[0] == "numeric"  # ID column
    assert column_types[1] == "text"  # Name column
    assert column_types[2] == "numeric"  # Age column
    assert column_types[3] == "numeric"  # Salary column
