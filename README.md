# MuleX – Graph-Based Money Muling Detection Engine

MuleX is a web-based financial forensics engine built for the **RIFT 2026 Hackathon – Money Muling Detection Challenge**.  
It leverages **graph theory** to uncover hidden money muling networks that are difficult to detect using traditional database queries.

---

## 🔍 Problem Statement

Money muling is a critical component of financial crime where illicit funds are routed through networks of accounts to obscure their origin.  
Traditional rule-based or query-based systems fail to capture these **multi-hop, circular, and coordinated transaction patterns**.

MuleX addresses this problem by modeling financial transactions as a **directed graph** and applying graph-based detection algorithms to expose fraud rings.

---

## 🚀 Live Demo

🔗 **Hosted Application:** *(Add your deployed URL here)*  
📦 **GitHub Repository:** (https://github.com/akash-nimbolkar/mulex-MONEY-MULING-DETECTION) 

---

## 🧠 Core Idea

- Accounts are modeled as **nodes**
- Transactions are modeled as **directed edges**
- Fraud is detected by analyzing **network structures**, not isolated transactions

---

## ⚙️ System Architecture


CSV Upload
↓
Transaction Loader
↓
Graph Construction (NetworkX)
↓
Fraud Detection Engine
├── Cycle Detection
├── Smurfing Detection
└── Layered Shell Detection
↓
Suspicion Scoring
↓
Graph Visualization + JSON Output


---

## 🛠 Tech Stack

### Frontend
- React.js
- react-force-graph
- Tailwind CSS
- Axios

### Backend
- Python
- Flask
- NetworkX
- Pandas

---

## 📥 Input Specification

The application accepts a CSV file with the following structure:

| Column Name     | Type     | Description |
|-----------------|----------|-------------|
| transaction_id  | String   | Unique transaction identifier |
| sender_id       | String   | Sender account ID |
| receiver_id     | String   | Receiver account ID |
| amount          | Float    | Transaction amount |
| timestamp       | DateTime | Format: `YYYY-MM-DD HH:MM:SS` |

---

## 🔎 Detection Patterns Implemented

### 1. Circular Fund Routing (Cycles)
- Detects cycles of length **3 to 5**
- Example: `A → B → C → A`
- All accounts in the cycle are grouped into the same fraud ring

### 2. Smurfing Patterns (Fan-in / Fan-out)
- **Fan-in:** Multiple senders → one receiver (≥10)
- **Fan-out:** One sender → multiple receivers (≥10)
- Uses **72-hour temporal window** for increased suspicion

### 3. Layered Shell Networks
- Detects transaction chains with **3 or more hops**
- Intermediate accounts have **low transaction counts**
- Indicates pass-through or shell behavior

---

## 🧮 Suspicion Score Methodology

Each suspicious account is assigned a **suspicion score between 0 and 100** based on detected patterns.

### Scoring Logic (Example)

| Pattern Detected        | Score Contribution |
|-------------------------|--------------------|
| Cycle participation     | +40 |
| Fan-in behavior         | +25 |
| Fan-out behavior        | +25 |
| Layered shell account   | +20 |

- Scores are **cumulative**
- Final score is capped at **100**
- Each score is **explainable**, with detected patterns listed per account

This ensures transparency and avoids black-box detection.

---

## 📊 Outputs

### 1. Interactive Graph Visualization
- Nodes represent accounts
- Directed edges represent money flow
- **Red nodes:** Suspicious accounts
- **Green nodes:** Normal accounts
- Hovering on a node shows:
  - Account ID
  - Suspicion score
  - Detected patterns
  - Fraud ring ID

### 2. Fraud Ring Summary Table
Each detected ring includes:
- Ring ID
- Pattern type
- Member count
- Risk score
- Member account IDs

### 3. Downloadable JSON Report

The system generates a JSON file in the **exact required format**, including:
- Suspicious accounts
- Fraud rings
- Processing summary

---

## ⏱ Performance

- Handles datasets up to **10,000 transactions**
- Processing time ≤ **30 seconds**
- Optimized graph traversal and filtering logic

---

## ⚠️ Known Limitations

- Threshold-based detection may require tuning for different datasets
- Temporal analysis assumes consistent timestamp formats
- Legitimate high-volume merchants may require whitelisting for production use
- Designed for batch analysis, not real-time streaming (future scope)

---

## 🔮 Future Enhancements

- Real-time transaction stream analysis
- Adaptive scoring using machine learning
- Advanced ring similarity detection
- Investigator feedback loop for reducing false positives

---

## 🧪 Installation & Setup

### Backend
```bash
pip install -r requirements.txt
python app.py
```

Frontend
- npm install
- npm start

- 📌 Usage Instructions

Upload a CSV file from the homepage

Click Analyze

View graph visualization and fraud rings

Download JSON report
