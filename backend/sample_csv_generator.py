"""
Sample CSV generator for testing the backend.
Creates transaction data with known fraud patterns.
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def generate_sample_csv(filename="sample_transactions.csv", num_accounts=50, num_transactions=500):
    """
    Generate sample transaction data with fraud patterns.
    
    Patterns included:
    1. Cycles: Account groups in circular routing
    2. Smurfing: Fan-in aggregation patterns
    3. Shell networks: Pass-through intermediaries
    4. Legitimate transactions: Normal transfers
    """
    
    transactions = []
    
    base_time = datetime(2026, 1, 1)
    
    # Create account pool
    accounts = [f"ACC_{i:05d}" for i in range(num_accounts)]
    
    # Pattern 1: Create a cycle (A -> B -> C -> A)
    print("[Pattern 1] Creating cycle...")
    cycle_accounts = random.sample(accounts, 3)
    for i in range(10):
        transactions.append({
            "transaction_id": f"TXN_{len(transactions):06d}",
            "sender_id": cycle_accounts[0],
            "receiver_id": cycle_accounts[1],
            "amount": random.uniform(1000, 5000),
            "timestamp": (base_time + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S")
        })
        transactions.append({
            "transaction_id": f"TXN_{len(transactions):06d}",
            "sender_id": cycle_accounts[1],
            "receiver_id": cycle_accounts[2],
            "amount": random.uniform(1000, 5000),
            "timestamp": (base_time + timedelta(hours=i+1)).strftime("%Y-%m-%d %H:%M:%S")
        })
        transactions.append({
            "transaction_id": f"TXN_{len(transactions):06d}",
            "sender_id": cycle_accounts[2],
            "receiver_id": cycle_accounts[0],
            "amount": random.uniform(1000, 5000),
            "timestamp": (base_time + timedelta(hours=i+2)).strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Pattern 2: Create smurfing fan-in (many -> one)
    print("[Pattern 2] Creating smurfing (fan-in)...")
    aggregator = accounts[3]
    smurfs = random.sample(accounts[4:20], 12)
    for i, smurf in enumerate(smurfs):
        for j in range(3):
            transactions.append({
                "transaction_id": f"TXN_{len(transactions):06d}",
                "sender_id": smurf,
                "receiver_id": aggregator,
                "amount": random.uniform(100, 2000),
                "timestamp": (base_time + timedelta(hours=i*2+j)).strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # Pattern 3: Create shell network (A -> Shell -> Shell -> B)
    print("[Pattern 3] Creating shell network...")
    source = accounts[20]
    shell1 = accounts[21]
    shell2 = accounts[22]
    destination = accounts[23]
    
    for i in range(8):
        transactions.append({
            "transaction_id": f"TXN_{len(transactions):06d}",
            "sender_id": source,
            "receiver_id": shell1,
            "amount": 5000 + i * 10,
            "timestamp": (base_time + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S")
        })
        transactions.append({
            "transaction_id": f"TXN_{len(transactions):06d}",
            "sender_id": shell1,
            "receiver_id": shell2,
            "amount": 5000 + i * 10 - random.uniform(0, 100),
            "timestamp": (base_time + timedelta(hours=i, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
        })
        transactions.append({
            "transaction_id": f"TXN_{len(transactions):06d}",
            "sender_id": shell2,
            "receiver_id": destination,
            "amount": 5000 + i * 10 - random.uniform(0, 200),
            "timestamp": (base_time + timedelta(hours=i, minutes=45)).strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Fill rest with legitimate transactions
    print("[Legitimate] Creating normal transactions...")
    remaining = num_transactions - len(transactions)
    for i in range(remaining):
        sender = random.choice(accounts)
        receiver = random.choice([a for a in accounts if a != sender])
        
        transactions.append({
            "transaction_id": f"TXN_{len(transactions):06d}",
            "sender_id": sender,
            "receiver_id": receiver,
            "amount": random.uniform(100, 10000),
            "timestamp": (base_time + timedelta(hours=random.randint(0, 720))).strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Create DataFrame and save
    df = pd.DataFrame(transactions)
    df.to_csv(filename, index=False)
    
    print(f"\n✓ Generated {len(df)} transactions in {filename}")
    print(f"  Total accounts: {df['sender_id'].nunique() + df['receiver_id'].nunique()}")
    print(f"  Known fraud patterns: 3 (cycles, smurfing, shells)")
    print(f"  Legitimate transactions: ~{remaining}")
    
    return df

if __name__ == "__main__":
    df = generate_sample_csv()
    print(f"\nSample data:\n{df.head(10)}")
