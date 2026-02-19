from datetime import timedelta

def detect_smurfing(G, df, fan_threshold=10, time_window_hours=72):
    """
    Detect smurfing patterns: aggregation of small amounts or dispersal.
    
    PATTERN 1 - Fan-in (Aggregation): Multiple senders → 1 receiver
        Example: 50 accounts each send $1,000 to Account X in 24 hours
        Purpose: Combine small transfers to avoid reporting thresholds ($10k CTR)
    
    PATTERN 2 - Fan-out (Dispersal): 1 sender → Multiple receivers
        Example: Account X sends $1,000 to 50 different accounts
        Purpose: Break down large amounts to avoid detection
    
    TEMPORAL ANALYSIS: Transactions within time_window are more suspicious
    
    Args:
        G (networkx.DiGraph): Transaction graph
        df (pd.DataFrame): Original transaction data
        fan_threshold (int): Minimum unique counterparties for fan pattern
        time_window_hours (int): Time window for aggregation analysis
        
    Returns:
        list: Detected smurfing rings with structure:
            {
                "ring_id": "SMURK_001",
                "pattern_type": "smurfing",
                "smurfing_type": "fan_in" or "fan_out",
                "member_accounts": [list of accounts],
                "hub_account": str (central aggregator/disperser),
                "risk_score": float,
                "counterparty_count": int,
                "total_volume": float,
                "transaction_count": int
            }
    """
    smurfing_rings = []
    ring_id_counter = 1
    processed_hubs = set()
    
    for node in G.nodes():
        in_degree = G.in_degree(node)
        out_degree = G.out_degree(node)
        
        # FAN-IN: Many senders → One receiver (aggregation)
        if in_degree >= fan_threshold:
            predecessors = list(G.predecessors(node))
            
            if node not in processed_hubs:
                # Calculate temporal clustering
                edge_timestamps = []
                total_amount_in = 0.0
                tx_count = 0
                
                for sender in predecessors:
                    edge_data = G[sender][node]
                    total_amount_in += edge_data["amount"]
                    tx_count += edge_data["count"]
                    
                    for txn in edge_data.get("transactions", []):
                        try:
                            edge_timestamps.append(txn["timestamp"])
                        except:
                            pass
                
                # Check if transactions cluster within time window
                temporal_risk = check_temporal_clustering(
                    edge_timestamps, time_window_hours
                )
                
                # Risk score for fan-in (aggregation)
                # Higher when: many counterparties, large volume, tight timeframe
                base_risk = 70.0
                counterparty_risk = min(1.0, (in_degree - fan_threshold) / 100.0)
                volume_risk = min(1.0, total_amount_in / 100000.0)
                temporal_factor = temporal_risk
                
                risk_score = min(99.0,
                    base_risk + (counterparty_risk * 15) + (volume_risk * 10) + (temporal_factor * 5)
                )
                
                smurfing_rings.append({
                    "ring_id": f"SMURK_{ring_id_counter:03d}",
                    "pattern_type": "smurfing",
                    "smurfing_type": "fan_in",
                    "member_accounts": predecessors + [node],
                    "hub_account": node,
                    "hub_role": "aggregator",
                    "risk_score": round(risk_score, 2),
                    "counterparty_count": in_degree,
                    "total_volume": round(total_amount_in, 2),
                    "transaction_count": tx_count
                })
                ring_id_counter += 1
                processed_hubs.add(node)
        
        # FAN-OUT: One sender → Many receivers (dispersal)
        if out_degree >= fan_threshold:
            successors = list(G.successors(node))
            
            if node not in processed_hubs:
                # Calculate temporal clustering
                edge_timestamps = []
                total_amount_out = 0.0
                tx_count = 0
                
                for receiver in successors:
                    edge_data = G[node][receiver]
                    total_amount_out += edge_data["amount"]
                    tx_count += edge_data["count"]
                    
                    for txn in edge_data.get("transactions", []):
                        try:
                            edge_timestamps.append(txn["timestamp"])
                        except:
                            pass
                
                # Check temporal clustering
                temporal_risk = check_temporal_clustering(
                    edge_timestamps, time_window_hours
                )
                
                # Risk score for fan-out (dispersal)
                base_risk = 65.0
                counterparty_risk = min(1.0, (out_degree - fan_threshold) / 100.0)
                volume_risk = min(1.0, total_amount_out / 100000.0)
                temporal_factor = temporal_risk
                
                risk_score = min(99.0,
                    base_risk + (counterparty_risk * 15) + (volume_risk * 10) + (temporal_factor * 5)
                )
                
                smurfing_rings.append({
                    "ring_id": f"SMURK_{ring_id_counter:03d}",
                    "pattern_type": "smurfing",
                    "smurfing_type": "fan_out",
                    "member_accounts": [node] + successors,
                    "hub_account": node,
                    "hub_role": "disperser",
                    "risk_score": round(risk_score, 2),
                    "counterparty_count": out_degree,
                    "total_volume": round(total_amount_out, 2),
                    "transaction_count": tx_count
                })
                ring_id_counter += 1
                processed_hubs.add(node)
    
    return smurfing_rings


def check_temporal_clustering(timestamps, time_window_hours):
    """
    Check if transactions cluster within a time window.
    Tightly clustered = higher risk (coordinated fraud).
    
    Args:
        timestamps (list): List of timestamp strings
        time_window_hours (int): Time window threshold
        
    Returns:
        float: Temporal risk score (0-1)
    """
    if not timestamps or len(timestamps) < 2:
        return 0.0
    
    try:
        from datetime import datetime
        
        # Parse timestamps
        parsed = []
        for ts in timestamps:
            try:
                parsed.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
            except:
                try:
                    parsed.append(datetime.fromisoformat(ts))
                except:
                    pass
        
        if len(parsed) < 2:
            return 0.0
        
        # Sort by time
        parsed.sort()
        
        # Calculate time spans of transactions
        time_span = parsed[-1] - parsed[0]
        time_span_hours = time_span.total_seconds() / 3600.0
        
        # If all transactions happen within time window, risk is high
        if time_span_hours <= time_window_hours:
            return min(1.0, 1.0 - (time_span_hours / time_window_hours))
        
        return 0.0
    except:
        return 0.0
