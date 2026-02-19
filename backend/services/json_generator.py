import time

def generate_final_json(G, df, rings, suspicious_accounts, start_time):
    """
    Generate the final JSON output in RIFT 2026 specification format.
    
    RIFT SPECIFICATION:
    {
        "suspicious_accounts": [
            {
                "account_id": "ACC_00123",
                "suspicion_score": 87.5,
                "detected_patterns": ["cycle_length_3", "high_velocity"],
                "ring_id": "RING_001"
            }
        ],
        "fraud_rings": [
            {
                "ring_id": "RING_001",
                "member_accounts": ["ACC_00123", ...],
                "pattern_type": "cycle",
                "risk_score": 95.3
            }
        ],
        "summary": {
            "total_accounts_analyzed": 500,
            "suspicious_accounts_flagged": 15,
            "fraud_rings_detected": 4,
            "processing_time_seconds": 2.3
        }
    }
    
    Args:
        G (networkx.DiGraph): Transaction graph
        df (pd.DataFrame): Original transaction data
        rings (list): All detected fraud rings
        suspicious_accounts (list): Suspicious accounts with scores
        start_time (float): Start time of analysis (from time.time())
        
    Returns:
        dict: JSON-serializable output matching RIFT spec
    """
    processing_time = round(time.time() - start_time, 2)
    
    # Format fraud rings
    formatted_rings = []
    for ring in rings:
        formatted_rings.append({
            "ring_id": ring["ring_id"],
            "member_accounts": ring["member_accounts"],
            "pattern_type": ring["pattern_type"],
            "risk_score": round(ring.get("risk_score", 75.0), 2)
        })
    
    # Format suspicious accounts
    formatted_accounts = []
    for account in suspicious_accounts:
        formatted_accounts.append({
            "account_id": str(account["account_id"]).strip(),
            "suspicion_score": round(account["suspicion_score"], 2),
            "detected_patterns": account.get("detected_patterns", []),
            "ring_ids": account.get("ring_ids", [])
        })
    
    # Summary
    summary = {
        "total_accounts_analyzed": len(G.nodes()),
        "total_transactions_processed": len(df),
        "suspicious_accounts_flagged": len(formatted_accounts),
        "fraud_rings_detected": len(formatted_rings),
        "processing_time_seconds": processing_time,
        "detection_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return {
        "suspicious_accounts": formatted_accounts,
        "fraud_rings": formatted_rings,
        "summary": summary
    }
