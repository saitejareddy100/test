import re
import spacy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from .risk_scoring import calculate_risk

# Load spaCy model (download: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None
    print("Warning: spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")

# Mock vuln training data for TF-IDF + LogisticRegression classifier (balanced with negatives)
TRAINING_DATA = {
    "reentrancy": [
        # Positives
        "external call transfer before state update",
        "transfer external_call balance",
        "send ether recursive",
        "call.value fallback",
        # Negatives (safe patterns)
        "safeTransferFrom safeMath",
        "nonReentrant modifier",
        "ChecksEffectsInteractions",
        "transferFrom require balance"
    ],
    "integer_overflow": [
        # Positives
        "unchecked uint256 add",
        "balanceOf totalSupply",
        "mul uint overflow",
        # Negatives
        "SafeMath.add SafeMath.mul",
        "require a + b >= a",
        "unchecked { safeAdd }",
        "uint256 safeMul"
    ],
    "access_control": [
        # Positives
        "onlyOwner modifier missing",
        "public function sensitive",
        "no access control",
        # Negatives
        "modifier onlyOwner",
        "require msg.sender == owner",
        "accessControl standard",
        "Roles admin"
    ]
    # Add more vuln types...
}

# Train simple multi-label classifier (one model per vuln type)
vuln_classifiers = {}
for vuln, samples in TRAINING_DATA.items():
    if len(samples) < 4:  # Need balanced min size
        continue
    num_pos = len(samples) // 2
    num_neg = len(samples) - num_pos
    X = samples
    y = [1] * num_pos + [0] * num_neg  # Balanced: half positive, half negative
    vuln_classifiers[vuln] = make_pipeline(
        TfidfVectorizer(max_features=100, stop_words='english'),
        LogisticRegression(max_iter=200, class_weight='balanced')  # Better for small datasets
    )
    vuln_classifiers[vuln].fit(X, y)

def analyze_contract(text):
    """
    Advanced analysis: Regex + spaCy NER + ML classifier for 20+ vulns.
    """
    text_lower = text.lower()
    doc = nlp(text) if nlp else None

    # Expanded regex clauses (original + new smart contract vulns)
    clauses = {
        # Original
        "payment_terms": bool(re.search(r"payment(?:\\s+(?:terms?|conditions?))?", text_lower)),
        "termination_clause": bool(re.search(r"\\btermination\\b", text_lower)),
        "penalty_clause": bool(re.search(r"\\bpenalty\\b|\\bfine\\b", text_lower)),
        "confidentiality_clause": bool(re.search(r"\\bconfidential\\b", text_lower)),
        "data_privacy_clause": bool(re.search(r"(?:privacy|gdpr|data\\s+protection)", text_lower)),
        "token_transfer": bool(re.search(r"(?:transfer|send)\\s+(?:token|erc20)", text_lower)),
        "ownership_transfer": bool(re.search(r"(?:ownership|transferownership)", text_lower)),
"reentrancy_risk": bool(re.search(r"(?:external\\s+call|transfer)\\s*\\(\\)", text_lower)),
        "oracle_usage": bool(re.search(r"oracle", text_lower)),
        "pause_function": bool(re.search(r"pause|unpause", text_lower)),
        # New vulns
        "integer_overflow": bool(re.search(r"(?:unchecked\\s*add|uint256\\s*(?:\\+|\\*)|overflow)", text_lower)),
        "access_control": bool(re.search(r"(?:onlyOwner|modifier\\s*public)", text_lower)),
        "front_running": bool(re.search(r"(?:tx.origin|block.timestamp)", text_lower)),
        "short_address_attack": bool(re.search(r"msg.sender\\s*\\.[^\\s]{35}", text_lower)),
        "delegatecall_risk": bool(re.search(r"delegatecall", text_lower)),
        "unchecked_send": bool(re.search(r"send\\(\\s*\\)", text_lower)),
        "timestamp_dependence": bool(re.search(r"block.timestamp|now", text_lower)),
        "contract_size": bool(re.search(r"(?:contract\\s+size|deployed\\s+bytecode)", text_lower)),
    }

    # spaCy NER enhancements
    if doc:
        entities = [ent.text.lower() for ent in doc.ents]
        if any('money' in ent or '$' in ent for ent in entities):
            clauses["payment_terms"] = True
        if 'person' in [ent.label_ for ent in doc.ents]:
            clauses["access_control"] = True

    # ML Classifier predictions
    for vuln, clf in vuln_classifiers.items():
        try:
            if hasattr(clf, 'predict_proba'):
                proba = clf.predict_proba([text])[0]
                prob = proba[1] if len(proba) > 1 else 0.0
                clauses[f"{vuln}_ml"] = prob > 0.5
            else:
                clauses[f"{vuln}_ml"] = clf.predict([text])[0] == 1
        except Exception:
            clauses[f"{vuln}_ml"] = False  # Safe fallback

    risk_result = calculate_risk(clauses)

    # Enhanced summary with ML insights
    summary_lines = []
    high_ml = [k for k, v in clauses.items() if '_ml' in k and v]
    if high_ml:
        summary_lines.append(f"ML Alerts: {', '.join(high_ml)}")

    result = {
        "clauses_detected": {k: bool(v) for k, v in clauses.items()},
        "risk_score": risk_result["score"],
        "risk_level": risk_result["risk_level"],
        "ml_insights": high_ml,
        "spacy_entities": [ent.text for ent in (doc.ents if doc else [])],
    }

    return result
