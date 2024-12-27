"""Base formatter class for output formatting."""

from abc import ABC, abstractmethod
from typing import List, Union


class BaseFormatter(ABC):
    """Abstract base class for formatters."""

    def __init__(self) -> None:
        self.data_formatter = self.format_currency

    @abstractmethod
    def format_output(self, data: dict[str, str], tables: list[list[list[str]]]) -> str:
        """Format the extracted data and tables.

        Args:
            data: Dictionary of key-value pairs
            tables: List of tables, where each table is a list of rows

        Returns:
            Formatted output as string
        """
        pass

    def format_currency(self, amount: Union[str, float, int]) -> str:
        """Format currency amounts according to locale.

        Args:
            amount: Amount to format

        Returns:
            Formatted currency string
        """
        try:
            # Convert to float for standardization
            value = float(str(amount).replace(",", "."))
            # Format with Norwegian style (comma as decimal separator)
            return f"{value:,.2f}".replace(",", " ").replace(".", ",")
        except (ValueError, TypeError):
            return str(amount)

    def format_list(self, items: List[str]) -> str:
        """Format a list of items.

        Args:
            items: List of items to format

        Returns:
            Formatted list as string
        """
        return "\n".join(f"* {item}" for item in items)

    def format_table(self, rows: List[List[str]]) -> str:
        """Format a table.

        Args:
            rows: List of rows, where each row is a list of cells

        Returns:
            Formatted table as string
        """
        if not rows:
            return ""

        # Calculate column widths
        col_widths = [max(len(str(cell)) for cell in column) for column in zip(*rows)]

        # Create header separator
        separator = "|" + "|".join("-" * width for width in col_widths) + "|"

        # Format rows
        formatted_rows = []
        for i, row in enumerate(rows):
            cells = [str(cell).ljust(width) for cell, width in zip(row, col_widths)]
            formatted_rows.append("|" + "|".join(cells) + "|")
            if i == 0:  # After header
                formatted_rows.append(separator)

        return "\n".join(formatted_rows)
