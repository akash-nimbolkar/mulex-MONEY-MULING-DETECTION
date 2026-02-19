#!/usr/bin/env python3
"""
Comprehensive Integration Test
Tests frontend-backend integration, CORS, and full workflow
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:5173"
SAMPLE_CSV = "backend/sample_transactions.csv"

print("\n" + "="*80)
print("INTEGRATION TEST - BACKEND & FRONTEND")
print("="*80)

# Test 1: CORS Headers
print("\n[TEST 1] CORS Configuration")
print("-" * 80)
try:
    response = requests.options(f"{BASE_URL}/api/upload", 
        headers={"Origin": "http://localhost:5173"})
    cors_headers = {k: v for k, v in response.headers.items() 
                   if 'Access-Control' in k or 'access-control' in k}
    print(f"Status: {response.status_code}")
    print(f"CORS Headers: {json.dumps(cors_headers, indent=2)}")
    cors_ok = len(cors_headers) > 0
    print(f"✓ CORS Configured" if cors_ok else "✗ CORS Not Configured")
except Exception as e:
    print(f"✗ Error: {e}")
    cors_ok = False

# Test 2: Frontend Server Health
print("\n[TEST 2] Frontend Server Health")
print("-" * 80)
try:
    # The frontend is an SPA, so we check if the server responds
    response = requests.head(f"{FRONTEND_URL}/", allow_redirects=True)
    frontend_up = response.status_code in [200, 302, 301]
    print(f"Frontend server status: {'✓ Running' if frontend_up else '✗ Not found'}")
    print(f"Status code: {response.status_code}")
except Exception as e:
    print(f"✗ Frontend server error: {e}")
    frontend_up = False

# Test 3: API endpoint access from frontend origin
print("\n[TEST 3] API Accessibility from Frontend Origin")
print("-" * 80)
try:
    headers = {"Origin": "http://localhost:5173"}
    response = requests.get(f"{BASE_URL}/", headers=headers, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    api_accessible = response.status_code == 200
    print(f"✓ API Accessible from Frontend" if api_accessible else "✗ API Not Accessible")
except Exception as e:
    print(f"✗ Error: {e}")
    api_accessible = False

# Test 4: Full workflow simulation
print("\n[TEST 4] Complete Workflow Simulation")
print("-" * 80)

workflow_passed = True

# Step 1: Upload
print("\n  Step 1: Simulating file upload...")
try:
    with open(SAMPLE_CSV, 'rb') as f:
        files = {'file': (Path(SAMPLE_CSV).name, f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
    if response.status_code == 200:
        print(f"    ✓ File uploaded: {response.json()['filename']}")
    else:
        print(f"    ✗ Upload failed: {response.status_code}")
        workflow_passed = False
except Exception as e:
    print(f"    ✗ Error: {e}")
    workflow_passed = False

time.sleep(1)

# Step 2: Analyze
print("\n  Step 2: Simulating analysis request...")
try:
    response = requests.post(f"{BASE_URL}/api/analyze")
    if response.status_code == 200:
        data = response.json()
        print(f"    ✓ Analysis complete")
        print(f"      - Status: {data.get('message', 'N/A')}")
        print(f"      - Timestamp: {data.get('timestamp', 'N/A')}")
    else:
        print(f"    ✗ Analysis failed: {response.status_code}")
        workflow_passed = False
except Exception as e:
    print(f"    ✗ Error: {e}")
    workflow_passed = False

time.sleep(1)

# Step 3: Get Results
print("\n  Step 3: Simulating results retrieval...")
try:
    response = requests.get(f"{BASE_URL}/api/results")
    if response.status_code == 200:
        data = response.json()
        num_nodes = len(data.get('nodes', []))
        num_edges = len(data.get('edges', []))
        num_rings = len(data.get('rings', []))
        print(f"    ✓ Results retrieved:")
        print(f"      - Network nodes: {num_nodes}")
        print(f"      - Network edges: {num_edges}")
        print(f"      - Fraud rings: {num_rings}")
        
        if 'summary' in data:
            summary = data['summary']
            print(f"      - Suspicious accounts: {summary.get('suspicious_accounts', 0)}")
    else:
        print(f"    ✗ Results failed: {response.status_code}")
        workflow_passed = False
except Exception as e:
    print(f"    ✗ Error: {e}")
    workflow_passed = False

# Step 4: Download
print("\n  Step 4: Simulating JSON download...")
try:
    response = requests.get(f"{BASE_URL}/api/download-json")
    if response.status_code == 200:
        content_size = len(response.content)
        print(f"    ✓ JSON report downloaded: {content_size} bytes")
        # Verify it's valid JSON
        try:
            json.loads(response.content)
            print(f"    ✓ JSON is valid")
        except:
            print(f"    ✗ JSON is invalid")
            workflow_passed = False
    else:
        print(f"    ✗ Download failed: {response.status_code}")
        workflow_passed = False
except Exception as e:
    print(f"    ✗ Error: {e}")
    workflow_passed = False

# Test 5: API Routes Verification
print("\n[TEST 5] Backend Route Coverage")
print("-" * 80)

routes_to_test = [
    ("GET", "/"),
    ("POST", "/api/upload"),
    ("POST", "/api/analyze"),
    ("GET", "/api/results"),
    ("GET", "/api/download-json"),
]

routes_ok = True
for method, route in routes_to_test:
    try:
        if method == "GET":
            response = requests.head(f"{BASE_URL}{route}", allow_redirects=False)
        else:
            response = requests.options(f"{BASE_URL}{route}", allow_redirects=False)
        
        # For OPTIONS request, we just check if route exists
        exists = response.status_code in [200, 201, 204, 400, 405]
        status = "✓" if exists else "✗"
        print(f"  {status} {method:4s} {route:30s} → {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"  ✗ {method:4s} {route:30s} → Connection failed")
        routes_ok = False
    except Exception as e:
        print(f"  ✗ {method:4s} {route:30s} → {str(e)}")

# Final Summary
print("\n" + "="*80)
print("INTEGRATION TEST SUMMARY")
print("="*80)

results = {
    "CORS Enabled": cors_ok,
    "Frontend Server": frontend_up,
    "API Accessible": api_accessible,
    "Complete Workflow": workflow_passed,
    "Routes Available": routes_ok,
}

for test_name, result in results.items():
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"{status}: {test_name}")

all_passed = all(results.values())
print("\n" + ("="*80))
if all_passed:
    print("✓ ALL INTEGRATION TESTS PASSED")
    print("  The backend and frontend are properly integrated and working together!")
else:
    print("⚠ SOME TESTS FAILED")
    print("  Please review the failed tests above")
print("="*80 + "\n")

# Generate system information
print("[SYSTEM INFO]")
print("-" * 80)
print(f"Backend URL: {BASE_URL}")
print(f"Frontend URL: {FRONTEND_URL}")
print(f"Sample CSV: {Path(SAMPLE_CSV).resolve()}")
print()
