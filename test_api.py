#!/usr/bin/env python3
"""
Test script to verify backend API endpoints and integration
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:5000"
SAMPLE_CSV = "backend/sample_transactions.csv"

def test_health():
    """Test the health/status endpoint"""
    print("\n" + "="*70)
    print("[TEST 1] Health Check")
    print("="*70)
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_upload():
    """Test the file upload endpoint"""
    print("\n" + "="*70)
    print("[TEST 2] File Upload")
    print("="*70)
    try:
        with open(SAMPLE_CSV, 'rb') as f:
            files = {'file': (Path(SAMPLE_CSV).name, f, 'text/csv')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_analyze():
    """Test the analysis endpoint"""
    print("\n" + "="*70)
    print("[TEST 3] Analysis")
    print("="*70)
    try:
        response = requests.post(f"{BASE_URL}/api/analyze")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            # Print structure instead of full data
            if 'cycles' in data:
                print(f"  - Cycles detected: {len(data.get('cycles', []))}")
            if 'smurfing' in data:
                print(f"  - Smurfing patterns: {len(data.get('smurfing', []))}")
            if 'shells' in data:
                print(f"  - Shell networks: {len(data.get('shells', []))}")
            if 'suspicious_accounts' in data:
                print(f"  - Suspicious accounts: {len(data.get('suspicious_accounts', []))}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_results():
    """Test the results endpoint"""
    print("\n" + "="*70)
    print("[TEST 4] Get Results")
    print("="*70)
    try:
        response = requests.get(f"{BASE_URL}/api/results")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
        else:
            print(f"Response: {response.text}")
        return response.status_code in [200, 204]
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_json_download():
    """Test the JSON download endpoint"""
    print("\n" + "="*70)
    print("[TEST 5] Download JSON Report")
    print("="*70)
    try:
        response = requests.get(f"{BASE_URL}/api/download-json")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {response.headers.get('Content-Length')} bytes")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("\n" + "🚀 "*35)
    print("MONEY MULING DETECTION - API TEST SUITE")
    print("🚀 "*35)
    
    results = {}
    
    # Test endpoints in sequence
    results['Health Check'] = test_health()
    
    results['File Upload'] = test_upload()
    time.sleep(2)  # Allow server to process
    
    results['Analysis'] = test_analyze()
    time.sleep(2)  # Allow server to process
    
    results['Get Results'] = test_results()
    
    results['Download JSON'] = test_json_download()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All API endpoints are working correctly!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
