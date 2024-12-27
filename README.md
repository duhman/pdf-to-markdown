# PDF to Markdown Converter

A FastAPI application that converts PDF invoices to structured markdown documents using OCR technology. Supports both Norwegian and English invoices.

## Features

### Core Features

- Convert PDF invoices to structured markdown
- Multi-language support (Norwegian and English)
- Automatic language detection
- RESTful API interface
- Command-line batch conversion tool
- Document type detection (Invoices, Declarations)

### Advanced Features

- Smart field extraction and validation
  - Norwegian organization number (MVA) validation
  - KID number validation
  - Currency formatting
  - Phone number formatting
- Table detection and extraction
- Multiple output formats (Markdown, JSON, XML)
- Enhanced OCR processing
  - Multiple preprocessing methods
  - Layout detection
  - OCR error correction
  - Table structure recognition

## Installation

1. Clone the repository:

```bash
git clone https://github.com/duhman/pdf-to-markdown.git
cd pdf-to-markdown
```

2. Install system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-nor poppler-utils imagemagick

# macOS
brew install tesseract tesseract-lang poppler imagemagick
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Using the Web API

1. Start the server:

```bash
uvicorn app.main:app --reload
```

2. Convert a PDF invoice via API:

```bash
curl -X POST "http://localhost:8000/convert" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@invoice.pdf" \
     -F "output_format=markdown"
```

### Using the Command Line Script

1. Place your PDF files in the `input_pdfs` directory
2. Run the conversion script:

```bash
python3 convert_pdf.py
```

The script will automatically:
- Process all PDF files in the `input_pdfs` directory
- Create corresponding markdown files in `output_markdown` directory
- Print status messages for each conversion

Example response:

```json
{
  "markdown": "# Invoice Details\n\n## Company Registration\nNO 923 930 892 MVA\n\n## Invoice Number\n1122\n\n## Date\n2024-11-19\n\n## Due Date\n2024-12-19\n\n## Contact Person\nTim Robin Frick\n\n## Total Amount\n5 000,00 kr\n\n## Tax\n1 250,00 kr\n\n## Payment Information\nBank Account: 1506.61.77553\nReference: 0112219\n\n## Line Items\n| Description | Amount | Tax | Total |\n|-------------|--------|-----|--------|\n| Timer | 5 000,00 | 1 250,00 | 6 250,00 |",
  "detected_language": "no"
}
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test types
pytest tests/unit/  # Unit tests
pytest tests/integration/  # Integration tests
pytest tests/performance/  # Performance tests
pytest tests/property/  # Property-based tests

# Run with coverage
pytest --cov=app --cov-report=xml
```

### Code Quality

```bash
# Format code
black app tests

# Sort imports
isort app tests

# Lint code
flake8 app tests

# Type checking
mypy app tests

# Security checks
bandit -r app
safety scan
```

## Known Issues

- Tesseract OCR accuracy may vary based on PDF quality
- Some complex table layouts might not be detected correctly
- Python 3.13 compatibility issues with some dependencies

## Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests and quality checks
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
