import pandas as pd
from datetime import datetime

def load_transactions(file_path):
    """
    Load and validate CSV file with flexible column mapping.
    
    Expected columns: sender_id, receiver_id, amount, timestamp
    Handles common variations in naming conventions.
    
    Args:
        file_path (str): Path to CSV file
        
    Returns:
        pd.DataFrame: Validated and processed transaction data
        
    Raises:
        Exception: If required columns are missing
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise Exception(f"Failed to read CSV file: {str(e)}")
    
    # Flexible column mapping for common variations
    column_map = {
        "sender": "sender_id",
        "sender_account": "sender_id",
        "from_account": "sender_id",
        "from": "sender_id",
        "source": "sender_id",
        "receiver": "receiver_id",
        "receiver_account": "receiver_id",
        "to_account": "receiver_id",
        "to": "receiver_id",
        "destination": "receiver_id",
        "date": "timestamp",
        "time": "timestamp",
        "transaction_date": "timestamp",
        "txn_id": "transaction_id",
        "tx_id": "transaction_id",
        "id": "transaction_id"
    }
    
    # Normalize column names (lowercase)
    df.columns = df.columns.str.lower().str.strip()
    
    # Apply column mapping
    df = df.rename(columns=column_map)
    
    # Verify required columns
    REQUIRED_COLUMNS = ["sender_id", "receiver_id", "amount", "timestamp"]
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    
    if missing:
        raise Exception(f"CSV missing required columns: {', '.join(missing)}")
    
    # Auto-generate transaction_id if missing
    if "transaction_id" not in df.columns:
        df["transaction_id"] = [f"TXN_{i:06d}" for i in range(1, len(df) + 1)]
    
    # Parse timestamp
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    except Exception as e:
        raise Exception(f"Invalid timestamp format: {str(e)}")
    
    # Convert amount to float
    try:
        df["amount"] = pd.to_numeric(df["amount"], errors='coerce')
    except Exception as e:
        raise Exception(f"Invalid amount values: {str(e)}")
    
    # Remove rows with missing critical values
    df = df.dropna(subset=["sender_id", "receiver_id", "amount", "timestamp"])
    
    # Validate that sender != receiver (money muling requires different accounts)
    df = df[df["sender_id"] != df["receiver_id"]]
    
    if len(df) == 0:
        raise Exception("No valid transactions found after processing")
    
    return df
