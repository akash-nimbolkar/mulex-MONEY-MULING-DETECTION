Backend placeholder

Planned endpoints:
- POST /analyze (accepts CSV) -> runs detection algorithms server-side -> returns JSON in required format

We'll implement backend after frontend verification. Recommended stack: Node.js + Express, with same detection logic as frontend but optimized for larger datasets (10k tx).