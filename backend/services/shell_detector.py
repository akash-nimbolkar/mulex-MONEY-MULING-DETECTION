import networkx as nx
from collections import defaultdict

def detect_shell_networks(G, shell_threshold=3, hop_limit=5):
    """
    Detect layered shell networks: money passing through intermediate "shell" accounts.
    
    PATTERN: Money passes through intermediate accounts before reaching final destination
    EXAMPLE: A → Shell1 → Shell2 → B (3 hops with intermediate shells)
    
    CHARACTERISTICS:
    - Shell accounts have very few total transactions (2-3)
    - Act purely as pass-through intermediaries
    - Create distance between money source and destination
    - Used to obscure audit trails
    
    DETECTION METHOD:
    1. Identify low-degree intermediate accounts
    2. Find direct paths through these intermediaries
    3. Calculate risk based on structural characteristics
    
    Args:
        G (networkx.DiGraph): Transaction graph
        shell_threshold (int): Max transactions for account to be considered "shell"
        hop_limit (int): Maximum path length to explore
        
    Returns:
        list: Detected shell networks with structure:
            {
                "ring_id": "SHELL_001",
                "pattern_type": "shell",
                "member_accounts": [full path of accounts],
                "shell_accounts": [intermediate shell accounts],
                "source_account": str (originator),
                "destination_account": str (receiver),
                "path_length": int,
                "risk_score": float
            }
    """
    shell_networks = []
    ring_id_counter = 1
    processed_paths = set()
    
    # First, identify potential shell accounts
    potential_shells = set()
    for node in G.nodes():
        in_degree = G.in_degree(node)
        out_degree = G.out_degree(node)
        total_degree = in_degree + out_degree
        
        # Shell accounts have minimal connections
        # Usually: 1 incoming + 1 outgoing (or similar low pattern)
        if 2 <= total_degree <= 4 and in_degree > 0 and out_degree > 0:
            # Further filter: very low transaction volume
            total_volume = 0.0
            for pred in G.predecessors(node):
                total_volume += G[pred][node]["amount"]
            for succ in G.successors(node):
                total_volume += G[node][succ]["amount"]
            
            # Shells typically have modest volumes passing through
            potential_shells.add(node)
    
    # Use efficient BFS-based approach instead of all_simple_paths
    # to avoid exponential complexity
    for shell_account in potential_shells:
        # For each potential shell, find direct paths through it
        predecessors = list(G.predecessors(shell_account))
        successors = list(G.successors(shell_account))
        
        for source in predecessors:
            for target in successors:
                if source == target:
                    continue
                
                # Check if there's a short path from source to target
                try:
                    # Use shortest path to limit complexity
                    path = nx.shortest_path(G, source, target, weight=None)
                    
                    if len(path) >= 4 and shell_account in path:
                        # Verify the path actually goes through this shell
                        intermediates = path[1:-1]
                        shell_count = sum(1 for acc in intermediates 
                                        if acc in potential_shells)
                        
                        if shell_count >= 1:
                            path_key = tuple(path)
                            if path_key not in processed_paths:
                                # Calculate risk
                                risk_score = calculate_shell_network_risk(
                                    G, path, intermediates, potential_shells
                                )
                                
                                shell_networks.append({
                                    "ring_id": f"SHELL_{ring_id_counter:03d}",
                                    "pattern_type": "shell",
                                    "member_accounts": path,
                                    "shell_accounts": intermediates,
                                    "source_account": path[0],
                                    "destination_account": path[-1],
                                    "path_length": len(path),
                                    "intermediary_count": len(intermediates),
                                    "risk_score": risk_score
                                })
                                ring_id_counter += 1
                                processed_paths.add(path_key)
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue
    
    return shell_networks


def calculate_shell_network_risk(G, path, intermediates, potential_shells):
    """
    Calculate risk score for a suspected shell network.
    
    Risk factors:
    - Path length (longer = more obfuscation)
    - Number of shells (more shells = more layers)
    - Shell account characteristics (low transaction counts)
    - Transaction timing (rapid pass-through = suspicious)
    
    Args:
        G (networkx.DiGraph): Transaction graph
        path (list): Account path
        intermediates (list): Intermediate accounts
        potential_shells (set): Potential shell accounts
        
    Returns:
        float: Risk score (0-100)
    """
    base_risk = 60.0
    
    # Path length risk (longer paths = more obfuscation)
    path_length_risk = min(10.0, (len(path) - 3) * 2.0)
    
    # Shell count risk
    shell_count = sum(1 for acc in intermediates if acc in potential_shells)
    shell_risk = min(15.0, shell_count * 5.0)
    
    # Intermediary characteristics risk
    intermediary_risk = 0.0
    for acc in intermediates:
        in_d = G.in_degree(acc)
        out_d = G.out_degree(acc)
        
        # If account has very low degree, it's likely a shell
        if in_d + out_d <= 4:
            intermediary_risk += 5.0
    intermediary_risk = min(15.0, intermediary_risk)
    
    # Transaction volume consistency (shells pass through similar amounts)
    volume_consistency = check_volume_consistency(G, path)
    volume_risk = 10.0 * volume_consistency
    
    risk_score = min(95.0, 
        base_risk + path_length_risk + shell_risk + intermediary_risk + volume_risk
    )
    
    return round(risk_score, 2)


def check_volume_consistency(G, path):
    """
    Check if money flows through intermediaries with consistent amounts.
    High consistency = suspicious (indicates pre-planned transfer).
    
    Args:
        G (networkx.DiGraph): Transaction graph
        path (list): Account path
        
    Returns:
        float: Consistency score (0-1)
    """
    if len(path) < 3:
        return 0.0
    
    amounts = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if G.has_edge(u, v):
            amounts.append(G[u][v]["amount"])
    
    if not amounts:
        return 0.0
    
    # Calculate coefficient of variation
    import statistics
    try:
        mean = statistics.mean(amounts)
        if mean == 0:
            return 0.0
        std_dev = statistics.stdev(amounts)
        cv = std_dev / mean
        
        # Low CV (< 0.2) = suspicious consistency
        if cv < 0.2:
            return 1.0
        elif cv < 0.5:
            return 0.7
        elif cv < 1.0:
            return 0.3
        else:
            return 0.0
    except:
        return 0.0
