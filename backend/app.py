from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import logging
import tempfile
from dotenv import load_dotenv

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.document_processor import DocumentProcessor
from services.web_search import WebSearchService
from services.ai_processor import AIProcessor
from services.chart_generator import ChartGenerator
from services.report_generator import ReportGenerator

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS with specific configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://127.0.0.1:8000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize services
try:
    doc_processor = DocumentProcessor()
    web_search = WebSearchService()
    ai_processor = AIProcessor()
    chart_generator = ChartGenerator()
    report_generator = ReportGenerator()
    logger.info("✅ All services initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing services: {e}")

@app.route('/')
def home():
    return "Flask backend is running!"

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Report Generator API is running",
        "services": {
            "openai": "✅" if os.getenv('OPENAI_API_KEY') else "❌",
            "serpapi": "✅" if os.getenv('SERPAPI_API_KEY') else "❌"
        }
    })

@app.route('/api/generate-report', methods=['POST', 'OPTIONS'])
def generate_report():
    """Main endpoint to generate report"""
    
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        logger.info("📝 Report generation started")
        
        # Get inputs
        topic = request.form.get('topic')
        file = request.files.get('document')
        
        if not topic:
            logger.error("Topic not provided")
            return jsonify({"success": False, "error": "Topic is required"}), 400
        
        logger.info(f"📌 Topic: {topic}")
        
        # Step 1: Process document (if provided)
        document_text = ""
        if file:
            logger.info(f"📄 Processing document: {file.filename}")
            try:
                # Save to temporary file
                temp_path = os.path.join(tempfile.gettempdir(), file.filename)
                file.save(temp_path)
                document_text = doc_processor.extract_text_from_pdf(temp_path)
                os.remove(temp_path)
                logger.info(f"✅ Document processed: {len(document_text)} characters")
            except Exception as e:
                logger.error(f"Error processing document: {e}")
                document_text = ""
        
        # Step 2: Web search using SerpAPI
        logger.info(f"🔍 Searching web for: {topic}")
        try:
            search_results = web_search.search(topic, count=5)
            logger.info(f"✅ Found {len(search_results)} search results")
        except Exception as e:
            logger.error(f"Search error: {e}")
            search_results = []
        
        # Step 3: AI processing
        logger.info("🤖 Generating report with AI...")
        try:
            report_data = ai_processor.generate_report_structure(
                topic, document_text, search_results
            )
            
            if not report_data:
                raise Exception("AI processor returned empty report")
            
            logger.info("✅ Report structure generated")
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return jsonify({
                "success": False, 
                "error": f"Failed to generate report: {str(e)}"
            }), 500
        
        # Step 4: Generate charts
        logger.info("📊 Generating charts...")
        try:
            charts = chart_generator.generate_charts(
                report_data.get('data_points', [])
            )
            logger.info(f"✅ Generated {len(charts)} charts")
        except Exception as e:
            logger.error(f"Chart generation error: {e}")
            charts = []
        
        # Step 5: Generate PDF
        logger.info("📄 Generating PDF...")
        try:
            pdf_path = report_generator.generate_pdf(report_data, charts)
            logger.info(f"✅ PDF generated: {pdf_path}")
        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            return jsonify({
                "success": False,
                "error": f"Failed to generate PDF: {str(e)}"
            }), 500
        
        # Return response
        return jsonify({
            "success": True,
            "report": report_data,
            "charts_count": len(charts),
            "pdf_url": f"/api/download/{os.path.basename(pdf_path)}",
            "search_results_count": len(search_results)
        })
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_report(filename):
    """Download generated PDF report"""
    try:
        file_path = os.path.join(tempfile.gettempdir(), filename)
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return jsonify({"error": "File not found"}), 404
        
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=f"report_{filename}"
        )
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Check if API keys are set
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning("⚠️  OPENAI_API_KEY not set")
    if not os.getenv('SERPAPI_API_KEY'):
        logger.warning("⚠️  SERPAPI_API_KEY not set")
    
    port = int(os.getenv('PORT', 5000))
    logger.info(f"🚀 Starting server on port {port}")
    
    # Run with host='0.0.0.0' to allow external connections
    # Disable reloader and debug to avoid macOS fork-related mutex issues
    app.run(host='0.0.0.0', debug=False, use_reloader=False, threaded=False, port=port)