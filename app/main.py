"""Main FastAPI application."""

import logging
from typing import Dict  # type: ignore

import uvicorn  # type: ignore
from fastapi import BackgroundTasks, FastAPI, File, UploadFile  # type: ignore
from fastapi.exceptions import HTTPException  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from app.markdown_generator import MarkdownGenerator
from app.pdf_processor import PDFProcessor

# Create a logger
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF to Markdown Converter")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a background tasks object
background_tasks = BackgroundTasks()


@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)) -> Dict[str, str]:
    """Convert a PDF file to markdown."""
    try:
        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")

        # Process PDF
        processor = PDFProcessor()
        text = await processor.process_pdf(content)

        # Generate markdown
        generator = MarkdownGenerator()
        language = processor.detect_language(text)
        markdown = generator.generate_markdown(text, language)

        return {"markdown": markdown, "language": language}

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
