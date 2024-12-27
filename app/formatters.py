from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any
import json
import xml.etree.ElementTree as ET
from .validators import DataFormatter


class BaseFormatter(ABC):
    """Base class for all formatters."""

    def __init__(self):
        """Initialize the formatter with a data formatter."""
        self.data_formatter = DataFormatter()

    @abstractmethod
    def format_output(self, data: Dict[str, Any], tables: list = None) -> str:
        """Format the extracted data into the desired output format."""
        pass

    @staticmethod
    def format_currency(amount: str) -> str:
        """Format currency values."""
        try:
            value = Decimal(amount.replace(" ", "").replace(",", "."))
            return f"{value:,.2f}"
        except (ValueError, Decimal.InvalidOperation):
            return amount

    @staticmethod
    def format_date(date_str: str) -> str:
        """Format date strings."""
        if not date_str:
            return ""
        # Add date formatting logic here
        return date_str

    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone numbers."""
        digits = "".join(filter(str.isdigit, phone))
        if len(digits) == 8:
            return f"{digits[:2]} {digits[2:4]} {digits[4:6]} {digits[6:]}"
        return phone

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        return " ".join(text.split())

    @staticmethod
    def format_address(address: str) -> str:
        """Format address strings."""
        if not address:
            return ""
        parts = [p.strip() for p in address.split(",")]
        return "\n".join(p for p in parts if p)


class JSONFormatter(BaseFormatter):
    """Format data as JSON."""

    def format_output(self, data: Dict[str, Any], tables: list = None) -> str:
        """Format the data into JSON format."""
        formatted_data = {
            "invoice_details": {
                "company_registration": (
                    self.data_formatter.format_field("org_number", data.get("registration", ""))
                ),
                "invoice_number": data.get("invoice_number", ""),
                "issue_date": data.get("issue_date", ""),
                "due_date": data.get("due_date", ""),
                "contact_person": data.get("contact_person", ""),
                "financial": {
                    "total_amount": self.format_currency(data.get("total", "")),
                    "tax": self.format_currency(data.get("tax", "")),
                },
                "payment": {
                    "bank_account": data.get("bank_account", ""),
                    "reference": (
                        self.data_formatter.format_field("kid", data.get("reference", ""))
                    ),
                },
            }
        }

        if tables:
            formatted_data["tables"] = []
            for table in tables:
                table_data = {
                    "headers": table.headers if table.headers else [],
                    "rows": [[cell.value for cell in row.cells] for row in table.rows],
                }
                formatted_data["tables"].append(table_data)

        return json.dumps(formatted_data, indent=2)


class XMLFormatter(BaseFormatter):
    """Format data as XML."""

    def format_output(self, data: Dict[str, Any], tables: list = None) -> str:
        """Format the data into XML format."""
        root = ET.Element("invoice")

        # Company Information
        company = ET.SubElement(root, "company")
        reg = self.data_formatter.format_field("org_number", data.get("registration", ""))
        company.text = reg

        # Basic Information
        details = ET.SubElement(root, "details")
        ET.SubElement(details, "invoice_number").text = data.get("invoice_number", "")
        ET.SubElement(details, "issue_date").text = data.get("issue_date", "")
        ET.SubElement(details, "due_date").text = data.get("due_date", "")
        ET.SubElement(details, "contact_person").text = data.get("contact_person", "")

        # Financial Information
        financial = ET.SubElement(root, "financial")
        total = self.format_currency(data.get("total", ""))
        tax = self.format_currency(data.get("tax", ""))
        ET.SubElement(financial, "total_amount").text = total
        ET.SubElement(financial, "tax").text = tax

        # Payment Information
        payment = ET.SubElement(root, "payment")
        ET.SubElement(payment, "bank_account").text = data.get("bank_account", "")
        ref = self.data_formatter.format_field("kid", data.get("reference", ""))
        ET.SubElement(payment, "reference").text = ref

        # Add tables if present
        if tables:
            tables_elem = ET.SubElement(root, "tables")
            for table in tables:
                table_elem = ET.SubElement(tables_elem, "table")
                if table.headers:
                    headers_elem = ET.SubElement(table_elem, "headers")
                    for header in table.headers:
                        ET.SubElement(headers_elem, "header").text = header
                rows_elem = ET.SubElement(table_elem, "rows")
                for row in table.rows:
                    row_elem = ET.SubElement(rows_elem, "row")
                    for cell in row.cells:
                        ET.SubElement(row_elem, "cell").text = cell.value

        return ET.tostring(root, encoding="unicode", method="xml")
