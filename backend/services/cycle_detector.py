import networkx as nx

def detect_cycles(G, min_length=3, max_length=5, max_successors=5, max_paths_per_target=3):
    """
    Detect circular fund routing patterns (money laundering cycles).
    
    PATTERN: Money flows in a loop through multiple accounts
    EXAMPLE: A → B → C → A (cycle of length 3)
    
    HEAVILY BOUNDED ALGORITHM:
    - For each high-degree source node, limit successors to max_successors (default 5)
    - For each target, limit paths found to max_paths_per_target
    - Use nx.all_simple_paths(cutoff=max_length) to find paths
    - Verify path closes back to source
    - Deduplicate cycles by canonical form
    
    Args:
        G (nx.DiGraph): Transaction graph
        min_length (int): Minimum cycle length (default 3)
        max_length (int): Maximum cycle length (default 5)
        max_successors (int): Max successors per node to check (default 5)
        max_paths_per_target (int): Max paths to find per target (default 3)
        
    Returns:
        list: List of dicts with 'member_accounts', 'length', 'risk_score'
    """
    cycles = []
    seen_canonical = set()  # Track canonical forms to avoid duplicates
    
    try:
        # Only check high-degree nodes (sources of cycles are typically hub accounts)
        min_degree = 2
        high_degree_nodes = [n for n in G.nodes() if G.out_degree(n) >= min_degree]
        high_degree_nodes = sorted(high_degree_nodes, key=lambda n: G.out_degree(n), reverse=True)[:30]  # Top 30 only
        
        # Iterate through high-degree source nodes
        for source_node in high_degree_nodes:
            try:
                # Get direct successors (one-hop neighbors)
                successors = list(G.successors(source_node))
                
                # CRITICAL: Limit successors to prevent combinatorial explosion
                successors = successors[:max_successors]
                
                # For each successor, find paths back through max_length hops
                for target in successors:
                    path_count = 0
                    try:
                        # Find paths from target back to source with strict cutoff
                        paths = nx.all_simple_paths(
                            G,
                            source=target,
                            target=source_node,
                            cutoff=max_length - 1
                        )
                        
                        for path in paths:
                            if path_count >= max_paths_per_target:
                                break  # Stop after max_paths_per_target
                            
                            # path is [target, ..., source_node]
                            # Full cycle is [source_node, target, ..., source_node]
                            full_cycle = [source_node] + path
                            cycle_len = len(full_cycle) - 1  # Don't count duplicate endpoint
                            
                            if min_length <= cycle_len <= max_length:
                                # Deduplicate by canonical (sorted) form
                                canonical = tuple(sorted(full_cycle[:-1]))
                                if canonical not in seen_canonical:
                                    seen_canonical.add(canonical)
                                    cycles.append({
                                        'member_accounts': full_cycle[:-1],
                                        'length': cycle_len,
                                        'risk_score': 80.0 + min(cycle_len * 2, 15)
                                    })
                                    path_count += 1
                        
                    except (nx.NetworkXNoPath, StopIteration):
                        pass  # No path from target back to source
                        
            except Exception:
                continue  # Skip this source node on error
                
    except Exception as e:
        print(f"  ⚠ Cycle detection error: {str(e)[:50]}")
    
    return cycles
