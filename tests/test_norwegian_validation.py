import pytest

from app.validators import NorwegianValidator


@pytest.fixture
def validator():
    return NorwegianValidator()


def test_org_number_validation(validator):
    """Test organization number validation."""
    assert validator.validate_org_number("923930892")  # Valid
    assert not validator.validate_org_number("123456789")  # Invalid
    assert not validator.validate_org_number("92393089")  # Too short
    assert not validator.validate_org_number("9239308921")  # Too long


def test_account_number_validation(validator):
    """Test bank account number validation."""
    assert validator.validate_account_number("1506.61.77553")  # Valid
    assert validator.validate_account_number("15066177553")  # Valid without dots
    assert not validator.validate_account_number("1506617755")  # Too short
    assert not validator.validate_account_number("15066177552")  # Invalid checksum


def test_personal_number_validation(validator):
    """Test personal number (fødselsnummer) validation."""
    assert validator.validate_personal_number(
        "29029600013"
    )  # Valid (29th Feb 1996, Individual number 001, Control digits 1,3)
    assert not validator.validate_personal_number("29029600012")  # Invalid checksum
    assert not validator.validate_personal_number("32029600013")  # Invalid date
    assert not validator.validate_personal_number("2902960001")  # Too short


def test_vat_number_validation(validator):
    """Test VAT number validation."""
    assert validator.validate_vat_number("NO 923 930 892 MVA")  # Valid with prefix and suffix
    assert validator.validate_vat_number("923930892MVA")  # Valid without spaces
    assert not validator.validate_vat_number("NO123456789MVA")  # Invalid number
    assert not validator.validate_vat_number("92393089")  # Too short


def test_address_validation(validator):
    """Test address validation."""
    assert validator.validate_address("0180", "Oslo")  # Valid
    assert validator.validate_address("1407", "Oslo")  # Valid
    assert not validator.validate_address("0000", "Oslo")  # Invalid postal code
    assert not validator.validate_address("123", "Oslo")  # Too short


def test_currency_formatting(validator):
    """Test currency amount formatting."""
    assert validator.format_currency("1234.56") == "1 234,56 kr"
    assert validator.format_currency("1234") == "1 234,00 kr"
    assert validator.format_currency("1234.5") == "1 234,50 kr"
    assert validator.format_currency("1234.567") == "1 234,57 kr"  # Rounds to 2 decimals


def test_phone_formatting(validator):
    """Test phone number formatting."""
    assert validator.format_phone("12345678") == "+47 12 34 56 78"
    assert validator.format_phone("+4712345678") == "+47 12 34 56 78"
    assert validator.format_phone("004712345678") == "+47 12 34 56 78"
    assert validator.format_phone("12345") == "12345"  # Too short, returns unchanged


def test_account_number_formatting(validator):
    """Test bank account number formatting."""
    assert validator.format_account_number("15066177553") == "1506.61.77553"
    assert validator.format_account_number("1506.61.77553") == "1506.61.77553"
    assert (
        validator.format_account_number("150661775") == "150661775"
    )  # Too short, returns unchanged


def test_address_formatting(validator):
    """Test address formatting."""
    address = "Storgata 1\n0180\nOslo"
    expected = "Storgata 1\n0180 Oslo"
    assert validator.format_address("Storgata 1", "0180", "Oslo") == expected

    # Invalid postal code
    invalid_address = validator.format_address("Storgata 1", "0000", "Oslo")
    assert "Invalid postal code" in invalid_address