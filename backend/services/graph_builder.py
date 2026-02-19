import networkx as nx
from collections import defaultdict

def build_transaction_graph(df):
    """
    Build a directed graph from transaction data.
    
    Nodes = account IDs
    Edges = money flow (sender -> receiver) with amount and timestamp metadata
    
    Args:
        df (pd.DataFrame): Transaction data with sender_id, receiver_id, amount, timestamp
        
    Returns:
        nx.DiGraph: Directed graph with transaction metadata
    """
    G = nx.DiGraph()
    
    for _, row in df.iterrows():
        sender = str(row["sender_id"]).strip()
        receiver = str(row["receiver_id"]).strip()
        amount = float(row["amount"])
        timestamp = row["timestamp"]
        txn_id = row.get("transaction_id", "")
        
        # Add edge with metadata
        if G.has_edge(sender, receiver):
            # Aggregate if edge exists
            G[sender][receiver]["amount"] += amount
            G[sender][receiver]["count"] += 1
            G[sender][receiver]["transactions"].append({
                "id": txn_id,
                "amount": amount,
                "timestamp": timestamp.isoformat()
            })
        else:
            # Create new edge
            G.add_edge(
                sender,
                receiver,
                amount=amount,
                count=1,
                transactions=[{
                    "id": txn_id,
                    "amount": amount,
                    "timestamp": timestamp.isoformat()
                }],
                timestamp_first=timestamp,
                timestamp_last=timestamp
            )
    
    return G


def get_account_metrics(G, df):
    """
    Calculate in-degree, out-degree, and other metrics for each account.
    
    Args:
        G (nx.DiGraph): Transaction graph
        df (pd.DataFrame): Original transaction data
        
    Returns:
        dict: Account metrics keyed by account_id
    """
    metrics = {}
    
    for node in G.nodes():
        in_degree = G.in_degree(node)
        out_degree = G.out_degree(node)
        
        # Total transactions
        total_in = sum(G[u][node]["amount"] for u in G.predecessors(node))
        total_out = sum(G[node][v]["amount"] for v in G.successors(node))
        
        # Count unique counterparties
        unique_senders = len(list(G.predecessors(node)))
        unique_receivers = len(list(G.successors(node)))
        
        metrics[node] = {
            "in_degree": in_degree,
            "out_degree": out_degree,
            "unique_senders": unique_senders,
            "unique_receivers": unique_receivers,
            "total_received": round(total_in, 2),
            "total_sent": round(total_out, 2),
            "net_flow": round(total_out - total_in, 2)
        }
    
    return metrics
