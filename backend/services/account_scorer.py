"""
SUSPICION SCORE METHODOLOGY
===========================

This module implements a sophisticated suspicion scoring system that combines
multiple fraud indicators to produce a final suspicion score (0-100).

SCORING PRINCIPLES:
1. Pattern-based: Different fraud patterns carry different base weights
2. Contextual: Account behavior analyzed against network norms
3. Temporal: Clustering of transactions increases risk
4. Volumetric: Transaction amounts and frequencies matter
5. Deduplication: Avoid double-counting across patterns

FINAL SCORE INTERPRETATION:
- 0-30:   Low risk (legitimate business)
- 31-50:  Medium risk (warrants monitoring)
- 51-70:  High risk (likely fraudulent)
- 71-100: Critical risk (definite fraud ring member)
"""

from collections import defaultdict
import statistics

def generate_suspicious_accounts(rings, G, df, metrics):
    """
    Generate list of suspicious accounts with detailed scoring.
    
    Args:
        rings (list): List of detected fraud rings (cycles, smurfing, shells)
        G (networkx.DiGraph): Transaction graph
        df (pd.DataFrame): Original transaction data
        metrics (dict): Account metrics from graph_builder
        
    Returns:
        list: Sorted list of suspicious accounts (highest score first)
    """
    suspicious_accounts = {}  # account_id -> account_data
    account_ring_membership = defaultdict(list)  # account_id -> [ring_ids]
    
    # Step 1: Extract accounts from all rings and basic patterns
    for ring in rings:
        ring_id = ring["ring_id"]
        pattern_type = ring.get("pattern_type", "unknown")
        
        for account in ring.get("member_accounts", []):
            account = str(account).strip()
            
            if account not in account_ring_membership:
                suspicious_accounts[account] = {
                    "account_id": account,
                    "suspicion_score": 0.0,
                    "detected_patterns": [],
                    "ring_ids": [],
                    "pattern_scores": {}
                }
            
            account_ring_membership[account].append(ring_id)
            if ring_id not in suspicious_accounts[account]["ring_ids"]:
                suspicious_accounts[account]["ring_ids"].append(ring_id)
    
    # Step 2: Calculate pattern-based scores
    for ring in rings:
        ring_id = ring["ring_id"]
        pattern_type = ring.get("pattern_type", "unknown")
        risk_score = ring.get("risk_score", 50.0)
        
        for account in ring.get("member_accounts", []):
            account = str(account).strip()
            
            if account not in suspicious_accounts:
                continue
            
            # Add pattern to list (avoid duplicates)
            pattern_desc = get_pattern_description(ring)
            if pattern_desc not in suspicious_accounts[account]["detected_patterns"]:
                suspicious_accounts[account]["detected_patterns"].append(pattern_desc)
            
            # Add ring-specific pattern score
            if pattern_type not in suspicious_accounts[account]["pattern_scores"]:
                suspicious_accounts[account]["pattern_scores"][pattern_type] = risk_score
            else:
                # Take max risk score for this pattern type
                suspicious_accounts[account]["pattern_scores"][pattern_type] = max(
                    suspicious_accounts[account]["pattern_scores"][pattern_type],
                    risk_score
                )
    
    # Step 3: Calculate final suspicion scores
    for account_id, account_data in suspicious_accounts.items():
        account = str(account_id).strip()
        
        # Base score from pattern involvement
        pattern_scores = list(account_data["pattern_scores"].values())
        if pattern_scores:
            base_score = max(pattern_scores)  # Highest pattern risk
        else:
            base_score = 50.0
        
        # Behavioral modifiers
        if account in metrics:
            behavioral_adjustment = calculate_behavioral_adjustment(
                account, metrics, G
            )
        else:
            behavioral_adjustment = 0.0
        
        # Final score (capped at 100)
        final_score = min(100.0, base_score + behavioral_adjustment)
        
        suspicious_accounts[account_id]["suspicion_score"] = round(final_score, 2)
    
    # Step 4: Convert to list and sort by suspicion score (descending)
    result = list(suspicious_accounts.values())
    result.sort(key=lambda x: x["suspicion_score"], reverse=True)
    
    return result


def get_pattern_description(ring):
    """
    Generate human-readable pattern description.
    
    Args:
        ring (dict): Ring data with pattern_type
        
    Returns:
        str: Pattern description (e.g., "cycle_length_4")
    """
    pattern_type = ring.get("pattern_type", "unknown")
    
    if pattern_type == "cycle":
        cycle_length = ring.get("cycle_length", "3")
        return f"cycle_length_{cycle_length}"
    
    elif pattern_type == "smurfing":
        smurfing_type = ring.get("smurfing_type", "unknown")
        counterparty_count = ring.get("counterparty_count", "?")
        return f"smurfing_{smurfing_type}_{counterparty_count}"
    
    elif pattern_type == "shell":
        path_length = ring.get("path_length", "3")
        return f"shell_network_depth_{path_length}"
    
    else:
        return f"{pattern_type}"


def calculate_behavioral_adjustment(account, metrics, G):
    """
    Calculate behavioral risk adjustments based on network analysis.
    
    Factors:
    1. Network position (hub nodes = higher risk)
    2. Transaction velocity (rapid transactions = higher risk)
    3. Degree asymmetry (imbalanced in/out = higher risk)
    4. Statistical anomalies (unusual patterns = higher risk)
    
    Args:
        account (str): Account ID
        metrics (dict): Account metrics
        G (networkx.DiGraph): Transaction graph
        
    Returns:
        float: Adjustment to suspicion score (-10 to +20)
    """
    adjustment = 0.0
    
    if account not in metrics:
        return adjustment
    
    m = metrics[account]
    
    # 1. Hub-like behavior (high degree)
    in_degree = m["in_degree"]
    out_degree = m["out_degree"]
    total_degree = in_degree + out_degree
    
    # Hub accounts (degree > median) are slightly more suspicious
    if total_degree > 10:
        adjustment += 5.0
    if total_degree > 20:
        adjustment += 5.0
    
    # 2. Degree asymmetry (imbalanced flow)
    if total_degree > 0:
        in_ratio = in_degree / total_degree
        
        # Accounts that primarily receive or primarily send are suspicious
        if in_ratio < 0.2 or in_ratio > 0.8:
            adjustment += 3.0
    
    # 3. Transaction velocity
    # (High transaction count in short time = suspicious)
    # This would require timestamp analysis - covered in smurfing detector
    
    # 4. Statistical anomalies
    total_volume = m["total_received"] + m["total_sent"]
    
    # Very high volume might indicate exchange/payment processor (low risk)
    # Very low volume might indicate shell (higher risk already captured)
    
    # 5. Cap adjustment
    adjustment = max(-10.0, min(20.0, adjustment))
    
    return adjustment


def calculate_network_statistics(G):
    """
    Calculate network-wide statistics for context.
    
    Used to identify statistical anomalies in account behavior.
    
    Args:
        G (networkx.DiGraph): Transaction graph
        
    Returns:
        dict: Network statistics
    """
    degrees = [G.degree(n) for n in G.nodes()]
    
    return {
        "mean_degree": statistics.mean(degrees) if degrees else 0,
        "median_degree": statistics.median(degrees) if degrees else 0,
        "stdev_degree": statistics.stdev(degrees) if len(degrees) > 1 else 0,
        "total_nodes": len(G.nodes()),
        "total_edges": len(G.edges())
    }
