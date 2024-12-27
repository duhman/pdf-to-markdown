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
