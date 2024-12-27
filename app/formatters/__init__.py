"""Formatter implementations for various output formats."""

from typing import Any, Protocol

from app.formatters.base_formatter import BaseFormatter
from app.formatters.csv_formatter import CSVFormatter
from app.formatters.html_formatter import HTMLFormatter
from app.formatters.yaml_formatter import YAMLFormatter


class FormatterProtocol(Protocol):
    """Protocol defining the interface for formatters."""

    def format_output(self, data: dict[str, str], tables: list[list[list[str]]]) -> str:
        """Format the extracted data and tables into a specific output format."""
        ...

    def format_currency(self, amount: Any) -> str:
        """Format currency amounts according to locale."""
        ...


__all__ = ["BaseFormatter", "CSVFormatter", "HTMLFormatter", "YAMLFormatter", "FormatterProtocol"]
