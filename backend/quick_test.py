#!/usr/bin/env python
"""Quick test of backend analysis performance"""

import sys
import time
sys.path.insert(0, '.')

from services.analysis_engine import run_complete_analysis

print("Testing analysis engine directly...")
print("=" * 60)

t0 = time.time()
try:
    result = run_complete_analysis('sample_transactions.csv')
    elapsed = time.time() - t0

    print(f"\n✓ Analysis completed in {elapsed:.2f} seconds")
    print(f"  Cycles found: {len([r for r in result['all_rings'] if r.get('pattern_type')=='cycle'])}")
    print(f"  Smurfing found: {len([r for r in result['all_rings'] if r.get('pattern_type')=='smurfing'])}")
    print(f"  Shells found: {len([r for r in result['all_rings'] if r.get('pattern_type')=='shell'])}")
    print(f"  Suspicious accounts: {len(result['suspicious_accounts'])}")
    print(f"\n{'✓ PASS' if elapsed < 5 else '⚠ SLOW'}: Performance target is <5s")
except Exception as e:
    elapsed = time.time() - t0
    print(f"✗ Error after {elapsed:.2f}s: {str(e)[:200]}")
