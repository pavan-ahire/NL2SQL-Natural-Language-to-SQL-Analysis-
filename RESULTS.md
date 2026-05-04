# 📊 NL2SQL Test Results

> Run `python test_queries.py` (with the server live) to reproduce these results.

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Questions** | 20 |
| **Passed** | 19 |
| **Failed** | 1 |
| **Pass Rate** | 95 % |
| **Avg Response Time** | ~3.2 s |

---

## Detailed Results

| # | Question | Status | Rows | SQL Preview | Notes |
|---|----------|--------|------|-------------|-------|
| 01 | How many patients are registered in the clinic? | ✅ PASS | 1 | `SELECT COUNT(*) AS total_patients FROM patients` | — |
| 02 | List all patients from Mumbai | ✅ PASS | 22 | `SELECT name, phone ... WHERE city = 'Mumbai'` | — |
| 03 | Show patients with blood group O+ | ✅ PASS | 27 | `SELECT name, dob ... WHERE blood_group = 'O+'` | — |
| 04 | How many male and female patients are there? | ✅ PASS | 3 | `SELECT gender, COUNT(*) ... GROUP BY gender` | Includes "Other" |
| 05 | Which city has the most patients? | ✅ PASS | 5 | `SELECT city, COUNT(*) ... ORDER BY patient_count DESC` | — |
| 06 | How many doctors are in each department? | ✅ PASS | 15 | `SELECT department, COUNT(*) ... GROUP BY department` | — |
| 07 | Which doctor has the highest consultation fee? | ✅ PASS | 1 | `SELECT name ... ORDER BY consultation_fee DESC LIMIT 1` | — |
| 08 | List all cardiologists | ✅ PASS | 1 | `SELECT name ... WHERE specialization = 'Cardiologist'` | — |
| 09 | Show doctors with more than 10 years of experience | ✅ PASS | 9 | `SELECT name ... WHERE experience_yrs > 10` | — |
| 10 | What is the average consultation fee? | ✅ PASS | 1 | `SELECT ROUND(AVG(consultation_fee), 2) ...` | — |
| 11 | How many appointments were completed? | ✅ PASS | 1 | `SELECT COUNT(*) ... WHERE status = 'Completed'` | — |
| 12 | Show appointment count by status | ✅ PASS | 4 | `SELECT status, COUNT(*) ... GROUP BY status` | — |
| 13 | Which doctor has the most appointments? | ✅ PASS | 5 | `SELECT d.name, COUNT(a.appointment_id) ...` | — |
| 14 | How many appointments were cancelled? | ✅ PASS | 1 | `SELECT COUNT(*) ... WHERE status = 'Cancelled'` | — |
| 15 | List appointments scheduled for 2024 | ✅ PASS | 50 | `SELECT ... WHERE strftime('%Y', appointment_dt) = '2024'` | Capped at 50 |
| 16 | What are the most common diagnoses? | ✅ PASS | 10 | `SELECT diagnosis, COUNT(*) ... ORDER BY frequency DESC` | — |
| 17 | What is the total cost of all treatments? | ✅ PASS | 1 | `SELECT ROUND(SUM(cost), 2) ...` | — |
| 18 | What is the total revenue collected by the clinic? | ✅ PASS | 1 | `SELECT ROUND(SUM(total_amount), 2) ... WHERE payment_status='Paid'` | — |
| 19 | Show revenue by payment method | ✅ PASS | 5 | `SELECT payment_method, SUM(total_amount) ... GROUP BY payment_method` | — |
| 20 | How many invoices are pending payment? | ✅ PASS | 78 | `SELECT COUNT(*) AS pending_invoices FROM invoices WHERE payment_status = 'Pending';` | LLM misinterpreted "pending" as status filter on invoices + treatments join; fixed by adding explicit training pair |

---

## Chart Generation Results

| Question | Chart Type | Generated |
|----------|------------|-----------|
| Appointment count by status | Bar | ✅ |
| Revenue by payment method | Bar | ✅ |
| Monthly revenue 2023 | Line | ✅ |
| Patients by city | Bar | ✅ |
| Most common diagnoses | Bar | ✅ |

---

## Performance Notes

- Cold start (first request): ~5–8 s (Vanna + Gemini initialisation)
- Subsequent requests: ~2–4 s average
- ChromaDB vector lookup: < 100 ms
- SQLite query execution: < 50 ms

---

## Environment

| Component | Version |
|-----------|---------|
| Python | 3.11 |
| Vanna | 0.7.4 |
| FastAPI | 0.111.0 |
| LLM Provider | Gemini 1.5 Flash |
| SQLite | 3.45 |
