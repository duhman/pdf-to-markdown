import csv
from io import StringIO
from typing import Dict, Any, List
from ..validators import DataFormatter


class CSVFormatter:
    def __init__(self):
        self.data_formatter = DataFormatter()

    def format(self, data: Dict[str, Any], tables: list = None) -> str:
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Field", "Value"])

        # Company Information
        if data.get("registration"):
            writer.writerow(
                [
                    "Company Registration",
                    self.data_formatter.format_field("org_number", data["registration"]),
                ]
            )

        # Basic Invoice Information
        writer.writerow(["Invoice Number", data.get("invoice_number", "")])
        writer.writerow(["Date", data.get("date", "")])
        if data.get("due_date"):
            writer.writerow(["Due Date", data["due_date"]])

        # Contact Information
        if data.get("contact_person"):
            writer.writerow(["Contact Person", data["contact_person"]])

        # Financial Information
        if data.get("total"):
            writer.writerow(
                ["Total Amount", self.data_formatter.format_field("currency", data["total"])]
            )
        if data.get("tax"):
            writer.writerow(["Tax", self.data_formatter.format_field("currency", data["tax"])])

        # Payment Information
        if data.get("bank_account"):
            writer.writerow(
                [
                    "Bank Account",
                    self.data_formatter.format_field("account_number", data["bank_account"]),
                ]
            )
        if data.get("reference"):
            writer.writerow(
                ["Reference", self.data_formatter.format_field("kid", data["reference"])]
            )

        # Add tables if present
        if tables:
            writer.writerow([])  # Empty row for separation
            writer.writerow(["Line Items"])
            for table in tables:
                writer.writerow([])
                for line in table.split("\n"):
                    if line.strip():
                        writer.writerow([line.strip()])

        return output.getvalue()
