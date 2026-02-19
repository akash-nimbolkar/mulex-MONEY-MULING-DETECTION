"""
Orchestrator for the entire analysis pipeline.
Coordinates all detection engines and produces final output.
"""

import time
import os
from services.csv_processor import load_transactions
from services.graph_builder import build_transaction_graph, get_account_metrics
from services.cycle_detector import detect_cycles
from services.smurfing_detector import detect_smurfing
from services.shell_detector import detect_shell_networks
from services.account_scorer import generate_suspicious_accounts, calculate_network_statistics
from services.json_generator import generate_final_json

UPLOAD_FOLDER = "uploads"

def run_complete_analysis(file_path):
    """
    Execute complete money muling detection analysis.
    
    Pipeline:
    1. Load and validate CSV
    2. Build transaction graph
    3. Run all detection algorithms (cycles, smurfing, shells)
    4. Aggregate rings and calculate suspicion scores
    5. Generate JSON output
    
    Args:
        file_path (str): Path to uploaded CSV file
        
    Returns:
        dict: Complete analysis results with:
            - G (networkx.DiGraph): Transaction graph
            - df (pd.DataFrame): Processed transactions
            - all_rings (list): All detected fraud rings
            - suspicious_accounts (list): Flagged accounts with scores
            - final_json (dict): RIFT-spec JSON output
            - network_stats (dict): Network statistics
            
    Raises:
        Exception: If any stage fails with descriptive message
    """
    
    start_time = time.time()
    
    try:
        # Stage 1: Load CSV
        print("[1/6] Loading and validating CSV...")
        df = load_transactions(file_path)
        print(f"     ✓ Loaded {len(df)} transactions")
        
        # Stage 2: Build graph
        print("[2/6] Building transaction network...")
        G = build_transaction_graph(df)
        print(f"     ✓ Created graph with {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        # Stage 3: Calculate metrics
        print("[3/6] Analyzing account metrics...")
        metrics = get_account_metrics(G, df)
        network_stats = calculate_network_statistics(G)
        print(f"     ✓ Calculated metrics for {len(metrics)} accounts")
        
        # Stage 4: Run detection algorithms
        print("[4/6] Detecting fraud patterns...")
        
        # Cycle detection with timeout
        print("     - Detecting circular fund routing...")
        try:
            # Bounded cycle detection: limit successors to avoid combinatorial explosion
            cycles = detect_cycles(G, min_length=3, max_length=5, max_successors=10)
            print(f"       Found {len(cycles)} cycles")
        except Exception as e:
            print(f"       ⚠ Cycle detection error: {str(e)[:50]}")
            cycles = []
        
        # Consolidate cycles into cycle-level fraud rings to avoid explosion
        # Group cycles that share accounts into a single ring (preserves accuracy)
        def consolidate_cycles_to_rings(cycles_list):
            import networkx as _nx
            rings_out = []
            if not cycles_list:
                return rings_out

            # Build an undirected graph connecting accounts that appear together in any cycle
            C = _nx.Graph()
            for c in cycles_list:
                members = list(c.get('member_accounts', c.get('member_accounts', [])))
                for i in range(len(members)):
                    C.add_node(members[i])
                    for j in range(i+1, len(members)):
                        C.add_edge(members[i], members[j])

            components = list(_nx.connected_components(C))
            ring_counter = 1
            # For each connected component, aggregate cycle info
            for comp in components:
                comp_nodes = sorted(list(comp))
                # gather cycles that intersect this comp
                related_cycles = [c for c in cycles_list if any(a in comp for a in c.get('member_accounts', []))]
                # compute ring risk as max of member cycle risk (fallback to 75)
                max_risk = 0.0
                for rc in related_cycles:
                    try:
                        max_risk = max(max_risk, float(rc.get('risk_score', 0)))
                    except Exception:
                        continue

                rings_out.append({
                    'ring_id': f'RING_C_{ring_counter:03d}',
                    'member_accounts': comp_nodes,
                    'pattern_type': 'cycle',
                    'risk_score': round(max_risk if max_risk>0 else 80.0, 2)
                })
                ring_counter += 1

            return rings_out

        # Replace raw cycles list with consolidated cycle rings
        consolidated_cycle_rings = consolidate_cycles_to_rings(cycles)
        print(f"       Consolidated cycles into {len(consolidated_cycle_rings)} cycle rings")
        # Smurfing detection
        print("     - Detecting smurfing patterns...")
        try:
            smurfing = detect_smurfing(G, df, fan_threshold=10, time_window_hours=72)
            print(f"       Found {len(smurfing)} smurfing patterns")
        except Exception as e:
            print(f"       ⚠ Smurfing detection error: {str(e)[:50]}")
            smurfing = []
        
        # Shell network detection with timeout
        print("     - Detecting shell networks...")
        try:
            shells = detect_shell_networks(G, shell_threshold=3, hop_limit=5)
            print(f"       Found {len(shells)} shell networks")
        except Exception as e:
            print(f"       ⚠ Shell detection error: {str(e)[:50]}")
            shells = []
        
        # Combine all rings - use consolidated cycles instead of raw cycles
        all_rings = consolidated_cycle_rings + smurfing + shells
        print(f"     ✓ Total rings detected: {len(all_rings)}")
        
        # Stage 5: Score suspicious accounts
        print("[5/6] Calculating suspicion scores...")
        stage5_start = time.time()
        suspicious_accounts = generate_suspicious_accounts(all_rings, G, df, metrics)
        stage5_time = time.time() - stage5_start
        print(f"     ✓ Flagged {len(suspicious_accounts)} suspicious accounts ({stage5_time:.2f}s)")
        
        # Stage 6: Generate JSON output
        print("[6/6] Generating output...")
        stage6_start = time.time()
        final_json = generate_final_json(G, df, all_rings, suspicious_accounts, start_time)
        stage6_time = time.time() - stage6_start
        print(f"     ✓ Complete in {final_json['summary']['processing_time_seconds']}s (json gen: {stage6_time:.2f}s)")
        
        return {
            "G": G,
            "df": df,
            "all_rings": all_rings,
            "suspicious_accounts": suspicious_accounts,
            "final_json": final_json,
            "network_stats": network_stats,
            "metrics": metrics
        }
        
    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        raise Exception(f"Analysis failed after {elapsed}s: {str(e)}")


def prepare_visualization_data(G, df, all_rings, suspicious_accounts):
    """
    Prepare data for frontend graph visualization.
    
    Args:
        G (networkx.DiGraph): Transaction graph
        df (pd.DataFrame): Transaction data
        all_rings (list): Detected fraud rings
        suspicious_accounts (list): Flagged accounts
        
    Returns:
        dict: Visualization data with nodes and edges
    """
    
    # Build set of suspicious account IDs
    suspicious_ids = {str(acc["account_id"]).strip() 
                     for acc in suspicious_accounts}
    
    # Build set of accounts in fraud rings
    ring_account_ids = set()
    for ring in all_rings:
        for acc in ring.get("member_accounts", []):
            ring_account_ids.add(str(acc).strip())
    
    # Nodes
    nodes = []
    for node in G.nodes():
        node_str = str(node).strip()
        is_suspicious = node_str in suspicious_ids
        is_in_ring = node_str in ring_account_ids
        
        # Find suspicion score if available
        suspicion_score = 0.0
        if is_suspicious:
            for acc in suspicious_accounts:
                if str(acc["account_id"]).strip() == node_str:
                    suspicion_score = acc["suspicion_score"]
                    break
        
        nodes.append({
            "id": node_str,
            "suspicious": is_suspicious,
            "in_ring": is_in_ring,
            "suspicion_score": suspicion_score,
            "label": node_str[:15]  # Truncate long IDs
        })
    
    # Edges
    edges = []
    edge_id = 0
    for u, v in G.edges():
        u_str = str(u).strip()
        v_str = str(v).strip()
        
        edge_data = G[u][v]
        
        # Highlight edges if both nodes are in fraud rings
        is_fraud_edge = (u_str in ring_account_ids and v_str in ring_account_ids)
        
        edges.append({
            "id": f"edge_{edge_id}",
            "source": u_str,
            "target": v_str,
            "amount": round(edge_data["amount"], 2),
            "count": edge_data["count"],
            "is_fraud_edge": is_fraud_edge
        })
        edge_id += 1
    
    return {
        "nodes": nodes,
        "edges": edges
    }
