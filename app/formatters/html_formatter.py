"""Format data as HTML."""

from typing import Any, Dict, List, Optional

from app.formatters import BaseFormatter


class HTMLFormatter(BaseFormatter):
    def __init__(self) -> None:
        super().__init__()

    def format_field(self, value: str | float | int) -> str:
        """Format a field value."""
        if isinstance(value, (float, int)):
            return self.format_currency(value)
        return str(value)

    def format_output(self, data: Dict[str, Any], tables: Optional[List[Any]] = None) -> str:
        """Format the data into HTML format."""
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Invoice Details</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            "table { border-collapse: collapse; width: 100%; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            "</style>",
            "</head>",
            "<body>",
        ]

        # Company Information
        html.append("<h1>Invoice Details</h1>")
        if data.get("registration"):
            html.append("<h2>Company Registration</h2>")
            reg_num = self.format_field(data["registration"])
            html.append(f"<p>{reg_num}</p>")

        # Basic Invoice Information
        html.append("<h2>Basic Information</h2>")
        html.append("<table>")
        html.append("<tr><th>Field</th><th>Value</th></tr>")
        html.append(
            f"<tr><td>Invoice Number</td><td>{self.format_field(data.get('invoice_number', ''))}</td></tr>"
        )
        html.append(
            f"<tr><td>Issue Date</td><td>{self.format_field(data.get('issue_date', ''))}</td></tr>"
        )
        html.append(
            f"<tr><td>Due Date</td><td>{self.format_field(data.get('due_date', ''))}</td></tr>"
        )
        html.append(
            f"<tr><td>Contact Person</td><td>{self.format_field(data.get('contact_person', ''))}</td></tr>"
        )
        html.append("</table>")

        # Financial Information
        html.append("<h2>Financial Information</h2>")
        html.append("<table>")
        html.append("<tr><th>Field</th><th>Value</th></tr>")
        if data.get("total"):
            total = self.format_field(data["total"])
            html.append(f"<tr><td>Total Amount</td><td>{total}</td></tr>")
        if data.get("tax"):
            tax = self.format_field(data["tax"])
            html.append(f"<tr><td>Tax</td><td>{tax}</td></tr>")
        html.append("</table>")

        # Payment Information
        html.append("<h2>Payment Information</h2>")
        html.append("<table>")
        html.append("<tr><th>Field</th><th>Value</th></tr>")
        if data.get("bank_account"):
            html.append(
                f"<tr><td>Bank Account</td><td>{self.format_field(data['bank_account'])}</td></tr>"
            )
        if data.get("reference"):
            ref = self.format_field(data["reference"])
            html.append(f"<tr><td>Reference</td><td>{ref}</td></tr>")
        html.append("</table>")

        # Add tables if present
        if tables:
            html.append("<h2>Table Data</h2>")
            for table in tables:
                html.append("<table>")
                if table.headers:
                    html.append("<tr>")
                    for header in table.headers:
                        html.append(f"<th>{header}</th>")
                    html.append("</tr>")
                for row in table.rows:
                    html.append("<tr>")
                    for cell in row.cells:
                        html.append(f"<td>{self.format_field(cell.value)}</td>")
                    html.append("</tr>")
                html.append("</table>")
                html.append("<br>")

        html.extend(["</body>", "</html>"])
        return "\n".join(html)
