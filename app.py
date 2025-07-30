

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Add current directory to path to import your modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing modules
from document_processor import DocumentProcessor
from question_answerer import QuestionAnswerer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for hackathon testing

# Initialize your RAG system components
doc_processor = None
qa_system = None

def initialize_rag_system():
    """Initialize RAG system components"""
    global doc_processor, qa_system
    try:
        logger.info("Initializing RAG system...")
        doc_processor = DocumentProcessor()
        qa_system = QuestionAnswerer()
        
        # Check if processed data exists, if not process default doc
        if not os.path.exists('embeddings') or not os.listdir('embeddings'):
            logger.info("No existing embeddings found. Processing default document...")
            if os.path.exists('data/doc1.pdf'):
                doc_processor.process_document('data/doc1.pdf')
            else:
                logger.warning("No doc1.pdf found in data directory")
        
        logger.info("RAG system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {str(e)}")
        return False

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "message": "Bajaj RAG System API",
        "status": "running",
        "endpoints": {
            "webhook": "/webhook",
            "ask": "/ask",
            "health": "/health"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    global qa_system
    return jsonify({
        "status": "healthy" if qa_system else "initializing",
        "rag_system": "ready" if qa_system else "loading"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Main webhook endpoint for hackathon testing"""
    global qa_system
    
    try:
        if not qa_system:
            return jsonify({
                "error": "RAG system not initialized",
                "status": "error"
            }), 503
        
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "status": "error"
            }), 400
        
        query = data.get('query', '')
        if not query:
            return jsonify({
                "error": "No query provided",
                "status": "error"
            }), 400
        
        # Process the query using your RAG system
        logger.info(f"Processing query: {query}")
        answer = qa_system.ask_question(query)
        
        return jsonify({
            "response": answer,
            "query": query,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error processing webhook request: {str(e)}")
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "status": "error"
        }), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    """Alternative endpoint for asking questions"""
    return webhook()  # Same functionality as webhook

@app.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process new document"""
    global doc_processor
    
    try:
        if not doc_processor:
            return jsonify({
                "error": "Document processor not initialized",
                "status": "error"
            }), 503
        
        if 'file' not in request.files:
            return jsonify({
                "error": "No file provided",
                "status": "error"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "error": "No file selected",
                "status": "error"
            }), 400
        
        if file and file.filename.endswith('.pdf'):
            # Save uploaded file
            os.makedirs('data', exist_ok=True)
            filepath = os.path.join('data', 'uploaded_doc.pdf')
            file.save(filepath)
            
            # Process the document
            doc_processor.process_document(filepath)
            
            return jsonify({
                "message": "Document processed successfully",
                "status": "success"
            })
        else:
            return jsonify({
                "error": "Only PDF files are supported",
                "status": "error"
            }), 400
            
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "status": "error"
        }), 500

# Initialize RAG system on startup
@app.before_first_request
def startup():
    """Initialize RAG system before first request"""
    initialize_rag_system()

if __name__ == '__main__':
    # For local development
    initialize_rag_system()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=False)
