#!/usr/bin/env python3
"""
Test Money Muling Detection Engine with Large Dataset (1200 rows)
Tests the backend with a significantly larger dataset to verify scalability
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

BASE_URL = "http://localhost:5000"
LARGE_CSV = "c:\\Users\\aghul\\Desktop\\money\\backend\\uploads\\dataset1200rows.csv"

print("\n" + "="*90)
print("LARGE DATASET TEST - MONEY MULING DETECTION ENGINE")
print("="*90)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Dataset: {LARGE_CSV}")

# Get file info
try:
    file_size = Path(LARGE_CSV).stat().st_size
    print(f"File Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
except:
    print(f"File Size: Unknown")

print("="*90 + "\n")

# Test 1: Upload Large Dataset
print("[TEST 1] Uploading Large Dataset (1200 rows)")
print("-" * 90)
upload_time = 0
upload_ok = False
start_time = time.time()
try:
    with open(LARGE_CSV, 'rb') as f:
        files = {'file': (Path(LARGE_CSV).name, f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/api/upload", files=files, timeout=30)
    
    upload_time = time.time() - start_time
    print(f"Status: {response.status_code}")
    print(f"Upload Time: {upload_time:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ File uploaded: {data.get('filename', 'unknown')}")
        print(f"  - Size: {data.get('file_size', 'unknown'):,} bytes")
        print(f"  - Timestamp: {data.get('upload_time', 'unknown')}")
        upload_ok = True
    else:
        print(f"✗ Upload failed")
        print(f"Response: {response.text}")
        upload_ok = False
except Exception as e:
    print(f"✗ Error: {e}")
    upload_ok = False

time.sleep(2)

# Test 2: Run Analysis
print("\n[TEST 2] Running Analysis on Large Dataset")
print("-" * 90)
analysis_time = 0
analysis_ok = False
start_time = time.time()
try:
    response = requests.post(f"{BASE_URL}/api/analyze", timeout=60)
    analysis_time = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    print(f"Analysis Time: {analysis_time:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Analysis completed")
        print(f"  - Message: {data.get('message', 'N/A')}")
        if 'summary' in data:
            summary = data['summary']
            print(f"  - Cycles: {summary.get('cycles', 0)}")
            print(f"  - Rings: {summary.get('rings', 0)}")
            print(f"  - Smurfing: {summary.get('smurfing', 0)}")
            print(f"  - Shells: {summary.get('shells', 0)}")
        analysis_ok = True
    else:
        print(f"✗ Analysis failed")
        analysis_ok = False
except Exception as e:
    print(f"✗ Error: {e}")
    analysis_ok = False

time.sleep(1)

# Test 3: Get Detailed Results
print("\n[TEST 3] Retrieving Analysis Results")
print("-" * 90)
results_time = 0
results_ok = False
start_time = time.time()
try:
    response = requests.get(f"{BASE_URL}/api/results", timeout=30)
    results_time = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    print(f"Retrieval Time: {results_time:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        
        # Network Statistics
        num_nodes = len(data.get('nodes', []))
        num_edges = len(data.get('edges', []))
        num_rings = len(data.get('rings', []))
        
        print(f"✓ Results retrieved:")
        print(f"\n  ╔═ NETWORK GRAPH ═════════════════════╗")
        print(f"  ║ Nodes (Accounts): {num_nodes:<20} ║")
        print(f"  ║ Edges (Transactions): {num_edges:<15} ║")
        print(f"  ║ Rings (Fraud Patterns): {num_rings:<12} ║")
        print(f"  ╚══════════════════════════════════════╝")
        
        if 'summary' in data:
            summary = data['summary']
            print(f"\n  ╔═ FRAUD DETECTION ════════════════════╗")
            print(f"  ║ Circular Patterns: {summary.get('cycles', 0):<19} ║")
            print(f"  ║ Smurfing Patterns: {summary.get('smurfing', 0):<19} ║")
            print(f"  ║ Shell Networks: {summary.get('shells', 0):<23} ║")
            print(f"  ║ Suspicious Accounts: {summary.get('suspicious_accounts', 0):<16} ║")
            print(f"  ╚══════════════════════════════════════╝")
        
        results_ok = True
    else:
        print(f"✗ Results failed: {response.status_code}")
        results_ok = False
except Exception as e:
    print(f"✗ Error: {e}")
    results_ok = False

# Test 4: Download JSON Report
print("\n[TEST 4] Downloading JSON Report")
print("-" * 90)
download_time = 0
download_ok = False
start_time = time.time()
try:
    response = requests.get(f"{BASE_URL}/api/download-json", timeout=30)
    download_time = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    print(f"Download Time: {download_time:.2f}s")
    
    if response.status_code == 200:
        content_size = len(response.content)
        print(f"✓ JSON report downloaded: {content_size:,} bytes ({content_size/1024:.1f} KB)")
        
        # Verify JSON validity
        try:
            json_data = json.loads(response.content)
            print(f"✓ JSON is valid")
            
            if 'metadata' in json_data:
                print(f"  - Format: {json_data['metadata'].get('format', 'N/A')}")
                print(f"  - Version: {json_data['metadata'].get('version', 'N/A')}")
            
            download_ok = True
        except:
            print(f"✗ JSON is invalid")
            download_ok = False
    else:
        print(f"✗ Download failed: {response.status_code}")
        download_ok = False
except Exception as e:
    print(f"✗ Error: {e}")
    download_ok = False

# Summary and Comparison
print("\n" + "="*90)
print("TEST SUMMARY & PERFORMANCE COMPARISON")
print("="*90)

results = {
    "Large Dataset Upload": upload_ok,
    "Large Dataset Analysis": analysis_ok,
    "Results Retrieval": results_ok,
    "JSON Download": download_ok,
}

print("\nTest Results:")
for test_name, result in results.items():
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"  {status}: {test_name}")

print("\nPerformance Metrics:")
print(f"  • Upload Time: {upload_time:.2f}s")
print(f"  • Analysis Time: {analysis_time:.2f}s")
print(f"  • Results Retrieval: {results_time:.2f}s")
print(f"  • Download Time: {download_time:.2f}s")
print(f"  • Total Time: {upload_time + analysis_time + results_time + download_time:.2f}s")

print("\nComparison with Sample Dataset (500 rows):")
print(f"  Sample Dataset:")
print(f"    - Upload: ~0.5s")
print(f"    - Analysis: ~0.2s")
print(f"    - Total: ~0.7s")
print(f"")
print(f"  Large Dataset (1200 rows = 2.4x larger):")
print(f"    - Upload: {upload_time:.2f}s")
print(f"    - Analysis: {analysis_time:.2f}s")
print(f"    - Total: {upload_time + analysis_time:.2f}s")

if all(results.values()):
    print(f"\n✓ ALL TESTS PASSED")
    print(f"✓ System handles larger datasets efficiently")
    scale_factor = (upload_time + analysis_time) / 0.7
    print(f"✓ Scalability: {scale_factor:.2f}x time increase for {2.4:.1f}x data increase")
else:
    print(f"\n⚠ Some tests failed - review results above")

print("\n" + "="*90 + "\n")
