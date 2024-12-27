"""Module for generating markdown from extracted text."""

from typing import Dict, List, Optional


class MarkdownGenerator:
    """Class for generating markdown from extracted text."""

    def __init__(self) -> None:
        """Initialize markdown generator with language-specific keywords."""
        self.invoice_keywords: Dict[str, Dict[str, str]] = {
            "en": {
                "invoice": "Invoice",
                "date": "Date",
                "amount": "Amount",
                "tax": "Tax",
                "total": "Total",
            },
            "no": {
                "invoice": "Faktura",
                "date": "Dato",
                "amount": "Beløp",
                "tax": "MVA",
                "total": "Total",
            },
        }

    def detect_language(self, text: str) -> str:
        """Detect the language of the text based on keywords.

        Args:
            text: Input text to analyze

        Returns:
            Language code ('en' or 'no')
        """
        norwegian_count = sum(
            1 for keyword in self.invoice_keywords["no"].values() if keyword.lower() in text.lower()
        )
        english_count = sum(
            1 for keyword in self.invoice_keywords["en"].values() if keyword.lower() in text.lower()
        )

        return "no" if norwegian_count > english_count else "en"

    def format_section(self, title: str, content: str) -> str:
        """Format a section with title and content.

        Args:
            title: Section title
            content: Section content

        Returns:
            Formatted markdown section
        """
        return f"## {title}\n\n{content}\n\n"

    def format_table(self, table_data: List[List[str]]) -> str:
        """Format table data into markdown table.

        Args:
            table_data: List of rows, where each row is a list of cells

        Returns:
            Formatted markdown table
        """
        if not table_data:
            return ""

        # Create header row
        table = "| " + " | ".join(table_data[0]) + " |\n"
        # Add separator row
        table += "|" + "|".join("---" for _ in table_data[0]) + "|\n"
        # Add data rows
        for row in table_data[1:]:
            table += "| " + " | ".join(row) + " |\n"

        return table

    def format_list(self, items: List[str]) -> str:
        """Format list items into markdown list.

        Args:
            items: List of items to format

        Returns:
            Formatted markdown list
        """
        return "\n".join(f"* {item}" for item in items)

    def generate_markdown(self, text: str, language: Optional[str] = None) -> str:
        """Generate markdown from extracted text.

        Args:
            text: Input text to convert to markdown
            language: Optional language code ('en' or 'no')

        Returns:
            Formatted markdown string
        """
        if not text.strip():
            return ""

        lang = language or self.detect_language(text)
        keywords = self.invoice_keywords[lang]

        sections: Dict[str, str] = {}
        current_section = "General"

        for raw_line in text.strip().split("\n"):
            line = raw_line.strip()
            if not line:
                continue

            # Check if line is a section header
            if any(keyword.lower() in line.lower() for keyword in keywords.values()):
                current_section = line
                sections[current_section] = ""
            else:
                if current_section not in sections:
                    sections[current_section] = ""
                sections[current_section] += line + "\n"

        # Generate markdown
        markdown = ""
        for section, content in sections.items():
            if section != "General":
                markdown += self.format_section(section, content)
            else:
                markdown += content + "\n"

        return markdown.strip()
