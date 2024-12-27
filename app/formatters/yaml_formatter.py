from typing import Dict, Any, List
import yaml
from ..validators import DataFormatter

class YAMLFormatter:
    def __init__(self):
        self.data_formatter = DataFormatter()
    
    def format(self, data: Dict[str, Any], tables: list = None) -> str:
        formatted_data = {
            'invoice_details': {
                'company_registration': self.data_formatter.format_field('org_number', data.get('registration', '')),
                'invoice_number': data.get('invoice_number', ''),
                'date': data.get('date', ''),
                'due_date': data.get('due_date', ''),
                'contact_person': data.get('contact_person', ''),
                'financial': {
                    'total_amount': self.data_formatter.format_field('currency', data.get('total', '')),
                    'tax': self.data_formatter.format_field('currency', data.get('tax', ''))
                },
                'payment': {
                    'bank_account': self.data_formatter.format_field('account_number', data.get('bank_account', '')),
                    'reference': self.data_formatter.format_field('kid', data.get('reference', ''))
                }
            }
        }
        
        if tables:
            formatted_data['line_items'] = tables
        
        return yaml.dump(formatted_data, allow_unicode=True, sort_keys=False)
