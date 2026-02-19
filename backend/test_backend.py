#!/usr/bin/env python3
"""
Test script for Money Muling Detection Backend
Tests all 4 API endpoints
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_upload():
    """Test CSV upload endpoint"""
    print("\n[TEST 1] Testing /upload endpoint...")
    try:
        with open('sample_transactions.csv', 'rb') as f:
            files = {'file': f}
            response = requests.post(f'{BASE_URL}/upload', files=files)
        
        if response.status_code == 200:
            print("✓ Upload successful")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Upload error: {e}")
        return False

def test_analyze():
    """Test analysis endpoint"""
    print("\n[TEST 2] Testing /analyze endpoint...")
    try:
        response = requests.post(f'{BASE_URL}/analyze')
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Analysis successful")
            print(f"  Suspicious accounts found: {data.get('suspicious_accounts_count', 0)}")
            print(f"  Fraud rings detected: {data.get('fraud_rings_count', 0)}")
            print(f"  Processing time: {data.get('processing_time_seconds', 0):.2f}s")
            return True
        else:
            print(f"✗ Analysis failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Analysis error: {e}")
        return False

def test_results():
    """Test results retrieval endpoint"""
    print("\n[TEST 3] Testing /results endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/results')
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Results retrieved successfully")
            print(f"  Nodes in graph: {len(data.get('graph', {}).get('nodes', []))}")
            print(f"  Edges in graph: {len(data.get('graph', {}).get('edges', []))}")
            print(f"  Fraud rings: {len(data.get('fraud_rings', []))}")
            print(f"  Suspicious accounts: {len(data.get('suspicious_accounts', []))}")
            
            # Show top 3 flagged accounts
            accounts = data.get('suspicious_accounts', [])
            if accounts:
                print("\n  Top flagged accounts:")
                for i, acc in enumerate(sorted(accounts, key=lambda x: x.get('suspicion_score', 0), reverse=True)[:3]):
                    print(f"    {i+1}. {acc.get('account_id', 'N/A')}: {acc.get('suspicion_score', 0):.1f}")
            
            return True
        else:
            print(f"✗ Results failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Results error: {e}")
        return False

def test_download_json():
    """Test JSON download endpoint"""
    print("\n[TEST 4] Testing /download-json endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/download-json')
        
        if response.status_code == 200:
            data = response.json()
            print("✓ JSON download successful")
            print(f"  File size: {len(response.content)} bytes")
            print(f"  Suspicious accounts in JSON: {len(data.get('suspicious_accounts', []))}")
            print(f"  Fraud rings in JSON: {len(data.get('fraud_rings', []))}")
            print(f"  Summary: {data.get('summary', {})}")
            return True
        else:
            print(f"✗ Download failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Download error: {e}")
        return False

def main():
    print("=" * 70)
    print("MONEY MULING DETECTION - BACKEND API TEST SUITE")
    print("=" * 70)
    print(f"\nTesting backend at: {BASE_URL}")
    print(f"Sample data file: sample_transactions.csv")
    
    results = []
    
    # Test sequence
    results.append(("Upload", test_upload()))
    time.sleep(1)
    
    results.append(("Analyze", test_analyze()))
    time.sleep(1)
    
    results.append(("Results", test_results()))
    time.sleep(1)
    
    results.append(("Download JSON", test_download_json()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

if __name__ == '__main__':
    main()
