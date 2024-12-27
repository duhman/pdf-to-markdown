"""CSV formatter implementation."""

import csv
from io import StringIO
from typing import Any, Dict, List, Optional

from app.formatters import BaseFormatter


class CSVFormatter(BaseFormatter):
    """Format data as CSV."""

    def __init__(self) -> None:
        super().__init__()

    def format_field(self, value: str | float | int) -> str:
        """Format a field value."""
        if isinstance(value, (float, int)):
            return self.format_currency(value)
        return str(value)

    def format_output(self, data: Dict[str, Any], tables: Optional[List[Any]] = None) -> str:
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
                    self.format_field(data["registration"]),
                ]
            )

        # Write basic invoice information
        writer.writerow(["Invoice Number", self.format_field(data.get("invoice_number", ""))])
        writer.writerow(["Issue Date", self.format_field(data.get("issue_date", ""))])
        writer.writerow(["Due Date", self.format_field(data.get("due_date", ""))])
        writer.writerow(["Contact Person", self.format_field(data.get("contact_person", ""))])

        # Write financial information
        if data.get("total"):
            writer.writerow(["Total Amount", self.format_field(data["total"])])
        if data.get("tax"):
            writer.writerow(["Tax", self.format_field(data["tax"])])

        # Write payment information
        if data.get("bank_account"):
            writer.writerow(["Bank Account", self.format_field(data["bank_account"])])
        if data.get("reference"):
            writer.writerow(["Reference", self.format_field(data["reference"])])

        # Add tables if present
        if tables:
            writer.writerow([])  # Empty row for separation
            writer.writerow(["Table Data"])
            for table in tables:
                writer.writerow([])  # Empty row between tables
                if table.headers:
                    writer.writerow(table.headers)
                for row in table.rows:
                    writer.writerow([self.format_field(cell.value) for cell in row.cells])

        return output.getvalue()
