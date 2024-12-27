# PDF to Markdown Converter

A Python tool for converting PDF invoices to well-formatted Markdown files. The tool uses OCR when needed and preserves the structure and formatting of the original invoice.

## Features

- Converts PDF invoices to clean, well-formatted Markdown
- Extracts and preserves all important invoice information:
  - Company details
  - Customer information
  - Invoice details
  - Project information
  - Line items with pricing
  - Payment details
- Uses OCR (Optical Character Recognition) when needed
- Supports both English and Norwegian invoices
- Follows markdown best practices and linting rules
- Handles both text-based and image-based PDFs

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf-to-markdown.git
cd pdf-to-markdown
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your PDF invoices in the `input_pdfs` directory.
2. Run the conversion script:
```bash
python convert_pdf.py
```
3. Find the converted markdown files in the `output_markdown` directory.

## Output Format

The converted markdown files follow a consistent structure:

```markdown
# Company Name

## Company Details
* Address: ...
* Phone: ...
* Email: ...
* Organization Number: ...
* Website: ...

## Customer Details
* Company: ...
* Address: ...
* Postal Code: ...

## Invoice Details
* Invoice Number: ...
* Invoice Date: ...
* Due Date: ...
* Customer Number: ...
* Reference: ...

## Project Details
* Project: ...
* Contact: ...
* Delivery Date: ...
* Delivery Address: ...

## Line Items
| Description | Amount (excl. VAT) | VAT (25%) | Amount (incl. VAT) |
|------------|-------------------|-----------|------------------|
| Item 1     | 1000,00          | 250,00    | 1250,00         |

## Total
Total Amount: NOK 1250,00

## Payment Details
* Account Number: ...
* Reference: ...
* Due Date: ...
```

## Dependencies

- `opencv-python`: Image processing
- `pytesseract`: OCR text extraction
- `pdf2image`: PDF to image conversion
- `beautifulsoup4`: HTML parsing
- `fastapi`: API framework (for future web interface)
- `uvicorn`: ASGI server

## Recent Updates

- Added proper URL formatting in markdown output
- Improved markdown formatting to follow best practices
- Fixed issues with markdown linting:
  - Proper URL formatting
  - Consistent heading structure
  - Single trailing newline
- Enhanced invoice data extraction and organization

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
