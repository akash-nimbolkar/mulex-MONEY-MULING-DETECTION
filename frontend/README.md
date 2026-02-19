Money Muling Detection — Frontend

Quick start:

1. cd frontend
2. npm install
3. npm run dev

This React + Vite app provides CSV upload, simple graph detection logic (cycles, fan-in/out, shell intermediates), Cytoscape visualization, and JSON export. The backend is planned in the repository root /backend.

Files:
- src/App.jsx — main UI and detection logic
- src/styles.css — basic styles

Project structure (frontend):
- src/pages/Home.jsx — homepage with CSV upload
- src/pages/Analysis.jsx — analysis dashboard with graph and tables
- src/utils/detection.js — graph algorithms and analysis helper
- src/components/ (future) — UI components

Notes:
- This is a frontend-first scaffold. The detection code is currently implemented client-side for quick testing. For production and large datasets move processing to backend.

Scoring methodology
-------------------
We use a deterministic, rule-based scoring method (no ML):
- cycle membership (length 3-5): +45 points
- fan-in (>=10 distinct senders into an account): +20 points
- fan-out (>=10 distinct receivers from an account): +20 points
- shell intermediate (intermediate accounts with 2-3 total txs in a 3+ hop chain): +15 points
- high velocity (>=6 transactions within 72 hours): +10 points

Scores are summed, capped at 100, and reported with one decimal place (e.g. 55.0). The frontend filters out accounts with final score 0. The `processing_time_seconds` field is measured from upload start to analysis completion and rounded to two decimals.
