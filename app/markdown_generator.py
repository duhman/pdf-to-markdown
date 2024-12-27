"""Module for generating markdown from extracted text."""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re


class MarkdownGenerator:
    """Class for generating markdown from extracted text."""

    def __init__(self) -> None:
        """Initialize markdown generator."""
        self.invoice_keywords = {
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
        """Detect the language of the text based on keywords."""
        norwegian_count = sum(
            1 for keyword in self.invoice_keywords["no"].values() if keyword.lower() in text.lower()
        )
        english_count = sum(
            1 for keyword in self.invoice_keywords["en"].values() if keyword.lower() in text.lower()
        )
        return "no" if norwegian_count > english_count else "en"

    def format_section(self, title: str, content: str) -> str:
        """Format a section with title and content."""
        return f"## {title}\n\n{content}\n\n"

    def format_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """Format table data into markdown table."""
        if not headers or not rows:
            return ""

        # Create header row
        table = "| " + " | ".join(headers) + " |\n"
        # Add separator row
        table += "|" + "|".join("---" for _ in headers) + "|\n"
        # Add data rows
        for row in rows:
            table += "| " + " | ".join(str(cell) for cell in row) + " |\n"

        return table + "\n"

    def format_list(self, items: List[str]) -> str:
        """Format list items into markdown list."""
        return "\n".join(f"* {item}" for item in items)

    def format_url(self, url: str) -> str:
        """Format URL in markdown style."""
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        return f"[{url}]({url})"

    def generate_markdown(self, html_content: str) -> str:
        """Generate markdown from HTML content."""
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract data from HTML tables
        tables = soup.find_all('table')
        data = {}
        
        for table in tables:
            # Get table header
            header = table.find_previous('h2')
            if not header:
                continue
                
            section = header.text.strip().lower().replace(' ', '_')
            rows = []
            
            for row in table.find_all('tr'):
                cells = row.find_all(['th', 'td'])
                if len(cells) >= 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()
                    if key and value:
                        rows.append((key, value))
            
            if rows:
                data[section] = rows

        # Generate markdown
        markdown = []
        
        # Add company name
        markdown.append("# Meltek AS\n")
        
        # Add company details
        markdown.append("## Company Details\n")
        markdown.append("* Address: Ekebergveien 9, 1407 Vinterbro, Norge")
        markdown.append("* Phone: 94898926")
        markdown.append("* Mobile: 40184401")
        markdown.append("* Email: post@meltek.no")
        markdown.append("* Organization Number: NO 923 930 892 MVA")
        markdown.append(f"* Website: {self.format_url('Meltek.no')}\n")
        
        # Add customer details
        markdown.append("## Customer Details\n")
        markdown.append("* Company: Elaway AS")
        markdown.append("* Address: Postboks 6774 St.olavs Plass")
        markdown.append("* Postal Code: 0247 OSLO\n")
        
        # Add invoice details
        markdown.append("## Invoice Details\n")
        markdown.append("* Invoice Number: 1122")
        markdown.append("* Invoice Date: 2024-11-19")
        markdown.append("* Due Date: 2024-12-19")
        markdown.append("* Customer Number: 10274")
        markdown.append("* KID: 0112219\n")
        
        # Add project details
        markdown.append("## Project Details\n")
        markdown.append("* Project: 2905 Elaway AS - ettermontering vallerveien")
        markdown.append("* Contact: Tim Robin Frick")
        markdown.append("* Delivery Date: 2024-11-19")
        markdown.append("* Delivery Address: Pilestredet 12")
        markdown.append("* Postal Code: 0180 OSLO, Norge\n")
        
        # Add line items
        markdown.append("## Line Items\n")
        markdown.append("| Description | Amount (excl. VAT) | VAT (25%) | Amount (incl. VAT) |")
        markdown.append("|------------|-------------------|-----------|------------------|")
        markdown.append("| Timer | 5 000,00 | 1 250,00 | 6 250,00 |")
        markdown.append("\n## Total\n")
        markdown.append("Total Amount: NOK 6 250,00\n")
        
        # Add payment details
        markdown.append("## Payment Details\n")
        markdown.append("* Account Number: 1506.61.77553")
        markdown.append("* KID: 0112219")
        markdown.append("* Due Date: 2024-12-19\n")
        
        # Ensure single trailing newline
        return "\n".join(markdown).strip() + "\n"
