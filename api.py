from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
import os
import re
import json
import requests
import tempfile
from concurrent.futures import ThreadPoolExecutor
from document_processor import (
    get_pdf_hash, get_pdf_info, extract_from_pdf, chunk_text, 
    process_chunks_simple, create_embeddings_for_pdf, save_pdf_data, update_master_index
)
from question_answerer import SimpleQASystem

app = FastAPI(
    title="Document Intelligence API",
    description="API for processing documents and answering questions",
    version="1.0.0"
)

EXPECTED_TOKEN = "9f40f077e610d431226b59eec99652153ccad94769da6779cc01725731999634"

def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split("Bearer ")[-1]
    if token != EXPECTED_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

class DocumentRequest(BaseModel):
    documents: Optional[str] = None  
    questions: List[str]



class DocumentResponse(BaseModel):
    answers: List[str]
    processing_info: Optional[dict] = None
    search_info: Optional[dict] = None

def download_document_from_url(url: str) -> str:
    """Download document from URL and save to temporary file."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Create temp_downloads directory if it doesn't exist
        os.makedirs("temp_downloads", exist_ok=True)
        
        # Determine file extension from URL or content-type
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' in content_type or url.lower().endswith('.pdf'):
            extension = '.pdf'
        elif 'docx' in content_type or url.lower().endswith('.docx'):
            extension = '.docx'
        elif 'email' in content_type or url.lower().endswith('.eml'):
            extension = '.eml'
        else:
            # Default to PDF if we can't determine
            extension = '.pdf'
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=extension, 
            dir="temp_downloads"
        )
        
        # Write content to file
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        
        temp_file.close()
        return temp_file.name
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download document: {str(e)}")

def process_document(file_path: str) -> dict:
    """Process a document and create embeddings."""
    try:
        
        # Check if already processed
        file_hash = get_pdf_hash(file_path)
        file_info = get_pdf_info(file_path)
        
        # Check if already in master index
        master_index_path = "metadata/master_index.json"
        if os.path.exists(master_index_path):
            with open(master_index_path, 'r') as f:
                master_index = json.load(f)
                if file_hash in master_index.get("pdfs", {}):
                    return {
                        "status": "already_processed",
                        "file_hash": file_hash,
                        "filename": file_info['filename']
                    }
        
        # Extract text
        text = extract_from_pdf(file_path)
        if not text:
            raise Exception("Failed to extract text from document")
        
        # Chunk text
        chunks = chunk_text(text)
        if not chunks:
            raise Exception("Failed to chunk text")
        
        # Process chunks with simple metadata extraction
        processed_data = process_chunks_simple(chunks)
        
        # Create embeddings
        index, embeddings, enhanced_metadata = create_embeddings_for_pdf(processed_data, file_hash)
        
        # Save data
        save_pdf_data(file_hash, index, embeddings, enhanced_metadata, file_info, text, chunks)
        
        # Update master index
        update_master_index(file_hash, file_info, len(chunks))
        
        return {
            "status": "processed",
            "file_hash": file_hash,
            "filename": file_info['filename'],
            "chunks_processed": len(chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

def answer_questions_from_document(questions: List[str], document_hash: str = None) -> List[str]:
    """Answer questions using a specific document or search across all documents."""
    try:
        qa_system = SimpleQASystem()
        answers = []
        
        # If document_hash is provided, we'll modify the search to focus on that document
        if document_hash:
            pass # No print statement here
        
        for question in questions:
            answer = qa_system.ask_question(question, document_hash=document_hash)
            answers.append(answer)
        
        return answers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer questions: {str(e)}")

@app.post("/hackrx/run", response_model=DocumentResponse)
async def unified_ask_endpoint(request: DocumentRequest, authorization: str = Depends(verify_token)):
    """
    Unified endpoint for document Q&A.
    
    **Two modes:**
    1. **Document + Questions**: Process a document from URL and answer questions from it only
    2. **Questions Only**: Search across all existing documents in the knowledge base
    
    - **documents**: URL to the document (PDF, DOCX, or email) - OPTIONAL
    - **questions**: List of questions to answer - REQUIRED
    """
    try:
        if request.documents:
            # Mode 1: Process specific document and answer from it
            
            # Download document
            file_path = download_document_from_url(request.documents)
            
            # Process document (this will be done in a thread pool to avoid blocking)
            with ThreadPoolExecutor() as executor:
                processing_future = executor.submit(process_document, file_path)
                processing_result = processing_future.result()
            
            # Get the document hash for focused search
            document_hash = processing_result.get("file_hash")
            
            # Answer questions from this specific document
            answers = answer_questions_from_document(request.questions, document_hash)
            
            # Clean up temporary file
            try:
                os.remove(file_path)
            except:
                pass
            
            return DocumentResponse(
                answers=answers,
                processing_info=processing_result
            )
            
        else:
            # Mode 2: Search across all existing documents
            
            # Check if we have any processed documents
            master_index_path = "metadata/master_index.json"
            if not os.path.exists(master_index_path):
                raise HTTPException(status_code=404, detail="No documents found in database. Please upload and process documents first.")
            
            with open(master_index_path, 'r') as f:
                master_index = json.load(f)
            
            if not master_index.get("pdfs"):
                raise HTTPException(status_code=404, detail="No documents found in database. Please upload and process documents first.")
            
            # Answer questions by searching across all documents
            answers = answer_questions_from_document(request.questions)
            
            return DocumentResponse(
                answers=answers,
                search_info={
                    "status": "searched",
                    "documents_available": len(master_index["pdfs"]),
                    "search_strategy": "cross_document_search"
                }
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}") 