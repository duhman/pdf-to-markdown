import re
from typing import Optional
from decimal import Decimal

class NorwegianValidator:
    def __init__(self):
        self.postal_codes = self._load_postal_codes()
        
    def _load_postal_codes(self) -> set:
        # In a real implementation, load from a file or database
        return {'0180', '1407', '0247'}  # Example postal codes

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
    def _mod10_checksum(number: str) -> int:
        """Calculate MOD10 checksum for a number."""
        weights = [2, 1] * (len(number) // 2 + 1)  # Alternate weights
        total = 0
        for i, digit in enumerate(number):
            product = int(digit) * weights[i]
            # If product is two digits, add them together
            total += sum(int(d) for d in str(product))
        check_digit = (10 - (total % 10)) % 10
        return check_digit

    @staticmethod
    def _mod11_checksum(number: str, weights: list) -> int:
        """Calculate MOD11 checksum for a number using given weights."""
        if len(weights) < len(number):
            weights = weights[-len(number):]
        total = sum(int(d) * w for d, w in zip(number, weights))
        remainder = total % 11
        if remainder == 0:
            return 0
        elif remainder == 1:
            return -1  # Invalid
        return 11 - remainder

    @staticmethod
    def validate_kid(kid: str) -> bool:
        """Validate Norwegian KID number using MOD10 or MOD11 algorithm."""
        if not kid or not kid.isdigit():
            return False

        # Remove any whitespace and get length
        kid = kid.strip()
        if len(kid) < 4 or len(kid) > 25:
            return False

        # Try MOD10
        expected_checksum = int(kid[-1])
        number = kid[:-1]
        checksum = NorwegianValidator._mod10_checksum(number)
        if checksum == expected_checksum:
            return True

        # Try MOD11
        weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        checksum = NorwegianValidator._mod11_checksum(number, weights)
        return checksum != -1 and checksum == expected_checksum

    @staticmethod
    def validate_personal_number(number: str) -> bool:
        """Validate Norwegian personal number (fødselsnummer)."""
        if not number or not number.isdigit() or len(number) != 11:
            return False

        # Extract components
        day = int(number[0:2])
        month = int(number[2:4])
        year = int(number[4:6])
        individual = int(number[6:9])

        # Validate date components
        if day < 1 or day > 31 or month < 1 or month > 12:
            return False

        # Adjust individual number ranges for birth century
        if individual < 500:  # Born 1900-1999
            year += 1900
        elif individual < 750:  # Born 2000-2039
            year += 2000
        elif individual < 1000:  # Born 1854-1899
            year += 1800

        # Validate control digits using MOD11
        weights1 = [3, 7, 6, 1, 8, 9, 4, 5, 2]
        weights2 = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

        # First control digit
        checksum1 = NorwegianValidator._mod11_checksum(number[:9], weights1)
        if checksum1 == -1 or checksum1 != int(number[9]):
            return False

        # Second control digit
        checksum2 = NorwegianValidator._mod11_checksum(number[:10], weights2)
        if checksum2 == -1 or checksum2 != int(number[10]):
            return False

        return True

    def validate_address(self, postal_code: str, city: str) -> bool:
        """Validate Norwegian postal address."""
        if not postal_code.isdigit() or len(postal_code) != 4:
            return False
        return postal_code in self.postal_codes

    def validate_account_number(self, account: str) -> bool:
        """Validate Norwegian bank account number."""
        # Remove spaces and dots
        cleaned = ''.join(c for c in account if c.isdigit())
        if len(cleaned) != 11:
            return False
            
        # Calculate control digit using MOD11
        weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        sum_product = sum(int(d) * w for d, w in zip(cleaned[:-1], weights))
        control = (11 - (sum_product % 11)) % 11
        if control == 10:
            return False
        return control == int(cleaned[-1])

    @staticmethod
    def validate_vat_number(vat: str) -> bool:
        """Validate Norwegian VAT number."""
        # VAT number is org number + 'MVA'
        cleaned = vat.upper().replace('NO', '').replace('MVA', '').strip()
        return NorwegianValidator.validate_org_number(cleaned)

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
        # Remove all non-digit characters
        cleaned = re.sub(r'[^0-9]', '', phone)
        
        # Handle numbers with country code
        if cleaned.startswith('47') and len(cleaned) == 10:
            cleaned = cleaned[2:]
        elif cleaned.startswith('0047') and len(cleaned) == 12:
            cleaned = cleaned[4:]
            
        # Format 8-digit number
        if len(cleaned) == 8:
            return f"+47 {cleaned[:2]} {cleaned[2:4]} {cleaned[4:6]} {cleaned[6:]}"
            
        return phone

    def format_address(self, street: str, postal_code: str, city: str) -> str:
        """Format Norwegian address."""
        if self.validate_address(postal_code, city):
            return f"{street}\n{postal_code} {city}"
        return f"{street}\n{postal_code} {city} (Invalid postal code)"

    def format_account_number(self, account: str) -> str:
        """Format Norwegian bank account number."""
        cleaned = ''.join(c for c in account if c.isdigit())
        if len(cleaned) == 11:
            return f"{cleaned[:4]}.{cleaned[4:6]}.{cleaned[6:]}"
        return account

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
            elif field_type == 'address':
                parts = value.split('\n')
                if len(parts) == 3:
                    return self.norwegian.format_address(parts[0], parts[1], parts[2])
                return value
            elif field_type == 'account_number':
                return self.norwegian.format_account_number(value)
        
        return value

    def validate_field(self, field_type: str, value: str, language: str = 'no') -> bool:
        """Validate a field based on its type and language."""
        if language == 'no':
            if field_type == 'org_number':
                return self.norwegian.validate_org_number(value)
            elif field_type == 'kid':
                return self.norwegian.validate_kid(value)
            elif field_type == 'address':
                parts = value.split('\n')
                if len(parts) == 3:
                    return self.norwegian.validate_address(parts[1], parts[2])
                return False
            elif field_type == 'account_number':
                return self.norwegian.validate_account_number(value)
            elif field_type == 'personal_number':
                return self.norwegian.validate_personal_number(value)
            elif field_type == 'vat_number':
                return self.norwegian.validate_vat_number(value)
        
        return True
