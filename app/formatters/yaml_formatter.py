"""YAML formatter implementation."""

from typing import Any, Dict, List, Optional

import yaml

from app.formatters import BaseFormatter


class YAMLFormatter(BaseFormatter):
    """Format data as YAML."""

    def __init__(self):
        super().__init__()

    def format_output(self, data: Dict[str, Any], tables: Optional[List[Any]] = None) -> str:
        """Format the data into YAML format."""
        output_data: Dict[str, Any] = {
            "invoice_details": {
                "company_registration": data.get("registration", ""),
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
                    "reference": data.get("reference", ""),
                },
            }
        }

        if tables:
            output_data["tables"] = []
            for table in tables:
                table_data = {
                    "headers": table.headers if table.headers else [],
                    "rows": [[cell.value for cell in row.cells] for row in table.rows],
                }
                output_data["tables"].append(table_data)

        return yaml.dump(output_data, allow_unicode=True, sort_keys=False)
