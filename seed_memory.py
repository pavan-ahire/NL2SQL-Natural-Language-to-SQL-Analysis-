"""
seed_memory.py
--------------
Seeds Vanna's vector memory with 20 question → SQL pairs covering:
  - patients, doctors, appointments, revenue, time-based queries

Run AFTER setup_database.py:
    python seed_memory.py
"""

from vanna_setup import get_vanna_instance

# ── Training pairs ─────────────────────────────────────────────────────────────
QA_PAIRS = [
    # ── patients ──────────────────────────────────────────────────────────────
    {
        "question": "How many patients are registered in the clinic?",
        "sql": "SELECT COUNT(*) AS total_patients FROM patients;",
    },
    {
        "question": "List all patients from Mumbai",
        "sql": "SELECT name, phone, email FROM patients WHERE city = 'Mumbai' ORDER BY name;",
    },
    {
        "question": "Show patients with blood group O+",
        "sql": "SELECT name, dob, gender, city FROM patients WHERE blood_group = 'O+' ORDER BY name;",
    },
    {
        "question": "How many male and female patients are there?",
        "sql": """
SELECT gender, COUNT(*) AS count
FROM patients
GROUP BY gender
ORDER BY count DESC;
""".strip(),
    },
    {
        "question": "List patients registered in 2024",
        "sql": """
SELECT name, city, created_at
FROM patients
WHERE strftime('%Y', created_at) = '2024'
ORDER BY created_at DESC;
""".strip(),
    },
    {
        "question": "Which city has the most patients?",
        "sql": """
SELECT city, COUNT(*) AS patient_count
FROM patients
GROUP BY city
ORDER BY patient_count DESC
LIMIT 5;
""".strip(),
    },

    # ── doctors ───────────────────────────────────────────────────────────────
    {
        "question": "How many doctors are in each department?",
        "sql": """
SELECT department, COUNT(*) AS doctor_count
FROM doctors
GROUP BY department
ORDER BY doctor_count DESC;
""".strip(),
    },
    {
        "question": "Which doctor has the highest consultation fee?",
        "sql": """
SELECT name, specialization, consultation_fee
FROM doctors
ORDER BY consultation_fee DESC
LIMIT 1;
""".strip(),
    },
    {
        "question": "List all cardiologists",
        "sql": "SELECT name, experience_yrs, consultation_fee FROM doctors WHERE specialization = 'Cardiologist' ORDER BY experience_yrs DESC;",
    },
    {
        "question": "Show doctors with more than 10 years of experience",
        "sql": """
SELECT name, specialization, experience_yrs
FROM doctors
WHERE experience_yrs > 10
ORDER BY experience_yrs DESC;
""".strip(),
    },
    {
        "question": "What is the average consultation fee?",
        "sql": "SELECT ROUND(AVG(consultation_fee), 2) AS avg_fee FROM doctors;",
    },

    # ── appointments ──────────────────────────────────────────────────────────
    {
        "question": "How many appointments were completed?",
        "sql": "SELECT COUNT(*) AS completed FROM appointments WHERE status = 'Completed';",
    },
    {
        "question": "Show appointment count by status",
        "sql": """
SELECT status, COUNT(*) AS count
FROM appointments
GROUP BY status
ORDER BY count DESC;
""".strip(),
    },
    {
        "question": "Which doctor has the most appointments?",
        "sql": """
SELECT d.name, d.specialization, COUNT(a.appointment_id) AS total_appointments
FROM appointments a
JOIN doctors d ON a.doctor_id = d.doctor_id
GROUP BY d.doctor_id
ORDER BY total_appointments DESC
LIMIT 5;
""".strip(),
    },
    {
        "question": "List appointments scheduled for 2024",
        "sql": """
SELECT a.appointment_id, p.name AS patient, d.name AS doctor, a.appointment_dt, a.status
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN doctors  d ON a.doctor_id  = d.doctor_id
WHERE strftime('%Y', a.appointment_dt) = '2024'
ORDER BY a.appointment_dt DESC
LIMIT 50;
""".strip(),
    },
    {
        "question": "How many appointments were cancelled?",
        "sql": "SELECT COUNT(*) AS cancelled_appointments FROM appointments WHERE status = 'Cancelled';",
    },

    # ── treatments ────────────────────────────────────────────────────────────
    {
        "question": "What are the most common diagnoses?",
        "sql": """
SELECT diagnosis, COUNT(*) AS frequency
FROM treatments
GROUP BY diagnosis
ORDER BY frequency DESC
LIMIT 10;
""".strip(),
    },
    {
        "question": "What is the total cost of all treatments?",
        "sql": "SELECT ROUND(SUM(cost), 2) AS total_treatment_cost FROM treatments;",
    },
    {
        "question": "Show the most expensive treatments",
        "sql": """
SELECT t.treatment_name, t.diagnosis, t.cost, p.name AS patient, d.name AS doctor
FROM treatments t
JOIN patients p ON t.patient_id = p.patient_id
JOIN doctors  d ON t.doctor_id  = d.doctor_id
ORDER BY t.cost DESC
LIMIT 10;
""".strip(),
    },

    # ── invoices / revenue ────────────────────────────────────────────────────
    {
        "question": "What is the total revenue collected by the clinic?",
        "sql": "SELECT ROUND(SUM(total_amount), 2) AS total_revenue FROM invoices WHERE payment_status = 'Paid';",
    },
    {
        "question": "Show revenue by payment method",
        "sql": """
SELECT payment_method, COUNT(*) AS transactions, ROUND(SUM(total_amount), 2) AS revenue
FROM invoices
WHERE payment_status = 'Paid'
GROUP BY payment_method
ORDER BY revenue DESC;
""".strip(),
    },
    {
        "question": "How many invoices are pending payment?",
        "sql": "SELECT COUNT(*) AS pending_invoices, ROUND(SUM(total_amount), 2) AS pending_amount FROM invoices WHERE payment_status = 'Pending';",
    },
    {
        "question": "Show monthly revenue for 2023",
        "sql": """
SELECT strftime('%Y-%m', invoice_date) AS month,
       COUNT(*) AS invoice_count,
       ROUND(SUM(total_amount), 2) AS monthly_revenue
FROM invoices
WHERE payment_status = 'Paid'
  AND strftime('%Y', invoice_date) = '2023'
GROUP BY month
ORDER BY month;
""".strip(),
    },
    {
        "question": "Which patient has paid the most?",
        "sql": """
SELECT p.name, ROUND(SUM(i.total_amount), 2) AS total_paid
FROM invoices i
JOIN patients p ON i.patient_id = p.patient_id
WHERE i.payment_status = 'Paid'
GROUP BY i.patient_id
ORDER BY total_paid DESC
LIMIT 5;
""".strip(),
    },

    # ── cross-table / time queries ────────────────────────────────────────────
    {
        "question": "Show patient name, doctor name and appointment status for all completed appointments",
        "sql": """
SELECT p.name AS patient_name,
       d.name AS doctor_name,
       d.specialization,
       a.appointment_dt,
       a.status
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN doctors  d ON a.doctor_id  = d.doctor_id
WHERE a.status = 'Completed'
ORDER BY a.appointment_dt DESC
LIMIT 50;
""".strip(),
    },
]

# ── seeder ─────────────────────────────────────────────────────────────────────
def seed_memory():
    vn = get_vanna_instance()
    print(f"[Seed] Adding {len(QA_PAIRS)} Q&A pairs to Vanna memory...\n")

    for idx, pair in enumerate(QA_PAIRS, 1):
        vn.train(question=pair["question"], sql=pair["sql"])
        print(f"  [{idx:02d}] ✓  {pair['question']}")

    print(f"\n[Seed] Done. {len(QA_PAIRS)} pairs seeded successfully.")


if __name__ == "__main__":
    seed_memory()
