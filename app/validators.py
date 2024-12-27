"""Validation functions for invoice data."""

import re
from decimal import Decimal, InvalidOperation
from typing import Optional


def validate_norwegian_org_number(org_number: str) -> bool:
    """Validate Norwegian organization number.

    Args:
        org_number: The organization number to validate

    Returns:
        True if valid, False otherwise
    """
    if not org_number.isdigit() or len(org_number) != 9:
        return False

    weights = [3, 2, 7, 6, 5, 4, 3, 2]
    digits = [int(d) for d in org_number[:-1]]

    total = sum(w * d for w, d in zip(weights, digits))
    check_digit = (11 - (total % 11)) % 11
    if check_digit == 10:
        return False

    return check_digit == int(org_number[-1])


def validate_norwegian_account_number(account_number: str) -> bool:
    """Validate Norwegian bank account number.

    Args:
        account_number: The account number to validate

    Returns:
        True if valid, False otherwise
    """
    if not account_number.isdigit() or len(account_number) != 11:
        return False

    weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    digits = [int(d) for d in account_number[:-1]]

    total = sum(w * d for w, d in zip(weights, digits))
    check_digit = (11 - (total % 11)) % 11
    if check_digit == 10:
        return False

    return check_digit == int(account_number[-1])


def validate_amount(amount: str) -> Optional[Decimal]:
    """Validate and parse amount string.

    Args:
        amount: The amount string to validate

    Returns:
        Decimal amount if valid, None otherwise
    """
    # Remove whitespace and currency symbols
    amount = amount.strip().replace(" ", "").replace("kr", "").replace("NOK", "")

    # Replace comma with dot for decimal point
    amount = amount.replace(",", ".")

    try:
        decimal_amount = Decimal(amount)
        if decimal_amount < 0:
            return None
        return decimal_amount
    except (ValueError, InvalidOperation):
        return None


def validate_vat_number(vat_number: str) -> bool:
    """Validate Norwegian VAT number.

    Args:
        vat_number: The VAT number to validate

    Returns:
        True if valid, False otherwise
    """
    # Remove 'MVA' suffix if present
    vat_number = vat_number.upper().replace("MVA", "").strip()

    # Should be 9 digits
    if not vat_number.isdigit() or len(vat_number) != 9:
        return False

    return validate_norwegian_org_number(vat_number)


def validate_norwegian_phone(phone: str) -> bool:
    """Validate Norwegian phone number.

    Args:
        phone: The phone number to validate

    Returns:
        True if valid, False otherwise
    """
    # Remove spaces and special characters
    phone = re.sub(r"[\s\-\+\(\)]", "", phone)

    # Check if starts with country code
    if phone.startswith("47"):
        phone = phone[2:]
    elif phone.startswith("00"):
        phone = phone[4:]  # Remove '0047'
    elif phone.startswith("+"):
        phone = phone[3:]  # Remove '+47'

    # Should be 8 digits
    return phone.isdigit() and len(phone) == 8


def validate_norwegian_postal_code(postal_code: str) -> bool:
    """Validate Norwegian postal code.

    Args:
        postal_code: The postal code to validate

    Returns:
        True if valid, False otherwise
    """
    return postal_code.isdigit() and len(postal_code) == 4


def validate_norwegian_date(date_str: str) -> bool:
    """Validate Norwegian date format (DD.MM.YYYY).

    Args:
        date_str: The date string to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r"^\d{2}\.\d{2}\.\d{4}$"
    if not re.match(pattern, date_str):
        return False

    try:
        day, month, year = map(int, date_str.split("."))
        if not (1 <= month <= 12 and 1 <= day <= 31):
            return False
        if month in [4, 6, 9, 11] and day > 30:
            return False
        if month == 2:
            leap_year = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
            if day > 29 or (not leap_year and day > 28):
                return False
        return True
    except ValueError:
        return False


def setup_validators() -> None:
    """Initialize any required validator settings."""
    # Currently no initialization needed
    pass
