import numpy as np

def calculate_risk(clauses):
    """
    ML-enhanced dynamic risk scoring: Weighted + ML confidence adjustment.
    """
    # Expanded weights for all new clauses/ML
    weights = {
        # Critical
        "reentrancy_risk": 6,
        "integer_overflow": 5,
        "delegatecall_risk": 6,
        "access_control": 5,
        # High
        "ownership_transfer": 4,
        "oracle_usage": 4,
        "front_running": 4,
        "unchecked_send": 4,
        # Medium
        "token_transfer": 3,
        "pause_function": 3,
        "timestamp_dependence": 3,
        "short_address_attack": 3,
        # Low
        "payment_terms": 2,
        "termination_clause": 2,
        "penalty_clause": 2,
        "confidentiality_clause": 1,
        "data_privacy_clause": 1,
        "contract_size": 1,
        # ML bonuses
    }
    
    score = 0.0
    ml_bonus = 0.0
    
    for clause, detected in clauses.items():
        if detected:
            base_weight = weights.get(clause.replace('_ml', ''), weights.get(clause, 1))
            if '_ml' in clause:
                # ML detections get confidence multiplier
                ml_bonus += base_weight * 1.5
            else:
                score += base_weight
    
    score += ml_bonus
    
    # Dynamic thresholds with normalization
    max_possible = sum(weights.values()) * 1.5  # Approx with ML bonus
    normalized_score = min((score / max_possible) * 10, 10)
    
    if normalized_score >= 7:
        level = "HIGH RISK 🚨"
    elif normalized_score >= 4:
        level = "MEDIUM RISK ⚠️"
    else:
        level = "LOW RISK ✅"
    
    # Confidence from ML coverage
    num_ml = sum(1 for k in clauses if '_ml' in k and clauses[k])
    confidence = min(num_ml * 10, 100)
    
    return {
        "score": round(normalized_score, 2),
        "raw_score": round(score, 2),
        "risk_level": level,
        "confidence": f"{confidence}%",
        "max_possible": round(max_possible, 2)
    }
