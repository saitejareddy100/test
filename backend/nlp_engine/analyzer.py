import re
from .risk_scoring import calculate_risk


def analyze_contract(text):

    text_lower = text.lower()

    clauses = {

        "payment_terms": bool(re.search(r"\bpayment\b", text_lower)),

        "termination_clause": bool(re.search(r"\btermination\b", text_lower)),

        "penalty_clause": bool(re.search(r"\bpenalty\b|\bfine\b", text_lower)),

        "confidentiality_clause": bool(re.search(r"\bconfidential\b", text_lower)),

        "data_privacy_clause": bool(
            re.search(r"\bprivacy\b|\bdata protection\b", text_lower)
        ),
    }

    risk_result = calculate_risk(clauses)

    result = {
        "clauses_detected": clauses,
        "risk_score": risk_result["score"],
        "risk_level": risk_result["risk_level"],
    }

    return result