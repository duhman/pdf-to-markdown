"""YAML formatter implementation."""

from typing import Any, Dict

import yaml

from ..formatters import BaseFormatter


class YAMLFormatter(BaseFormatter):
    """Format data as YAML."""

    def format_output(self, data: Dict[str, Any], tables: list = None) -> str:
        """Format the data into YAML format."""
        formatted_data = {
            "invoice_details": {
                "company_registration": self.data_formatter.format_field(
                    "org_number", data.get("registration", "")
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
                    "reference": self.data_formatter.format_field("kid", data.get("reference", "")),
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

        return yaml.dump(formatted_data, allow_unicode=True, sort_keys=False)
