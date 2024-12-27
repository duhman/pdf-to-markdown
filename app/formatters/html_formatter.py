from typing import Any, Dict, List

from jinja2 import Template

from ..validators import DataFormatter


class HTMLFormatter:
    def __init__(self):
        self.data_formatter = DataFormatter()

    def format(self, data: dict, tables: List[str] = None) -> str:
        """Format data into HTML."""
        template = Template(
            """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Invoice Details</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; margin-top: 20px; }
        .section { margin: 20px 0; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f8f9fa; }
        .amount { text-align: right; }
    </style>
</head>
<body>
    <h1>Invoice Details</h1>
    
    {% if data.invoice_number or data.date or data.due_date %}
    <div class="section">
        <h2>Basic Information</h2>
        <table>
            {% if data.invoice_number %}<tr><th>Invoice Number</th><td>{{ data.invoice_number }}</td></tr>{% endif %}
            {% if data.date %}<tr><th>Date</th><td>{{ data.date }}</td></tr>{% endif %}
            {% if data.due_date %}<tr><th>Due Date</th><td>{{ data.due_date }}</td></tr>{% endif %}
        </table>
    </div>
    {% endif %}

    {% if data.contact_person %}
    <div class="section">
        <h2>Contact Information</h2>
        <p>{{ data.contact_person }}</p>
    </div>
    {% endif %}

    {% if data.total or data.tax %}
    <div class="section">
        <h2>Financial Information</h2>
        <table>
            {% if data.total %}
            <tr>
                <th>Total Amount</th>
                <td class="amount">{{ data.total }}</td>
            </tr>
            {% endif %}
            {% if data.tax %}
            <tr>
                <th>Tax</th>
                <td class="amount">{{ data.tax }}</td>
            </tr>
            {% endif %}
        </table>
    </div>
    {% endif %}

    {% if data.bank_account or data.reference %}
    <div class="section">
        <h2>Payment Information</h2>
        <table>
            {% if data.bank_account %}
            <tr>
                <th>Bank Account</th>
                <td>{{ data.bank_account }}</td>
            </tr>
            {% endif %}
            {% if data.reference %}
            <tr>
                <th>Reference</th>
                <td>{{ data.reference }}</td>
            </tr>
            {% endif %}
        </table>
    </div>
    {% endif %}

    {% if tables %}
    <div class="section">
        <h2>Line Items</h2>
        {% for table in tables %}
        <div class="table-container">
            {{ table|safe }}
        </div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
"""
        )

        return template.render(data=data, tables=tables)

    def _convert_markdown_table_to_html(self, table: str) -> str:
        html_table = table.replace("|", "</td><td>")
        html_table = html_table.replace("\n", "</tr>\n<tr><td>")
        html_table = f"<table><tr><td>{html_table}</tr></table>"
        return html_table
