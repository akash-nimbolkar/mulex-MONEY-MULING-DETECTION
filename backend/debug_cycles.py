#!/usr/bin/env python
"""Debug: analyze what cycles are in the sample data"""

import sys
sys.path.insert(0, '.')

import pandas as pd
from services.csv_processor import load_transactions
from services.graph_builder import build_transaction_graph
import networkx as nx

# Load data
df = load_transactions('sample_transactions.csv')
print(f"Loaded {len(df)} transactions")

# Build graph
G = build_transaction_graph(df)
print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Find cycles
cycles_3 = []
cycles_4 = []
cycles_5 = []

seen = set()

try:
    for cycle in nx.simple_cycles(G):
        cycle_len = len(cycle)
        
        if cycle_len >= 6:
            continue  # Skip longer cycles
        
        # Canonical form
        min_elem = min(cycle)
        min_idx = cycle.index(min_elem)
        canonical = tuple(cycle[min_idx:] + cycle[:min_idx])
        
        if canonical not in seen:
            seen.add(canonical)
            
            if cycle_len == 3:
                cycles_3.append(cycle)
            elif cycle_len == 4:
                cycles_4.append(cycle)
            elif cycle_len == 5:
                cycles_5.append(cycle)
            
            print(f"Cycle-{cycle_len}: {' → '.join(cycle)} → {cycle[0]}")
            
            if len(seen) >= 20:  # Show first 20
                break
except Exception as e:
    print(f"Error: {e}")

print(f"\nTotal unique cycles found (partial): {len(seen)}")
print(f"  3-node cycles: ~{cycles_3.count(cycles_3[0]) if cycles_3 else 0}")
