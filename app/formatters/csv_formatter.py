"""CSV formatter implementation."""

import csv
from io import StringIO
from typing import Any, Dict

from ..formatters import BaseFormatter


class CSVFormatter(BaseFormatter):
    """Format data as CSV."""

    def format_output(self, data: Dict[str, Any], tables: list = None) -> str:
        """Format the data into CSV format."""
        output = StringIO()
        writer = csv.writer(output, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Write headers
        headers = ["Field", "Value"]
        writer.writerow(headers)

        # Write company information
        if data.get("registration"):
            writer.writerow(
                [
                    "Company Registration",
                    self.data_formatter.format_field("org_number", data["registration"]),
                ]
            )

        # Write basic invoice information
        writer.writerow(["Invoice Number", data.get("invoice_number", "")])
        writer.writerow(["Issue Date", data.get("issue_date", "")])
        writer.writerow(["Due Date", data.get("due_date", "")])
        writer.writerow(["Contact Person", data.get("contact_person", "")])

        # Write financial information
        if data.get("total"):
            writer.writerow(["Total Amount", self.format_currency(data["total"])])
        if data.get("tax"):
            writer.writerow(["Tax", self.format_currency(data["tax"])])

        # Write payment information
        if data.get("bank_account"):
            writer.writerow(["Bank Account", data["bank_account"]])
        if data.get("reference"):
            writer.writerow(
                ["Reference", self.data_formatter.format_field("kid", data["reference"])]
            )

        # Add tables if present
        if tables:
            writer.writerow([])  # Empty row for separation
            writer.writerow(["Table Data"])
            for table in tables:
                writer.writerow([])  # Empty row between tables
                if table.headers:
                    writer.writerow(table.headers)
                for row in table.rows:
                    writer.writerow([cell.value for cell in row.cells])

        return output.getvalue()
