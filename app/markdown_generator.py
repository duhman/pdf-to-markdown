import re
from typing import Dict, List

class MarkdownGenerator:
    def __init__(self):
        self.invoice_keywords = {
            'en': {
                'invoice': ['invoice', 'bill'],
                'date': ['date', 'invoice date'],
                'due_date': ['due date', 'payment due'],
                'total': ['total', 'amount due', 'total amount'],
                'tax': ['tax', 'vat', 'gst'],
                'invoice_number': ['invoice number', 'invoice #', 'invoice no']
            },
            'no': {
                'invoice': ['faktura', 'regning'],
                'date': ['dato', 'fakturadato'],
                'due_date': ['forfallsdato', 'betalingsfrist'],
                'total': ['total', 'å betale', 'sum'],
                'tax': ['mva', 'merverdiavgift'],
                'invoice_number': ['fakturanummer', 'faktura nr']
            }
        }

    def generate_markdown(self, text: str, language: str) -> str:
        # Split text into lines and remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Initialize markdown content
        markdown_content = []
        
        # Add title
        markdown_content.append('# Invoice Details\n')
        
        # Process text and identify important sections
        keywords = self.invoice_keywords[language]
        
        # Extract and format important information
        for key, terms in keywords.items():
            for line in lines:
                for term in terms:
                    if term.lower() in line.lower():
                        # Format the line as a markdown heading and content
                        heading = key.replace('_', ' ').title()
                        content = line.replace(term, '').strip()
                        markdown_content.append(f'## {heading}')
                        markdown_content.append(content + '\n')
                        break
        
        # Add remaining content in a structured format
        markdown_content.append('## Additional Details\n')
        markdown_content.append('```')
        for line in lines:
            # Skip lines that were already processed
            already_processed = False
            for terms in keywords.values():
                for term in terms:
                    if term.lower() in line.lower():
                        already_processed = True
                        break
                if already_processed:
                    break
            if not already_processed:
                markdown_content.append(line)
        markdown_content.append('```\n')
        
        return '\n'.join(markdown_content)
