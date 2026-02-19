import requests
import time
from pathlib import Path

BASE = "http://localhost:5000"
SAMPLE = Path("backend/sample_transactions.csv")
OUT_RESULTS = Path("backend/last_results_run.json")
OUT_JSON = Path("backend/fraud_analysis_run.json")

if not SAMPLE.exists():
    print("Sample CSV not found:", SAMPLE)
    raise SystemExit(1)

print("Uploading file:", SAMPLE)
with open(SAMPLE, "rb") as f:
    files = {"file": (SAMPLE.name, f, "text/csv")}
    r = requests.post(f"{BASE}/upload", files=files)
    print("Upload status:", r.status_code, r.text)
    if r.status_code != 200:
        raise SystemExit(2)

print("Triggering analysis...")
r = requests.post(f"{BASE}/analyze")
print("Analyze status:", r.status_code, r.text)
if r.status_code != 200:
    raise SystemExit(3)

# wait briefly for server to complete caching
print("Waiting 1s for results to stabilize...")
time.sleep(1)

print("Fetching /results")
r = requests.get(f"{BASE}/results")
print("Results status:", r.status_code)
if r.status_code == 200:
    OUT_RESULTS.write_text(r.text, encoding="utf-8")
    print(f"Saved results to {OUT_RESULTS}")
else:
    print("Failed to fetch results", r.text)
    raise SystemExit(4)

print("Downloading JSON report via /download-json")
r = requests.get(f"{BASE}/download-json")
print("Download status:", r.status_code)
if r.status_code == 200:
    OUT_JSON.write_bytes(r.content)
    print(f"Saved JSON report to {OUT_JSON}")
else:
    try:
        print("Download failed:", r.json())
    except Exception:
        print("Download failed, response text:", r.text)
    raise SystemExit(5)

print("E2E run complete.")
# print small summary
try:
    d = r.json()
    print("Report keys:", list(d.keys()))
except Exception:
    print("Downloaded file saved; not JSON-parsed here.")
