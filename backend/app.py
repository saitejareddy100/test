from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from document_parser.pdf_parser import extract_text
from nlp_engine.analyzer import analyze_contract

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "../uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return "Smart Contract Analyzer Backend Running"


@app.route("/upload", methods=["POST"])
def upload_contract():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Extract text from contract
    text = extract_text(file_path)

    # Analyze contract
    result = analyze_contract(text)

    # Generate AI-style summary
    summary = "Contract Analysis Summary:\n"

    if result["clauses_detected"]["payment_terms"]:
        summary += "- Payment obligations detected in the contract.\n"

    if result["clauses_detected"]["termination_clause"]:
        summary += "- Termination clause present which may end the contract early.\n"

    if result["clauses_detected"]["penalty_clause"]:
        summary += "- Penalty clause found which may cause financial liability.\n"

    if result["clauses_detected"]["confidentiality_clause"]:
        summary += "- Confidentiality requirements are included.\n"

    if result["clauses_detected"]["data_privacy_clause"]:
        summary += "- Data privacy protections are included.\n"

    summary += f"\nOverall Risk Level: {result['risk_level']}"

    return jsonify({
        "clauses_detected": result["clauses_detected"],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "text": text,
        "summary": summary
    })


if __name__ == "__main__":
    print("Starting Flask Server...")
    app.run(debug=True)