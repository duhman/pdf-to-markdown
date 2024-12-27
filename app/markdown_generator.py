import re
from typing import Dict, List


class MarkdownGenerator:
    def __init__(self):
        self.invoice_keywords = {
            "en": {
                "invoice_number": ["Invoice #", "Invoice Number"],
                "date": ["Date", "Invoice Date"],
                "total": ["Total Amount", "Amount", "Sum"],
                "tax": ["VAT", "Tax"],
                "project": ["Project", "Project Reference"],
                "delivery_address": ["Delivery Address", "Ship To"],
                "delivery_date": ["Delivery Date"],
                "contract_amount": ["Contract Amount", "Contract Sum"],
                "bank_account": ["Bank Account", "Account Number"],
                "registration": ["Registration No", "Company Reg"],
                "contact_person": ["Contact", "Contact Person"],
                "due_date": ["Due Date", "Payment Due"],
                "reference": ["Reference", "Ref"],
            },
            "no": {
                "invoice_number": ["Fakturanr", "Fakturanummer"],
                "date": ["Dato", "Fakturadato"],
                "total": ["Sum", "Beløp", "Totalbeløp"],
                "tax": ["MVA", "Moms"],
                "project": ["Prosjekt"],
                "delivery_address": ["Leveranseadresse", "Leveringsadresse"],
                "delivery_date": ["Leveransedato"],
                "contract_amount": ["Kontraktsum", "Kontraktsbeløp"],
                "bank_account": ["Bankkonto", "Kontonummer"],
                "registration": ["Foretaksregisteret", "Org.nr"],
                "contact_person": ["Vår kontakt", "Kontaktperson"],
                "due_date": ["Forfallsdato"],
                "reference": ["KID", "Referanse"],
            },
        }

    def _extract_field(self, text: str, keywords: list[str]) -> str:
        for keyword in keywords:
            lines = text.split("\n")
            for line in lines:
                if keyword in line:
                    return line.split(keyword)[-1].strip().strip(":").strip()
        return ""

    def generate_markdown(self, text: str, language: str = "en") -> str:
        """Generate markdown from extracted text."""
        sections = []
        sections.append("# Invoice Details\n")

        # Extract invoice number
        invoice_number = self._extract_invoice_number(text, language)
        if invoice_number:
            sections.append("## Invoice Number")
            sections.append(invoice_number + "\n")

        # Extract date
        date = self._extract_date(text, language)
        if date:
            sections.append("## Date")
            sections.append(date + "\n")

        # Extract contact person
        contact = self._extract_contact_person(text, language)
        if contact:
            sections.append("## Contact Person")
            sections.append(contact + "\n")

        # Extract payment information
        payment_info = self._extract_payment_info(text, language)
        if payment_info:
            sections.append("## Payment Information")
            sections.append(payment_info + "\n")

        # Extract total amount
        total = self._extract_total_amount(text, language)
        if total:
            sections.append("## Total Amount")
            sections.append(total + "\n")

        # Extract tax information
        tax = self._extract_tax(text, language)
        if tax:
            sections.append("## Tax")
            sections.append(tax + "\n")

        # Extract delivery information
        delivery = self._extract_delivery_info(text, language)
        if delivery:
            sections.append("## Delivery Information")
            sections.append(delivery + "\n")

        # Extract line items
        line_items = self._extract_line_items(text, language)
        if line_items:
            sections.append("## Line Items")
            sections.append(line_items + "\n")

        return "\n".join(sections)

    def _extract_invoice_number(self, text: str, language: str) -> str:
        patterns = {
            "en": r"Invoice\s*#?:?\s*([A-Za-z0-9-]+)",
            "no": r"Faktura(?:nr|nummer)?\.?:?\s*([A-Za-z0-9-]+)",
        }
        return self._extract_with_pattern(text, patterns.get(language, patterns["en"]))

    def _extract_date(self, text: str, language: str) -> str:
        patterns = {
            "en": r"Date:?\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}\.\d{2}\.\d{4})",
            "no": r"(?:Faktura)?dato:?\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}\.\d{2}\.\d{4})",
        }
        return self._extract_with_pattern(text, patterns.get(language, patterns["en"]))

    def _extract_contact_person(self, text: str, language: str) -> str:
        patterns = {
            "en": r"Contact(?:\s*Person)?:?\s*([A-Za-z\s]+)",
            "no": r"(?:Vår|Deres)\s*kontakt:?\s*([A-Za-z\søæåØÆÅ]+)",
        }
        return self._extract_with_pattern(text, patterns.get(language, patterns["en"]))

    def _extract_payment_info(self, text: str, language: str) -> str:
        patterns = {
            "en": r"(?:Account|Reference|Payment).*?:?\s*([A-Za-z0-9\s\.]+)",
            "no": r"(?:Kontonummer|KID|Betalingsinformasjon).*?:?\s*([A-Za-z0-9\s\.]+)",
        }
        matches = re.finditer(
            patterns.get(language, patterns["en"]), text, re.IGNORECASE | re.MULTILINE
        )
        payment_info = []
        for match in matches:
            if match.group():
                payment_info.append(match.group().strip())
        return "\n".join(payment_info) if payment_info else ""

    def _extract_total_amount(self, text: str, language: str) -> str:
        patterns = {
            "en": r"Total\s*Amount:?\s*([\d\s,.]+(?:\s*[A-Za-z]+)?)",
            "no": r"(?:Sum|Beløp|Kontraktsum).*?:?\s*([\d\s,.]+(?:\s*[A-Za-z]+)?)",
        }
        return self._extract_with_pattern(text, patterns.get(language, patterns["en"]))

    def _extract_tax(self, text: str, language: str) -> str:
        patterns = {
            "en": r"(?:VAT|Tax):?\s*([\d\s,.]+(?:\s*[A-Za-z]+)?)",
            "no": r"(?:MVA|Merverdiavgift):?\s*([\d\s,.]+(?:\s*[A-Za-z]+)?|NO\s*\d{3}\s*\d{3}\s*\d{3}\s*MVA)",
        }
        return self._extract_with_pattern(text, patterns.get(language, patterns["en"]))

    def _extract_delivery_info(self, text: str, language: str) -> str:
        patterns = {
            "en": r"Delivery\s*Address:?\s*([A-Za-z0-9\s,\.]+)",
            "no": r"Leveranse(?:adresse)?:?\s*([A-Za-z0-9\søæåØÆÅ,\.]+)",
        }
        return self._extract_with_pattern(text, patterns.get(language, patterns["en"]))

    def _extract_line_items(self, text: str, language: str) -> str:
        # Extract any tabular data or itemized list
        lines = text.split("\n")
        items = []
        for line in lines:
            if re.search(r"\d+[\s,\.]+\d+", line):  # Line contains numbers that look like amounts
                items.append(line.strip())
        return "\n".join(items) if items else ""

    def _extract_with_pattern(self, text: str, pattern: str) -> str:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else ""
