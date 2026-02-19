#!/usr/bin/env python3
"""
Quick Local Project Verification Test
Verifies that the entire Money Muling Detection Engine is running locally
"""

import requests
import json
import time
from datetime import datetime

print("\n" + "="*90)
print("MONEY MULING DETECTION ENGINE - LOCAL PROJECT VERIFICATION")
print("="*90)
print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*90 + "\n")

# Test 1: Backend Health Check
print("[1] BACKEND SERVICE CHECK")
print("-" * 90)
try:
    response = requests.get("http://localhost:5000/", timeout=5)
    backend_status = "✓ RUNNING" if response.status_code == 200 else "✗ FAILED"
    backend_url = "http://localhost:5000"
    print(f"Status: {backend_status}")
    print(f"URL: {backend_url}")
    print(f"Response: {response.json()}")
    backend_ok = response.status_code == 200
except Exception as e:
    print(f"✗ ERROR: {e}")
    backend_ok = False

# Test 2: Frontend Health Check
print("\n[2] FRONTEND SERVICE CHECK")
print("-" * 90)
frontend_urls = ["http://localhost:5173/", "http://localhost:5174/", "http://localhost:5175/", "http://localhost:5176/"]
frontend_ok = False
frontend_url = None

for url in frontend_urls:
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code in [200, 302, 301]:
            frontend_ok = True
            frontend_url = url
            port = url.split(":")[-2]
            print(f"Status: ✓ RUNNING")
            print(f"URL: {url}")
            print(f"Port: {port}")
            break
    except:
        continue

if not frontend_ok:
    print(f"Status: ✗ NOT RUNNING")
else:
    print(f"Status Code: 200 - OK")

# Test 3: Quick API Test
print("\n[3] API ENDPOINTS VERIFICATION")
print("-" * 90)

endpoints = [
    ("GET", "/", "Health check"),
    ("POST", "/api/upload", "File upload"),
    ("POST", "/api/analyze", "Analysis"),
    ("GET", "/api/results", "Results"),
    ("GET", "/api/download-json", "Download"),
]

api_ok = True
for method, endpoint, description in endpoints:
    try:
        if method == "GET":
            response = requests.head(f"http://localhost:5000{endpoint}", timeout=3)
        else:
            response = requests.options(f"http://localhost:5000{endpoint}", timeout=3)
        
        status = "✓" if response.status_code in [200, 201, 204, 400, 405] else "✗"
        print(f"  {status} {method:4s} {endpoint:25s} ({description})")
    except Exception as e:
        api_ok = False
        print(f"  ✗ {method:4s} {endpoint:25s} (ERROR: {str(e)[:30]})")

# Test 4: CORS Configuration
print("\n[4] CORS CONFIGURATION CHECK")
print("-" * 90)
try:
    response = requests.options(
        "http://localhost:5000/api/upload",
        headers={"Origin": "http://localhost:5173"},
        timeout=5
    )
    cors_header = response.headers.get('Access-Control-Allow-Origin', 'NOT SET')
    cors_ok = cors_header != 'NOT SET'
    
    print(f"Status: {'✓ ENABLED' if cors_ok else '✗ DISABLED'}")
    print(f"Origin Allowed: {cors_header}")
except Exception as e:
    cors_ok = False
    print(f"✗ ERROR: {e}")

# Summary
print("\n" + "="*90)
print("PROJECT STATUS SUMMARY")
print("="*90)

services = {
    "Backend API": backend_ok,
    "Frontend UI": frontend_ok,
    "API Endpoints": api_ok,
    "CORS Configuration": cors_ok,
}

all_ok = all(services.values())

for service, status in services.items():
    indicator = "✓" if status else "✗"
    print(f"{indicator} {service:30s} {'RUNNING' if status else 'FAILED'}")

print("\n" + "="*90)
if all_ok:
    print("✓ ALL SYSTEMS OPERATIONAL - PROJECT IS RUNNING!")
    print("\nYou can access:")
    print(f"  • Frontend: {frontend_url}")
    print(f"  • Backend API: http://localhost:5000")
    print(f"  • Dashboard: {frontend_url if frontend_ok else 'NOT AVAILABLE'}")
else:
    print("⚠ SOME SYSTEMS NOT OPERATIONAL - VERIFY SETUP")
    if backend_ok:
        print("  ✓ Backend is running")
    else:
        print("  ✗ Backend needs to be started")
    
    if frontend_ok:
        print(f"  ✓ Frontend is running on {frontend_url}")
    else:
        print("  ✗ Frontend needs to be started")

print("\n" + "="*90 + "\n")
