import azure.functions as func
import logging
import json
from io import BytesIO

# Add the project root to Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import validate_config
from app.logging import setup_logging
from src.pdf_processor import PDFProcessor
from src.rag_engine import RAGEngine

# Initialize components
setup_logging()
logger = logging.getLogger('app')
pdf_processor = PDFProcessor()
rag_engine = RAGEngine()

def process_pdf(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get the PDF file from the request
        pdf_file = req.files['file']
        pdf_bytes = pdf_file.read()
        
        # Process the PDF
        pdf_processor.process(BytesIO(pdf_bytes))
        
        return func.HttpResponse(
            json.dumps({"message": "PDF processed successfully"}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

def query(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get the query from request body
        req_body = req.get_json()
        user_query = req_body.get('query')
        
        if not user_query:
            return func.HttpResponse(
                json.dumps({"error": "No query provided"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Process query through RAG engine
        answer = rag_engine.process_query(user_query)
        
        return func.HttpResponse(
            json.dumps({"answer": answer}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
