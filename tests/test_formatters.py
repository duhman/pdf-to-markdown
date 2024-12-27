import pytest
from app.formatters.csv_formatter import CSVFormatter
from app.formatters.html_formatter import HTMLFormatter
from app.formatters.yaml_formatter import YAMLFormatter

@pytest.fixture
def sample_data():
    return {
        'registration': '923930892',
        'invoice_number': 'INV-001',
        'date': '2024-01-26',
        'due_date': '2024-02-26',
        'contact_person': 'John Doe',
        'total': '1234.56',
        'tax': '308.64',
        'bank_account': '15066177553',
        'reference': '2345678903'
    }

@pytest.fixture
def sample_tables():
    return [
        "| Description | Amount | Tax | Total |\n|-------------|--------|-----|--------|\n| Item 1 | 1000,00 | 250,00 | 1250,00 |"
    ]

def test_csv_formatter(sample_data, sample_tables):
    """Test CSV formatter output."""
    formatter = CSVFormatter()
    output = formatter.format(sample_data, sample_tables)
    
    # Check format
    assert isinstance(output, str)
    assert output.count('\n') > 5  # Multiple lines
    
    # Check content
    assert 'Field,Value' in output
    assert 'Company Registration,NO 923 930 892 MVA' in output
    assert 'Invoice Number,INV-001' in output
    assert 'Total Amount,"1 234,56 kr"' in output
    assert 'Line Items' in output

def test_html_formatter(sample_data, sample_tables):
    """Test HTML formatter output."""
    formatter = HTMLFormatter()
    output = formatter.format(sample_data, sample_tables)
    
    # Check format
    assert isinstance(output, str)
    assert output.startswith('<!DOCTYPE html>')
    assert output.endswith('</html>')
    
    # Check content
    assert '<title>' in output
    assert '<style>' in output
    assert 'Invoice Details' in output
    assert 'NO 923 930 892 MVA' in output
    assert 'INV-001' in output
    assert '1 234,56 kr' in output
    assert '<table>' in output
    assert '</table>' in output

def test_yaml_formatter(sample_data, sample_tables):
    """Test YAML formatter output."""
    formatter = YAMLFormatter()
    output = formatter.format(sample_data, sample_tables)
    
    # Check format
    assert isinstance(output, str)
    assert 'invoice_details:' in output
    
    # Check content
    assert 'company_registration: NO 923 930 892 MVA' in output
    assert 'invoice_number: INV-001' in output
    assert 'total_amount: 1 234,56 kr' in output
    assert 'line_items:' in output

def test_empty_data_handling():
    """Test formatters with empty data."""
    empty_data = {}
    empty_tables = []
    
    # Test CSV formatter
    csv_formatter = CSVFormatter()
    csv_output = csv_formatter.format(empty_data, empty_tables)
    assert isinstance(csv_output, str)
    assert 'Field,Value' in csv_output
    
    # Test HTML formatter
    html_formatter = HTMLFormatter()
    html_output = html_formatter.format(empty_data, empty_tables)
    assert isinstance(html_output, str)
    assert '<!DOCTYPE html>' in html_output
    
    # Test YAML formatter
    yaml_formatter = YAMLFormatter()
    yaml_output = yaml_formatter.format(empty_data, empty_tables)
    assert isinstance(yaml_output, str)
    assert 'invoice_details:' in yaml_output

def test_special_character_handling(sample_data):
    """Test handling of special characters."""
    sample_data['contact_person'] = 'Øystein Åsen'
    
    # Test CSV formatter
    csv_formatter = CSVFormatter()
    csv_output = csv_formatter.format(sample_data, None)
    assert 'Øystein Åsen' in csv_output
    
    # Test HTML formatter
    html_formatter = HTMLFormatter()
    html_output = html_formatter.format(sample_data, None)
    assert 'Øystein Åsen' in html_output
    
    # Test YAML formatter
    yaml_formatter = YAMLFormatter()
    yaml_output = yaml_formatter.format(sample_data, None)
    assert 'Øystein Åsen' in yaml_output
