import re
from typing import Dict, List

class MarkdownGenerator:
    def __init__(self):
        self.invoice_keywords = {
            'en': {
                'invoice_number': ['Invoice #', 'Invoice Number'],
                'date': ['Date', 'Invoice Date'],
                'total': ['Total Amount', 'Amount', 'Sum'],
                'tax': ['VAT', 'Tax'],
                'project': ['Project', 'Project Reference'],
                'delivery_address': ['Delivery Address', 'Ship To'],
                'delivery_date': ['Delivery Date'],
                'contract_amount': ['Contract Amount', 'Contract Sum'],
                'bank_account': ['Bank Account', 'Account Number'],
                'registration': ['Registration No', 'Company Reg'],
                'contact_person': ['Contact', 'Contact Person'],
                'due_date': ['Due Date', 'Payment Due'],
                'reference': ['Reference', 'Ref']
            },
            'no': {
                'invoice_number': ['Fakturanr', 'Fakturanummer'],
                'date': ['Dato', 'Fakturadato'],
                'total': ['Sum', 'Beløp', 'Totalbeløp'],
                'tax': ['MVA', 'Moms'],
                'project': ['Prosjekt'],
                'delivery_address': ['Leveranseadresse', 'Leveringsadresse'],
                'delivery_date': ['Leveransedato'],
                'contract_amount': ['Kontraktsum', 'Kontraktsbeløp'],
                'bank_account': ['Bankkonto', 'Kontonummer'],
                'registration': ['Foretaksregisteret', 'Org.nr'],
                'contact_person': ['Vår kontakt', 'Kontaktperson'],
                'due_date': ['Forfallsdato'],
                'reference': ['KID', 'Referanse']
            }
        }

    def _extract_field(self, text: str, keywords: list[str]) -> str:
        for keyword in keywords:
            lines = text.split('\n')
            for line in lines:
                if keyword in line:
                    return line.split(keyword)[-1].strip().strip(':').strip()
        return ''

    def generate_markdown(self, text: str, language: str) -> str:
        """Generate markdown from extracted text."""
        keywords = self.invoice_keywords[language]
        
        # Extract all fields
        fields = {
            'invoice_number': self._extract_field(text, keywords['invoice_number']),
            'date': self._extract_field(text, keywords['date']),
            'total': self._extract_field(text, keywords['total']),
            'tax': self._extract_field(text, keywords['tax']),
            'project': self._extract_field(text, keywords['project']),
            'delivery_address': self._extract_field(text, keywords['delivery_address']),
            'delivery_date': self._extract_field(text, keywords['delivery_date']),
            'contract_amount': self._extract_field(text, keywords['contract_amount']),
            'bank_account': self._extract_field(text, keywords['bank_account']),
            'registration': self._extract_field(text, keywords['registration']),
            'contact_person': self._extract_field(text, keywords['contact_person']),
            'due_date': self._extract_field(text, keywords['due_date']),
            'reference': self._extract_field(text, keywords['reference'])
        }

        # Generate markdown
        markdown = "# Invoice Details\n\n"
        
        # Company Information
        if fields['registration']:
            markdown += f"## Company Registration\n{fields['registration']}\n\n"
            
        # Basic Invoice Information
        markdown += f"## Invoice Number\n{fields['invoice_number']}\n\n"
        markdown += f"## Date\n{fields['date']}\n\n"
        if fields['due_date']:
            markdown += f"## Due Date\n{fields['due_date']}\n\n"
            
        # Project Information
        if fields['project']:
            markdown += f"## Project Details\n{fields['project']}\n\n"
        
        # Contact Information
        if fields['contact_person']:
            markdown += f"## Contact Person\n{fields['contact_person']}\n\n"
            
        # Delivery Information
        if fields['delivery_address'] or fields['delivery_date']:
            markdown += "## Delivery Information\n"
            if fields['delivery_address']:
                markdown += f"Address: {fields['delivery_address']}\n"
            if fields['delivery_date']:
                markdown += f"Date: {fields['delivery_date']}\n"
            markdown += "\n"
            
        # Financial Information
        if fields['contract_amount']:
            markdown += f"## Contract Amount\n{fields['contract_amount']}\n\n"
        markdown += f"## Total Amount\n{fields['total']}\n\n"
        markdown += f"## Tax\n{fields['tax']}\n\n"
            
        # Payment Information
        markdown += "## Payment Information\n"
        if fields['bank_account']:
            markdown += f"Bank Account: {fields['bank_account']}\n"
        if fields['reference']:
            markdown += f"Reference: {fields['reference']}\n"

        return markdown
