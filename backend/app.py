"""
MONEY MULING DETECTION ENGINE - Flask Backend
RIFT 2026 Hackathon Challenge

This backend provides REST APIs for detecting money muling patterns
in financial transaction networks using graph theory and behavioral analysis.

ENDPOINTS:
- POST /upload              → Upload CSV file
- POST /analyze             → Analyze transactions (after upload)
- GET  /results             → Get analysis results
- GET  /download-json       → Download JSON report
- GET  /health              → Health check
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
import json
import traceback
from datetime import datetime

from services.analysis_engine import (
    run_complete_analysis,
    prepare_visualization_data
)

# Initialize Flask app
app = Flask(__name__)
# In development allow requests from the frontend dev server(s).
# Use permissive CORS during local development so Vite can auto-select ports.
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"csv"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global analysis cache
analysis_cache = {
    "results": None,
    "json_output": None,
    "viz_data": None,
    "uploaded_file": None
}


def allowed_file(filename):
    """Check if file has allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.route("/", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "Money Muling Detection Engine",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Upload and store CSV file for analysis.
    
    Expected:
    - Single file in request.files with key "file"
    - CSV format with columns: sender_id, receiver_id, amount, timestamp
    
    Returns:
    - 200: File accepted
    - 400: Invalid file or missing
    - 413: File too large
    - 500: Server error
    """
    try:
        # Validate file presence
        if "file" not in request.files:
            return jsonify({
                "error": "No file provided",
                "details": "Expected 'file' in form data"
            }), 400
        
        file = request.files["file"]
        
        if file.filename == "":
            return jsonify({
                "error": "Empty filename",
                "details": "File must have a name"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Invalid file type",
                "details": "Only CSV files are accepted"
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                "error": "File too large",
                "details": f"Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB"
            }), 413
        
        # Save file
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Remove old files to avoid conflicts
        for old_file in os.listdir(UPLOAD_FOLDER):
            old_path = os.path.join(UPLOAD_FOLDER, old_file)
            try:
                os.remove(old_path)
            except:
                pass
        
        file.save(filepath)
        analysis_cache["uploaded_file"] = filepath
        
        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename,
            "file_size": file_size,
            "upload_time": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Upload failed",
            "details": str(e)
        }), 500


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze uploaded CSV file for money muling patterns.
    
    Requires: File must be uploaded first via /upload
    
    Pipeline:
    1. Load and validate transactions
    2. Build transaction network graph
    3. Detect cycles, smurfing, shell networks
    4. Calculate suspicion scores
    5. Generate JSON output and visualization data
    
    Returns:
    - 200: Analysis complete (even if no fraud detected)
    - 400: No file uploaded
    - 500: Analysis error
    """
    try:
        # Check if file is uploaded
        if analysis_cache["uploaded_file"] is None:
            return jsonify({
                "error": "No file uploaded",
                "details": "Please upload a CSV file first using /upload"
            }), 400
        
        filepath = analysis_cache["uploaded_file"]
        
        if not os.path.exists(filepath):
            return jsonify({
                "error": "Uploaded file not found",
                "details": "File may have been deleted"
            }), 400
        
        # Run analysis
        print(f"\n{'='*70}")
        print("STARTING ANALYSIS")
        print(f"{'='*70}")
        
        results = run_complete_analysis(filepath)
        
        # Prepare visualization data
        viz_data = prepare_visualization_data(
            results["G"],
            results["df"],
            results["all_rings"],
            results["suspicious_accounts"]
        )
        
        # Cache results
        analysis_cache["results"] = results
        analysis_cache["json_output"] = results["final_json"]
        analysis_cache["viz_data"] = viz_data
        
        print(f"{'='*70}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*70}\n")
        
        return jsonify({
            "message": "Analysis completed successfully",
            "summary": results["final_json"]["summary"],
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            "error": "Analysis failed",
            "details": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route("/results", methods=["GET"])
def get_results():
    """
    Get analysis results for frontend visualization.
    
    Returns analysis data in format suitable for React components:
    - nodes: Account nodes with suspicious flags
    - edges: Transaction flows
    - rings: Detected fraud rings
    - accounts: Suspicious accounts with scores
    
    Returns:
    - 200: Results (may be empty if analysis not run)
    - 500: Error
    """
    try:
        if analysis_cache["results"] is None:
            print("⚠️ No analysis results in cache")
            return jsonify({
                "nodes": [],
                "edges": [],
                "rings": [],
                "accounts": [],
                "message": "No analysis results available yet"
            }), 200
        
        results = analysis_cache["results"]
        viz_data = analysis_cache["viz_data"]
        
        # Debug logging
        print(f"\n📊 /results endpoint called")
        print(f"   - Suspicious accounts: {len(results['suspicious_accounts'])}")
        print(f"   - All rings: {len(results['all_rings'])}")
        print(f"   - Viz nodes: {len(viz_data['nodes'])}")
        print(f"   - Viz edges: {len(viz_data['edges'])}")
        
        response_data = {
            "nodes": viz_data["nodes"],
            "edges": viz_data["edges"],
            "rings": results["all_rings"],
            "accounts": results["suspicious_accounts"],
            "summary": results["final_json"]["summary"],
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ Sending response with {len(response_data['accounts'])} accounts")
        print(f"   First 3 accounts: {response_data['accounts'][:3] if response_data['accounts'] else 'None'}\n")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to retrieve results",
            "details": str(e)
        }), 500


@app.route("/download-json", methods=["GET"])
def download_json():
    """
    Download complete analysis report as JSON file.
    
    Format: RIFT 2026 specification
    
    Returns:
    - 200: JSON file attachment
    - 400: No results available
    - 500: Error
    """
    try:
        if analysis_cache["json_output"] is None:
            return jsonify({
                "error": "No analysis results available",
                "details": "Please run analysis first"
            }), 400
        
        # Create JSON string
        json_str = json.dumps(analysis_cache["json_output"], indent=2)
        json_bytes = json_str.encode("utf-8")
        
        # Create file-like object
        json_io = io.BytesIO(json_bytes)
        
        return send_file(
            json_io,
            mimetype="application/json",
            as_attachment=True,
            download_name=f"fraud_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        ), 200
        
    except Exception as e:
        return jsonify({
            "error": "Download failed",
            "details": str(e)
        }), 500


@app.route("/api/upload", methods=["POST"])
@app.route("/api/analyze", methods=["POST"])
@app.route("/api/results", methods=["GET"])
@app.route("/api/download-json", methods=["GET"])
def api_proxy():
    """Route /api/* endpoints to non-api versions."""
    if request.path.startswith("/api/upload"):
        return upload_file()
    elif request.path.startswith("/api/analyze"):
        return analyze()
    elif request.path.startswith("/api/results"):
        return get_results()
    elif request.path.startswith("/api/download-json"):
        return download_json()


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "path": request.path
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "details": str(error)
    }), 500


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("MONEY MULING DETECTION ENGINE - Backend")
    print("RIFT 2026 Hackathon Challenge")
    print("="*70)
    print(f"Starting Flask server...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"CORS enabled for frontend development")
    print("="*70 + "\n")
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False  # Important: prevents duplicate analysis
    )
