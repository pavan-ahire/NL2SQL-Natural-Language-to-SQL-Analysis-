"""
test_queries.py
---------------
Runs 20 natural-language questions against the /chat endpoint and
prints a pass/fail report.

Prerequisites:
    uvicorn main:app --reload   (running in a separate terminal)

Run:
    python test_queries.py
"""

import httpx
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"
TIMEOUT  = 60  # seconds per request

TEST_QUESTIONS = [
    # patients
    "How many patients are registered in the clinic?",
    "List all patients from Mumbai",
    "Show patients with blood group O+",
    "How many male and female patients are there?",
    "Which city has the most patients?",
    # doctors
    "How many doctors are in each department?",
    "Which doctor has the highest consultation fee?",
    "List all cardiologists",
    "Show doctors with more than 10 years of experience",
    "What is the average consultation fee?",
    # appointments
    "How many appointments were completed?",
    "Show appointment count by status",
    "Which doctor has the most appointments?",
    "How many appointments were cancelled?",
    "List appointments scheduled for 2024",
    # treatments & revenue
    "What are the most common diagnoses?",
    "What is the total cost of all treatments?",
    "What is the total revenue collected by the clinic?",
    "Show revenue by payment method",
    "How many invoices are pending payment?",
]

def run_tests():
    results = []
    print(f"\n{'='*70}")
    print(f"  NL2SQL TEST SUITE — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    for i, question in enumerate(TEST_QUESTIONS, 1):
        start = time.time()
        status = "PASS"
        sql    = ""
        row_count = 0
        error  = ""

        try:
            resp = httpx.post(
                f"{API_BASE}/chat",
                json={"question": question, "generate_chart": False},
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()

            sql       = data.get("sql") or ""
            row_count = data.get("row_count", 0)
            error     = data.get("error") or ""

            if error or not sql:
                status = "FAIL"

        except Exception as e:
            status = "FAIL"
            error  = str(e)

        elapsed = round(time.time() - start, 2)

        results.append({
            "no":       i,
            "question": question,
            "status":   status,
            "sql":      sql,
            "rows":     row_count,
            "time_s":   elapsed,
            "error":    error,
        })

        icon = "✅" if status == "PASS" else "❌"
        print(f"[{i:02d}] {icon} {status}  ({elapsed}s | {row_count} rows)")
        print(f"       Q: {question}")
        if sql:
            short_sql = sql.replace("\n"," ")[:120]
            print(f"       SQL: {short_sql}{'...' if len(sql)>120 else ''}")
        if error:
            print(f"       ERR: {error}")
        print()

    # ── summary ────────────────────────────────────────────────────────────────
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = len(results) - passed

    print(f"{'='*70}")
    print(f"  RESULTS: {passed}/{len(results)} PASSED   |   {failed} FAILED")
    print(f"{'='*70}\n")

    # Save JSON
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("[Saved] test_results.json")

    return results

if __name__ == "__main__":
    run_tests()
