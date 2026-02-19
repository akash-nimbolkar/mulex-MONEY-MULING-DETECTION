import json
import sys

p = 'fraud_analysis_large.json'
try:
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print('ERROR_LOADING', e)
    sys.exit(2)

sa = data.get('suspicious_accounts', [])
fr = data.get('fraud_rings', [])
summary = data.get('summary', {})

print('suspicious_accounts_count', len(sa))
print('fraud_rings_count', len(fr))
print('summary_keys', list(summary.keys()))

# Validate fields in suspicious_accounts
missing_fields = 0
not_sorted = False
prev_score = float('inf')
for i, a in enumerate(sa):
    if not isinstance(a.get('account_id'), str):
        print('missing account_id at index', i)
        missing_fields += 1
    if not isinstance(a.get('suspicion_score'), (int, float)):
        print('missing suspicion_score at index', i)
        missing_fields += 1
    if not isinstance(a.get('detected_patterns', []), list):
        print('detected_patterns not list at index', i)
        missing_fields += 1
    if not isinstance(a.get('ring_id'), str):
        print('ring_id missing or not str at index', i)
        missing_fields += 1
    score = a.get('suspicion_score', 0)
    try:
        sc = float(score)
    except:
        sc = -1
    if sc > prev_score:
        not_sorted = True
    prev_score = sc

print('missing_fields_total', missing_fields)
print('suspicion_scores_sorted_desc', not not_sorted)

# Basic checks for fraud_rings entries
bad_ring = 0
for i, r in enumerate(fr):
    if not isinstance(r.get('ring_id'), str):
        bad_ring += 1
    if not isinstance(r.get('member_accounts', []), list):
        bad_ring += 1
    if not isinstance(r.get('pattern_type'), str):
        bad_ring += 1
    if not isinstance(r.get('risk_score'), (int, float)):
        bad_ring += 1
print('fraud_rings_bad_count', bad_ring)

if missing_fields == 0 and (not not_sorted) and bad_ring == 0:
    print('VALIDATION: PASS')
    sys.exit(0)
else:
    print('VALIDATION: FAIL')
    sys.exit(1)
