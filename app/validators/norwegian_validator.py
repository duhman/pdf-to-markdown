"""Norwegian validation rules implementation."""


class NorwegianValidator:
    """Validator for Norwegian specific formats and numbers."""

    def validate_organization_number(self, number: str) -> bool:
        """Validate Norwegian organization numbers."""
        if not number or not number.isdigit() or len(number) != 9:
            return False

        weights = [3, 2, 7, 6, 5, 4, 3, 2]
        digits = [int(d) for d in number]

        sum_product = sum(w * d for w, d in zip(weights, digits[:-1]))
        control_digit = (11 - (sum_product % 11)) % 11
        if control_digit == 10:
            return False

        return control_digit == digits[-1]

    def validate_org_number(self, number: str) -> bool:
        """Alias for validate_organization_number."""
        return self.validate_organization_number(number)

    def validate_account_number(self, number: str) -> bool:
        """Validate Norwegian bank account numbers."""
        # Remove dots if present
        number = number.replace(".", "")
        if not number.isdigit() or len(number) != 11:
            return False

        weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        digits = [int(d) for d in number]
        
        sum_product = sum(w * d for w, d in zip(weights, digits[:-1]))
        control_digit = (11 - (sum_product % 11)) % 11
        if control_digit == 10:
            return False
            
        return control_digit == digits[-1]

    def validate_personal_number(self, number: str) -> bool:
        """Validate Norwegian personal numbers (fødselsnummer)."""
        if not number.isdigit() or len(number) != 11:
            return False

        day = int(number[0:2])
        month = int(number[2:4])
        year = int(number[4:6])
        
        # Basic date validation
        if month < 1 or month > 12 or day < 1 or day > 31:
            return False
        if month in [4, 6, 9, 11] and day > 30:
            return False
        if month == 2:
            is_leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
            if (is_leap and day > 29) or (not is_leap and day > 28):
                return False

        # Validate control digits
        weights1 = [3, 7, 6, 1, 8, 9, 4, 5, 2]
        weights2 = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        
        digits = [int(d) for d in number]
        sum1 = sum(w * d for w, d in zip(weights1, digits[:-2]))
        control1 = (11 - (sum1 % 11)) % 11
        if control1 == 10 or control1 != digits[-2]:
            return False
            
        sum2 = sum(w * d for w, d in zip(weights2, digits[:-1]))
        control2 = (11 - (sum2 % 11)) % 11
        if control2 == 10 or control2 != digits[-1]:
            return False
            
        return True

    def validate_vat_number(self, number: str) -> bool:
        """Validate Norwegian VAT numbers."""
        # Remove prefix, suffix and spaces
        number = number.replace("NO", "").replace("MVA", "").replace(" ", "")
        return self.validate_organization_number(number)

    def validate_address(self, postal_code: str, city: str) -> bool:
        """Validate Norwegian postal codes."""
        if not postal_code.isdigit() or len(postal_code) != 4:
            return False
        if postal_code == "0000":
            return False
        # In a real implementation, we would check against a list of valid postal codes
        return True

    def format_currency(self, amount: float | int) -> str:
        """Format currency amounts in Norwegian style."""
        return f"NOK {amount:,.2f}".replace(",", " ").replace(".", ",")

    def format_phone(self, number: str) -> str:
        """Format Norwegian phone numbers."""
        # Remove any non-digits
        digits = "".join(filter(str.isdigit, number))
        if len(digits) == 8:
            return f"{digits[:2]} {digits[2:4]} {digits[4:6]} {digits[6:]}"
        elif len(digits) == 9:  # Mobile numbers
            return f"{digits[:3]} {digits[3:5]} {digits[5:7]} {digits[7:]}"
        return digits

    def format_account_number(self, number: str) -> str:
        """Format Norwegian bank account numbers."""
        digits = "".join(filter(str.isdigit, number))
        if len(digits) == 11:
            return f"{digits[:4]}.{digits[4:6]}.{digits[6:]}"
        return digits

    def format_address(self, street: str, postal_code: str, city: str) -> str:
        """Format Norwegian addresses."""
        if not self.validate_address(postal_code, city):
            return f"{street}\n{postal_code} {city}"
        return f"{street}\n{postal_code} {city}"
