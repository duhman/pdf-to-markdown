"""Table extraction module."""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class TableCell:
    """Table cell data."""

    text: str
    row: int
    col: int


@dataclass
class TableRow:
    """Table row data."""

    cells: List[TableCell]
    is_header: bool = False


class TableExtractor:
    """Extract tables from text."""

    def __init__(self) -> None:
        """Initialize the TableExtractor."""
        self.amount_pattern = re.compile(r"\d+[\s.,]\d+(?:[\s.,]\d+)*(?:\s*(?:kr|NOK))?")
        self.quantity_pattern = re.compile(r"^\d+(?:[,.]\d+)?$")
        self.table_patterns = [
            r"\|[^|]+\|[^|]+\|",  # Basic table pattern
            r"[-]+\s+[-]+",  # Separator line pattern
        ]

    def detect_table_structure(self, lines: List[str]) -> List[List[List[str]]]:
        """Detect potential table structure in text lines.

        Args:
            lines: Text lines to detect tables from.

        Returns:
            List of tables, where each table is a list of rows,
            and each row is a list of cells.
        """
        tables: List[List[List[str]]] = []
        current_table: List[List[str]] = []

        for line in lines:
            line = line.strip()
            if not line:
                if current_table:
                    if len(current_table) > 2:  # Minimum table size
                        tables.append(current_table)
                    current_table = []
                continue

            cells = self._split_into_cells(line)
            if cells:
                current_table.append(cells)

        if current_table and len(current_table) > 2:
            tables.append(current_table)

        # Normalize tables
        normalized_tables = []
        for table in tables:
            # Find max number of columns
            max_cols = max(len(row) for row in table)

            # Normalize each row to have the same number of columns
            normalized_table = []
            for row in table:
                if len(row) < max_cols:
                    row.extend([""] * (max_cols - len(row)))
                normalized_table.append(row)

            normalized_tables.append(normalized_table)

        return normalized_tables

    def _split_into_cells(self, line: str) -> List[str]:
        """Split a line into cells based on delimiters and spacing.

        Args:
            line: Line to split.

        Returns:
            List of cell values.
        """
        # First try splitting by common delimiters
        if "|" in line:
            cells = [cell.strip() for cell in line.split("|")]
            return [cell for cell in cells if cell]

        # Then try splitting by multiple spaces
        cells = re.split(r"\s{2,}", line.strip())
        if len(cells) > 1:
            return cells

        # Finally, try splitting by tabs
        cells = line.split("\t")
        if len(cells) > 1:
            return [cell.strip() for cell in cells if cell.strip()]

        # If no clear delimiter is found, treat as single cell
        return [line] if line else []

    def _normalize_cells(self, cells: List[str]) -> List[str]:
        """Normalize cell values by removing extra whitespace."""
        final_cells = []
        for cell in cells:
            cell = cell.strip()
            if cell and not cell.isspace():
                final_cells.append(cell)
        return [cell for cell in final_cells if cell]

    def identify_column_types(self, table: List[List[str]]) -> Dict[int, str]:
        """Identify column types based on content.

        Args:
            table: Table to identify columns from.

        Returns:
            Dictionary of column types, where keys are column indices.
        """
        if not table or not table[0]:
            return {}

        column_types: Dict[int, str] = {}
        num_columns = len(table[0])

        for col in range(num_columns):
            column_values = [row[col] for row in table[1:] if col < len(row)]

            # Check if column contains amounts
            if any(self.amount_pattern.match(val) for val in column_values):
                column_types[col] = "amount"
            # Check if column contains quantities
            elif any(self.quantity_pattern.match(val) for val in column_values):
                column_types[col] = "quantity"
            else:
                column_types[col] = "text"

        return column_types

    def format_table(self, table: List[List[str]], column_types: Dict[int, str]) -> str:
        """Convert table to markdown format.

        Args:
            table: Table to convert.
            column_types: Dictionary of column types.

        Returns:
            Markdown formatted table.
        """
        if not table:
            return ""

        # Format header row
        header_row = table[0]
        markdown = "| " + " | ".join(header_row) + " |\n"

        # Add separator row with alignment
        separator_parts = []
        for i in range(len(header_row)):
            col_type = column_types.get(i, "text")
            if col_type in ("amount", "quantity"):
                separator_parts.append(":---:")  # Center align numbers
            else:
                separator_parts.append("---")  # Left align text

        markdown += "|" + "|".join(separator_parts) + "|\n"

        # Format data rows
        for row in table[1:]:
            formatted_cells = []
            for i, cell in enumerate(row):
                col_type = column_types.get(i, "text")
                if col_type == "amount":
                    # Format amount with Norwegian style (space as thousand separator)
                    cell = re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1 ", cell)
                formatted_cells.append(cell)
            markdown += "| " + " | ".join(formatted_cells) + " |\n"

        return markdown

    def extract_tables(self, text: str) -> List[str]:
        """Extract and convert tables from text to markdown.

        Args:
            text: Text to extract tables from.

        Returns:
            List of markdown formatted tables.
        """
        lines = text.split("\n")
        tables = self.detect_table_structure(lines)
        markdown_tables = []

        for table in tables:
            column_types = self.identify_column_types(table)
            markdown_table = self.format_table(table, column_types)
            if markdown_table:
                markdown_tables.append(markdown_table)

        return markdown_tables

    def find_table_boundaries(self, text: str) -> List[Tuple[int, int]]:
        """Find the start and end lines of tables in text.

        Args:
            text: Text to search for tables.

        Returns:
            List of (start_line, end_line) tuples.
        """
        lines = text.split("\n")
        boundaries: List[Tuple[int, int]] = []
        start_line: Optional[int] = None

        for i, line in enumerate(lines):
            if self._is_table_line(line):
                if start_line is None:
                    start_line = i
            elif start_line is not None:
                if i - start_line > 2:  # Minimum table size
                    boundaries.append((start_line, i - 1))
                start_line = None

        if start_line is not None and len(lines) - start_line > 2:
            boundaries.append((start_line, len(lines) - 1))

        return boundaries

    def _is_table_line(self, line: str) -> bool:
        """Check if a line is part of a table.

        Args:
            line: Line to check.

        Returns:
            True if the line is part of a table, False otherwise.
        """
        return any(re.search(pattern, line) for pattern in self.table_patterns)
