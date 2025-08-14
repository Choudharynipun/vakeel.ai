import os
import logging
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import json

# Import custom modules
from models.rag_pipeline import RAGPipeline
from utils.document_processor import DocumentProcessor
from utils.legal_knowledge import LegalKnowledgeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SECRET_KEY'] = os.urandom(24)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'}

# Global objects
rag_pipeline = None
doc_processor = None
legal_kb = None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_app():
    """Initialize application components"""
    global rag_pipeline, doc_processor, legal_kb
    
    try:
        logger.info("Initializing application components...")
        
        # Create upload directory
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Initialize document processor
        logger.info("Initializing document processor...")
        doc_processor = DocumentProcessor()
        
        # Initialize legal knowledge base
        logger.info("Initializing legal knowledge base...")
        legal_kb = LegalKnowledgeBase()
        legal_kb.load_legal_documents()
        
        # Initialize RAG pipeline
        logger.info("Initializing RAG pipeline...")
        rag_pipeline = RAGPipeline()
        rag_pipeline.initialize()
        
        # Index legal documents
        logger.info("Indexing legal documents...")
        rag_pipeline.index_legal_documents(legal_kb.get_all_documents())
        
        logger.info("Application initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

@app.route('/')
def index():
    """Serve main application page"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported'}), 400
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = secure_filename(f"{file_id}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(file_path)
        logger.info(f"File uploaded: {filename}")
        
        # Process document
        extracted_text = doc_processor.extract_text(file_path)
        if not extracted_text:
            os.remove(file_path)  # Clean up
            return jsonify({'error': 'Failed to extract text from document'}), 400
        
        # Index document in RAG pipeline
        doc_id = rag_pipeline.index_document(extracted_text, filename)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'document_id': doc_id,
            'filename': file.filename,
            'text_length': len(extracted_text),
            'message': 'Document processed and indexed successfully'
        })
        
    except RequestEntityTooLarge:
        return jsonify({'error': 'File too large. Maximum size is 50MB'}), 413
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Failed to process document'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat queries"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        document_id = data.get('document_id')  # Optional: query specific document
        
        logger.info(f"Processing query: {user_message[:100]}...")
        
        # Get response from RAG pipeline
        response = rag_pipeline.query(
            user_message, 
            document_id=document_id,
            max_tokens=1000
        )
        
        return jsonify({
            'success': True,
            'response': response['answer'],
            'sources': response.get('sources', []),
            'confidence': response.get('confidence', 0.0),
            'processing_time': response.get('processing_time', 0.0)
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': 'Failed to process query'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'rag_pipeline': rag_pipeline is not None,
                'document_processor': doc_processor is not None,
                'legal_knowledge': legal_kb is not None
            }
        }
        
        if rag_pipeline:
            status['model_info'] = rag_pipeline.get_model_info()
            status['indexed_documents'] = rag_pipeline.get_document_count()
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_session():
    """Clear uploaded documents and reset session"""
    try:
        if rag_pipeline:
            rag_pipeline.clear_user_documents()
        
        return jsonify({
            'success': True,
            'message': 'Session cleared successfully'
        })
        
    except Exception as e:
        logger.error(f"Clear session error: {str(e)}")
        return jsonify({'error': 'Failed to clear session'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        init_app()
        logger.info("Starting Flask application...")
        app.run(
            host='0.0.0.0', 
            port=5000, 
            debug=False,  # Set to True for development
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise