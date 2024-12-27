import pytest
from app.markdown_generator import MarkdownGenerator


def test_norwegian_invoice_extraction():
    """Test extraction of fields from a Norwegian invoice."""
    generator = MarkdownGenerator()

    test_text = """
    Meltek AS
    Ekebergveien 9, 1407 Vinterbro, Norge
    Telefon: 94898926
    Mobil: 40184401
    E-postadresse: post@meltek.no
    Foretaksregisteret: NO 923 930 892 MVA
    Nettside: Meltek.no

    FAKTURA
    Fakturanr.: 1122
    Fakturadato: 2024-11-19
    Kundenr.: 10274

    Betalingsinformasjon
    Forfallsdato: 2024-12-19
    Kontonummer: 1506.61.77553
    KID: 0112219

    Prosjekt: 2905 Elaway AS - ettermontering vallerveien
    Vår kontakt: Tim Robin Frick
    Leveransedato: 2024-11-19
    Leveranseadresse: Pilestredet 12
    
    Kontraktsum ekskl. mva 5 000,00
    
    Timer            5 000,00    1 250,00    6 250,00
    """

    markdown = generator.generate_markdown(test_text, "no")

    # Check company information
    assert "NO 923 930 892 MVA" in markdown

    # Check basic invoice information
    assert "1122" in markdown
    assert "2024-11-19" in markdown
    assert "2024-12-19" in markdown

    # Check project information
    assert "2905 Elaway AS - ettermontering vallerveien" in markdown

    # Check contact information
    assert "Tim Robin Frick" in markdown

    # Check delivery information
    assert "Pilestredet 12" in markdown
    assert "2024-11-19" in markdown

    # Check financial information
    assert "5 000,00" in markdown
    assert "1 250,00" in markdown
    assert "6 250,00" in markdown

    # Check payment information
    assert "1506.61.77553" in markdown
    assert "0112219" in markdown


def test_norwegian_invoice_formatting():
    """Test the formatting of the markdown output."""
    generator = MarkdownGenerator()

    test_text = """
    Fakturanr.: 1122
    KID: 0112219
    Kontraktsum ekskl. mva 5 000,00
    """

    markdown = generator.generate_markdown(test_text, "no")

    # Check markdown structure
    assert "# Invoice Details" in markdown
    assert "## Invoice Number" in markdown
    assert "## Payment Information" in markdown
    assert "## Contract Amount" in markdown


def test_norwegian_amount_formats():
    """Test handling of Norwegian amount formats."""
    generator = MarkdownGenerator()

    test_text = """
    Sum: 1 234,56 kr
    MVA: 308,64 kr
    """

    markdown = generator.generate_markdown(test_text, "no")

    assert "1 234,56 kr" in markdown
    assert "308,64 kr" in markdown
