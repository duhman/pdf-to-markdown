from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
from app.pdf_processor import PDFProcessor
from app.markdown_generator import MarkdownGenerator

app = FastAPI(title="PDF to Markdown Converter")
pdf_processor = PDFProcessor()
markdown_generator = MarkdownGenerator()

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    try:
        # Process the PDF file
        text_content = await pdf_processor.process_pdf(file)
        
        # Detect language
        language = pdf_processor.detect_language(text_content)
        
        # Generate markdown
        markdown_content = markdown_generator.generate_markdown(text_content, language)
        
        return JSONResponse(content={
            "markdown": markdown_content,
            "detected_language": language
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
