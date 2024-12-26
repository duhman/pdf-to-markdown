# PDF to Markdown Converter

A FastAPI-based application that converts PDF invoices in Norwegian and English into structured markdown documents using OCR technology.

## Features

- PDF to text conversion using OCR (Optical Character Recognition)
- Support for both Norwegian and English invoices
- Automatic language detection
- Structured markdown output with key invoice fields
- RESTful API endpoint for easy integration

## Prerequisites

### System Dependencies

1. Tesseract OCR:

```bash
brew install tesseract
brew install tesseract-lang  # For Norwegian language support
```

1. Poppler (for PDF processing):

```bash
brew install poppler
```

1. ImageMagick (for image processing):

```bash
brew install imagemagick
```

### Python Dependencies

- Python 3.x
- Virtual Environment
- Required packages (installed via requirements.txt):
  - FastAPI
  - Uvicorn
  - Python-Multipart
  - PDF2Image
  - Pytesseract
  - Langdetect
  - Markdown
  - Pydantic
  - Python-Dotenv

## Installation

1. Clone the repository:

```bash
git clone https://github.com/duhman/pdf-to-markdown.git
cd pdf-to-markdown
```

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

1. The API will be available at `http://localhost:8000`

1. To convert a PDF to markdown, send a POST request to `/convert` endpoint with the PDF file:

```bash
curl -X POST -F "file=@your_invoice.pdf" http://localhost:8000/convert
```

## API Endpoints

- `POST /convert`: Convert PDF invoice to markdown
  - Input: PDF file (multipart/form-data)
  - Output: JSON response with markdown content and detected language

Example response:

```json
{
  "markdown": "# Invoice Details\n\n## Invoice Number\nINV-001\n\n## Date\n2024-01-26\n\n## Total Amount\n$100.00\n\n## VAT\n$20.00",
  "detected_language": "en"
}
```

## Project Structure

```plaintext
pdf-to-markdown/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and routes
│   ├── pdf_processor.py     # PDF processing and OCR logic
│   └── markdown_generator.py # Markdown generation logic
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## Known Issues

- Some dependencies may require additional system-level packages
- Python 3.13 compatibility issues with certain packages (e.g., pydantic-core)
- Tesseract OCR accuracy may vary depending on the PDF quality and format

## License

[License information]
