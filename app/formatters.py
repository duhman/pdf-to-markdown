import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, Optional

from .validators import DataFormatter


class BaseFormatter:
    def __init__(self):
        self.data_formatter = DataFormatter()

    def format_field(self, field_type: str, value: str, language: str = "no") -> str:
        return self.data_formatter.format_field(field_type, value, language)


class MarkdownFormatter(BaseFormatter):
    def format(self, data: Dict[str, Any], tables: list = None) -> str:
        markdown = "# Invoice Details\n\n"

        # Company Information
        if data.get("registration"):
            markdown += f"## Company Registration\n{self.format_field('org_number', data['registration'])}\n\n"

        # Basic Invoice Information
        markdown += f"## Invoice Number\n{data.get('invoice_number', '')}\n\n"
        markdown += f"## Date\n{data.get('date', '')}\n\n"
        if data.get("due_date"):
            markdown += f"## Due Date\n{data['due_date']}\n\n"

        # Contact Information
        if data.get("contact_person"):
            markdown += f"## Contact Person\n{data['contact_person']}\n\n"

        # Financial Information
        if data.get("total"):
            markdown += f"## Total Amount\n{self.format_field('currency', data['total'])}\n\n"
        if data.get("tax"):
            markdown += f"## Tax\n{self.format_field('currency', data['tax'])}\n\n"

        # Payment Information
        markdown += "## Payment Information\n"
        if data.get("bank_account"):
            markdown += f"Bank Account: {data['bank_account']}\n"
        if data.get("reference"):
            markdown += f"Reference: {self.format_field('kid', data['reference'])}\n\n"

        # Add tables if present
        if tables:
            markdown += "## Line Items\n\n"
            for table in tables:
                markdown += table + "\n"

        return markdown


class JSONFormatter(BaseFormatter):
    def format(self, data: Dict[str, Any], tables: list = None) -> str:
        formatted_data = {
            "invoice_details": {
                "company_registration": self.format_field(
                    "org_number", data.get("registration", "")
                ),
                "invoice_number": data.get("invoice_number", ""),
                "date": data.get("date", ""),
                "due_date": data.get("due_date", ""),
                "contact_person": data.get("contact_person", ""),
                "financial": {
                    "total_amount": self.format_field("currency", data.get("total", "")),
                    "tax": self.format_field("currency", data.get("tax", "")),
                },
                "payment": {
                    "bank_account": data.get("bank_account", ""),
                    "reference": self.format_field("kid", data.get("reference", "")),
                },
            }
        }

        if tables:
            formatted_data["line_items"] = tables

        return json.dumps(formatted_data, indent=2, ensure_ascii=False)


class XMLFormatter(BaseFormatter):
    def format(self, data: Dict[str, Any], tables: list = None) -> str:
        root = ET.Element("invoice")

        # Company Information
        company = ET.SubElement(root, "company_registration")
        company.text = self.format_field("org_number", data.get("registration", ""))

        # Basic Information
        details = ET.SubElement(root, "details")
        ET.SubElement(details, "invoice_number").text = data.get("invoice_number", "")
        ET.SubElement(details, "date").text = data.get("date", "")
        ET.SubElement(details, "due_date").text = data.get("due_date", "")

        # Contact Information
        if data.get("contact_person"):
            contact = ET.SubElement(root, "contact")
            ET.SubElement(contact, "person").text = data["contact_person"]

        # Financial Information
        financial = ET.SubElement(root, "financial")
        ET.SubElement(financial, "total_amount").text = self.format_field(
            "currency", data.get("total", "")
        )
        ET.SubElement(financial, "tax").text = self.format_field("currency", data.get("tax", ""))

        # Payment Information
        payment = ET.SubElement(root, "payment")
        ET.SubElement(payment, "bank_account").text = data.get("bank_account", "")
        ET.SubElement(payment, "reference").text = self.format_field(
            "kid", data.get("reference", "")
        )

        # Line Items
        if tables:
            line_items = ET.SubElement(root, "line_items")
            for i, table in enumerate(tables):
                table_elem = ET.SubElement(line_items, f"table_{i+1}")
                table_elem.text = table

        return ET.tostring(root, encoding="unicode", method="xml")
