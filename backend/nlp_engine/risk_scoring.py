def calculate_risk(clauses):

    score = 0

    if clauses["penalty_clause"]:
        score += 3

    if clauses["termination_clause"]:
        score += 2

    if clauses["payment_terms"]:
        score += 1

    if clauses["confidentiality_clause"]:
        score += 2

    if clauses["data_privacy_clause"]:
        score += 2

    if score >= 7:
        level = "HIGH RISK"

    elif score >= 4:
        level = "MEDIUM RISK"

    else:
        level = "LOW RISK"

    return {
        "score": score,
        "risk_level": level
    }