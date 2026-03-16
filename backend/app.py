from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import get_jwt_identity
import os

from config import Config
from models import db, Analysis, User
from utils import allowed_file, save_secure_file, cleanup_file
from document_parser import extract_text
from nlp_engine.analyzer import analyze_contract

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Extensions
db.init_app(app)
jwt = JWTManager(app)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["1000 per day", "50 per hour"]
)

with app.app_context():
    db.create_all()  # Create tables

# Ensure upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = app.config['MAX_CONTENT_LENGTH']

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "features": ["ML NLP", "DB History", "Auth", "Rate Limit"]})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    api_key = data.get('api_key')
    if not api_key:
        return jsonify({"error": "API key required"}), 400
    if User.query.filter_by(api_key=api_key).first():
        return jsonify({"error": "API key exists"}), 400
    user = User(api_key=api_key)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered", "user_id": user.id}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    api_key = data.get('api_key')
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401
    access_token = create_access_token(identity={'user_id': user.id})
    return jsonify(access_token=access_token), 200

@app.route('/history/<int:user_id>', methods=['GET'])
@jwt_required()
def history(user_id):
    analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).limit(20).all()
    return jsonify([{
        'id': a.id,
        'filename': a.filename,
        'risk_score': a.risk_score,
        'risk_level': a.risk_level,
        'created_at': a.created_at.isoformat()
    } for a in analyses])

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory('../frontend', 'dashboard.html')

@app.route('/<path:filename>')
def serve_file(filename):
    frontend_dir = '../frontend'
    possible_paths = [
        os.path.join(frontend_dir, filename),
        os.path.join(frontend_dir, 'js', filename),
        os.path.join(frontend_dir, 'css', filename)
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return send_from_directory(os.path.dirname(path), os.path.basename(path))
    
    return "File not found", 404

@app.route("/upload", methods=["POST"])
def upload_contract():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file.content_length and file.content_length > app.config['MAX_CONTENT_LENGTH']:
        return jsonify({"error": "File too large"}), 413

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed (PDF, DOCX, TXT only)"}), 400

    filepath = save_secure_file(file, app.config['UPLOAD_FOLDER'])
    
    try:
        text = extract_text(filepath)
        if not text or not text.strip():
            return jsonify({"error": "No text extracted from file"}), 400

        result = analyze_contract(text)

        summary_lines = ["AI Smart Contract Analysis:"]
        for key, detected in result["clauses_detected"].items():
            status = "✅ Detected" if detected else "❌ Not Found"
            summary_lines.append(f"{key.replace('_', ' ').title()}: {status}")

        summary_lines.append(f"Risk Score: {result['risk_score']}/20")
        summary_lines.append(f"Risk Level: {result['risk_level']}")
        summary = "\\n".join(summary_lines)

        # Frontend expects
        response_data = {
            "clauses_detected": result["clauses_detected"],
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "summary": summary,
            "text": text[:2000] + "..." if len(text) > 2000 else text
        }

        return jsonify(response_data)
    finally:
        cleanup_file(filepath)

if __name__ == "__main__":
    print(f"🚀 AI Smart Contract Analyzer starting...")
    print(f"📱 Frontend: http://{app.config['HOST']}:{app.config['PORT']}/dashboard")
    print(f"🔧 API Endpoint: http://{app.config['HOST']}:{app.config['PORT']}/upload")
    print(f"✅ Health: http://{app.config['HOST']}:{app.config['PORT']}/health")
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])

