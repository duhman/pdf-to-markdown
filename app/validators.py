import re
from typing import Optional
from decimal import Decimal

class NorwegianValidator:
    @staticmethod
    def validate_org_number(org_number: str) -> bool:
        """Validate Norwegian organization number (9 digits)."""
        # Remove 'NO' prefix and spaces
        cleaned = re.sub(r'[^0-9]', '', org_number)
        if len(cleaned) != 9:
            return False
        
        # Validate using weights and modulus 11
        weights = [3, 2, 7, 6, 5, 4, 3, 2]
        digits = [int(d) for d in cleaned[:-1]]
        control = int(cleaned[-1])
        
        sum_product = sum(w * d for w, d in zip(weights, digits))
        remainder = sum_product % 11
        calculated_control = 11 - remainder if remainder != 0 else 0
        
        return calculated_control == control

    @staticmethod
    def format_org_number(org_number: str) -> str:
        """Format Norwegian organization number."""
        cleaned = re.sub(r'[^0-9]', '', org_number)
        if len(cleaned) == 9:
            return f"NO {cleaned[:3]} {cleaned[3:6]} {cleaned[6:]} MVA"
        return org_number

    @staticmethod
    def validate_kid(kid: str) -> bool:
        """Validate Norwegian KID number using MOD10 or MOD11."""
        cleaned = re.sub(r'[^0-9]', '', kid)
        if not cleaned:
            return False
            
        # Try MOD10 (Luhn algorithm) first
        digits = [int(d) for d in cleaned]
        checksum = sum((d if i % 2 else d * 2 - 9 if d * 2 > 9 else d * 2) 
                      for i, d in enumerate(reversed(digits[:-1])))
        if (checksum + digits[-1]) % 10 == 0:
            return True
            
        # Try MOD11 if MOD10 fails
        weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2][-len(cleaned):]
        sum_product = sum(w * int(d) for w, d in zip(weights, cleaned[:-1]))
        control = (11 - (sum_product % 11)) % 11
        return control == int(cleaned[-1])

    @staticmethod
    def format_currency(amount: str) -> str:
        """Format currency amount in Norwegian style."""
        try:
            # Convert to decimal for precise handling
            cleaned = re.sub(r'[^0-9,.-]', '', amount.replace(' ', ''))
            cleaned = cleaned.replace(',', '.')
            decimal_amount = Decimal(cleaned)
            
            # Format with Norwegian conventions
            whole, decimal = f"{decimal_amount:.2f}".split('.')
            whole = ' '.join(re.findall(r'\d{1,3}(?=(?:\d{3})*$)', whole))
            return f"{whole},{decimal} kr"
        except:
            return amount

    @staticmethod
    def format_phone(phone: str) -> str:
        """Format Norwegian phone number."""
        cleaned = re.sub(r'[^0-9+]', '', phone)
        if len(cleaned) == 8:  # Norwegian domestic number
            return f"{cleaned[:2]} {cleaned[2:4]} {cleaned[4:6]} {cleaned[6:]}"
        elif len(cleaned) == 11 and cleaned.startswith('+47'):
            local = cleaned[3:]
            return f"+47 {local[:2]} {local[2:4]} {local[4:6]} {local[6:]}"
        return phone

class DataFormatter:
    def __init__(self):
        self.norwegian = NorwegianValidator()
    
    def format_field(self, field_type: str, value: str, language: str = 'no') -> str:
        """Format a field based on its type and language."""
        if not value:
            return value
            
        if language == 'no':
            if field_type == 'org_number':
                return self.norwegian.format_org_number(value)
            elif field_type == 'currency':
                return self.norwegian.format_currency(value)
            elif field_type == 'phone':
                return self.norwegian.format_phone(value)
            elif field_type == 'kid':
                return value if self.norwegian.validate_kid(value) else f"Invalid KID: {value}"
        
        return value

    def validate_field(self, field_type: str, value: str, language: str = 'no') -> bool:
        """Validate a field based on its type and language."""
        if language == 'no':
            if field_type == 'org_number':
                return self.norwegian.validate_org_number(value)
            elif field_type == 'kid':
                return self.norwegian.validate_kid(value)
        
        return True
