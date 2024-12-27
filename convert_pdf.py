#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import asyncio
from app.pdf_processor import PDFProcessor
from app.ocr_processor import OCRProcessor
from app.html_formatter import HTMLFormatter
from app.markdown_converter import MarkdownConverter

async def convert_pdf_to_markdown(pdf_path: str, output_dir: str) -> None:
    """
    Convert a PDF file to markdown format.
    
    Args:
        pdf_path: Path to the input PDF file
        output_dir: Directory where the markdown file will be saved
    """
    # Initialize processors
    pdf_processor = PDFProcessor()
    ocr_processor = OCRProcessor()
    html_formatter = HTMLFormatter()
    markdown_converter = MarkdownConverter()
    
    try:
        # Extract text and images from PDF
        pdf_content = await pdf_processor.process(pdf_path)
        
        # Process with OCR if needed
        ocr_result = await ocr_processor.process(pdf_content)
        
        # Format as HTML
        html_content = await html_formatter.format(ocr_result)
        
        # Convert to markdown
        markdown_content = await markdown_converter.convert(html_content)
        
        # Create output filename
        pdf_filename = Path(pdf_path).stem
        output_path = os.path.join(output_dir, f"{pdf_filename}.md")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        print(f"Successfully converted {pdf_path} to {output_path}")
        
    except Exception as e:
        print(f"Error converting {pdf_path}: {str(e)}")

async def process_directory(input_dir: str, output_dir: str) -> None:
    """
    Process all PDF files in the input directory.
    
    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory where markdown files will be saved
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all PDF files in the input directory
    for file in os.listdir(input_dir):
        if file.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, file)
            await convert_pdf_to_markdown(pdf_path, output_dir)

async def main():
    # Define directories relative to the script location
    base_dir = Path(__file__).parent
    input_dir = base_dir / 'input_pdfs'
    output_dir = base_dir / 'output_markdown'
    
    if not input_dir.exists():
        print(f"Creating input directory: {input_dir}")
        input_dir.mkdir(exist_ok=True)
    
    if not output_dir.exists():
        print(f"Creating output directory: {output_dir}")
        output_dir.mkdir(exist_ok=True)
    
    print(f"Watching directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print("Place PDF files in the input_pdfs directory to convert them to markdown.")
    
    await process_directory(str(input_dir), str(output_dir))

if __name__ == "__main__":
    asyncio.run(main())
