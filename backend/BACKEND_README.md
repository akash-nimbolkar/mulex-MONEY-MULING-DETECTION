# Money Muling Detection Engine - Backend

Production-grade Flask backend for RIFT 2026 Money Muling Detection Challenge.

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### 1. POST /upload
Upload CSV file for analysis.

**Request:**
```bash
curl -X POST -F "file=@transactions.csv" http://localhost:5000/upload
```

**Response:**
```json
{
  "message": "File uploaded successfully",
  "filename": "transactions.csv",
  "file_size": 102400,
  "upload_time": "2026-02-19T10:30:45"
}
```

### 2. POST /analyze
Run fraud detection analysis on uploaded file.

**Request:**
```bash
curl -X POST http://localhost:5000/analyze
```

**Response:**
```json
{
  "message": "Analysis completed successfully",
  "summary": {
    "total_accounts_analyzed": 500,
    "total_transactions_processed": 5000,
    "suspicious_accounts_flagged": 15,
    "fraud_rings_detected": 4,
    "processing_time_seconds": 2.3
  }
}
```

### 3. GET /results
Get visualization data and analysis results.

**Request:**
```bash
curl http://localhost:5000/results
```

**Response:**
```json
{
  "nodes": [...],        // Account nodes
  "edges": [...],        // Transaction flows
  "rings": [...],        // Detected fraud rings
  "accounts": [...]      // Suspicious accounts with scores
}
```

### 4. GET /download-json
Download complete analysis report as JSON.

**Request:**
```bash
curl http://localhost:5000/download-json > fraud_report.json
```

## Detection Algorithms

### 1. Cycle Detection
Detects circular fund routing patterns (A → B → C → A).

**Features:**
- Filters cycles of length 3-5
- Risk scoring based on cycle complexity
- Accounts money flows for context

### 2. Smurfing Detection
Detects fan-in (aggregation) and fan-out (dispersal) patterns.

**Features:**
- Fan-in: Multiple senders → 1 receiver (aggregation)
- Fan-out: 1 sender → Multiple receivers (dispersal)
- Temporal analysis: Tightly clustered = higher risk
- Threshold: ≥10 unique counterparties

### 3. Shell Network Detection
Detects layered shell networks with intermediate accounts.

**Features:**
- Identifies pass-through intermediaries
- Analyzes path length and volume consistency
- Flags accounts with minimal transaction counts

## Suspicion Score Methodology

**Score Range: 0-100**

- **0-30**: Low risk (legitimate business)
- **31-50**: Medium risk (warrants monitoring)
- **51-70**: High risk (likely fraudulent)
- **71-100**: Critical risk (definite fraud member)

**Calculation:**
1. **Base Score**: Highest pattern risk (cycles=85-95, smurfing=65-75, shells=60-80)
2. **Behavioral Adjustments**:
   - Hub-like behavior: +5-10
   - Degree asymmetry: +3-5
   - Network position anomalies: +2-5
3. **Final Score**: min(100, base + adjustments)

**Pattern Weighting:**
- Cycles are highest risk (sophisticated obfuscation)
- Smurfing is medium risk (threshold avoidance)
- Shells are medium risk (audit trail confusion)

## JSON Output Format (RIFT Spec)

```json
{
  "suspicious_accounts": [
    {
      "account_id": "ACC_00123",
      "suspicion_score": 87.5,
      "detected_patterns": ["cycle_length_3", "smurfing_fan_in_15"],
      "ring_ids": ["RING_001", "SMURK_003"]
    }
  ],
  "fraud_rings": [
    {
      "ring_id": "RING_001",
      "member_accounts": ["ACC_00123", "ACC_00456", "ACC_00789"],
      "pattern_type": "cycle",
      "risk_score": 95.3
    }
  ],
  "summary": {
    "total_accounts_analyzed": 500,
    "total_transactions_processed": 5000,
    "suspicious_accounts_flagged": 15,
    "fraud_rings_detected": 4,
    "processing_time_seconds": 2.3,
    "detection_timestamp": "2026-02-19 10:35:22"
  }
}
```

## CSV Input Format

Required columns (case-insensitive, flexible naming):
- `sender_id` (also accepts: sender, sender_account, from_account, source)
- `receiver_id` (also accepts: receiver, receiver_account, to_account, destination)
- `amount` (numeric, currency units)
- `timestamp` (format: YYYY-MM-DD HH:MM:SS or ISO 8601)

Optional:
- `transaction_id` (auto-generated if missing)

## Performance

**Processing Speed:**
- 1,000 transactions: < 0.5 seconds
- 5,000 transactions: 1-2 seconds
- 10,000 transactions: 2-5 seconds

**Precision/Recall:**
- Precision Target: ≥70% (minimize false positives)
- Recall Target: ≥60% (catch most fraud)

## Error Handling

All endpoints return detailed error messages:

```json
{
  "error": "Analysis failed",
  "details": "CSV missing required columns: sender_id, receiver_id"
}
```

HTTP Status Codes:
- 200: Success
- 400: Bad request (invalid file, missing data)
- 413: File too large
- 500: Server error (analysis failed)

## Development

### Testing
```bash
# Create sample CSV
python sample_csv_generator.py

# Upload and analyze
curl -X POST -F "file=@sample.csv" http://localhost:5000/upload
curl -X POST http://localhost:5000/analyze
curl http://localhost:5000/results
```

### Debugging
- Check Flask logs in terminal
- Enable verbose output in analysis_engine.py
- Inspect downloaded JSON for suspicious account details

## Known Limitations

1. **Single File at a Time**: Cache holds one analysis result (overwritten on new upload)
2. **Memory Usage**: Large graphs (50K+ nodes) may require more RAM
3. **Temporal Precision**: Timestamp resolution affects smurfing detection
4. **False Positives**: Complex legitimate patterns may trigger detection

## Future Enhancements

1. Database persistence for historical analysis
2. Machine learning for score refinement
3. Advanced visualization (3D network graphs)
4. Real-time streaming analysis
5. Multi-file batch processing

---

**RIFT 2026 Challenge Submission**
