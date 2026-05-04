"""
setup_database.py
-----------------
Creates the SQLite clinic database with 5 tables and realistic dummy data:
  - patients     (200 rows)
  - doctors      (15 rows)
  - appointments (500 rows)
  - treatments   (350 rows)
  - invoices     (300 rows)

Run:  python setup_database.py
"""

import sqlite3
import random
import os
from datetime import datetime, timedelta

# ── paths ──────────────────────────────────────────────────────────────────────
DB_PATH = "clinic.db"

# ── helpers ───────────────────────────────────────────────────────────────────
FIRST_NAMES = [
    "Aarav","Aditi","Amit","Ananya","Arjun","Deepa","Farhan","Ishaan",
    "Kavya","Meera","Neha","Priya","Rahul","Riya","Rohan","Sanya","Shiv",
    "Sneha","Tanvi","Vikram","Yash","Zara","Anil","Bhavna","Chetan",
    "Divya","Esha","Gaurav","Harini","Ira","Jay","Kiran","Lakshmi",
    "Manish","Nandita","Om","Pallavi","Qasim","Rekha","Sachin","Tara",
    "Uma","Varun","Waqar","Xena","Yogesh","Zoya","Abhi","Balaji",
]

LAST_NAMES = [
    "Sharma","Verma","Patel","Singh","Kumar","Gupta","Joshi","Nair",
    "Reddy","Iyer","Mehta","Shah","Bose","Das","Roy","Pillai","Rao",
    "Menon","Chaudhary","Kapoor","Malhotra","Saxena","Trivedi","Dubey",
    "Srivastava","Pandey","Mishra","Tiwari","Shukla","Bajaj",
]

SPECIALIZATIONS = [
    "General Physician","Cardiologist","Dermatologist","Orthopedist",
    "Pediatrician","Neurologist","Gynecologist","ENT Specialist",
    "Psychiatrist","Ophthalmologist","Urologist","Endocrinologist",
    "Pulmonologist","Gastroenterologist","Rheumatologist",
]

DEPARTMENTS = [
    "General Medicine","Cardiology","Dermatology","Orthopedics",
    "Pediatrics","Neurology","Gynecology","ENT","Psychiatry",
    "Ophthalmology","Urology","Endocrinology","Pulmonology",
    "Gastroenterology","Rheumatology",
]

BLOOD_GROUPS = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]

CITIES = ["Mumbai","Delhi","Bangalore","Chennai","Hyderabad","Pune",
          "Kolkata","Ahmedabad","Jaipur","Lucknow"]

DIAGNOSIS_LIST = [
    "Hypertension","Type 2 Diabetes","Migraine","Asthma","Arthritis",
    "Anemia","Common Cold","Fever","Back Pain","Obesity",
    "Depression","Anxiety Disorder","Hypothyroidism","GERD","UTI",
    "Sinusitis","Eczema","Psoriasis","Kidney Stones","Appendicitis",
]

TREATMENT_NAMES = [
    "Blood Pressure Monitoring","Insulin Therapy","Pain Management",
    "Physiotherapy","Chemotherapy","Radiation Therapy","Dialysis",
    "Cognitive Behavioral Therapy","Antibiotic Course","Steroid Therapy",
    "Vaccination","X-Ray","MRI Scan","CT Scan","ECG","Ultrasound",
    "Blood Transfusion","Oxygen Therapy","Nutritional Counseling","Surgery",
]

STATUS_OPTIONS = ["Scheduled","Completed","Cancelled","No-Show"]
GENDER_OPTIONS  = ["Male","Female","Other"]

def rand_date(start_year=1950, end_year=2005):
    start = datetime(start_year, 1, 1)
    end   = datetime(end_year,   12, 31)
    return (start + timedelta(days=random.randint(0, (end - start).days))).strftime("%Y-%m-%d")

def rand_appt_date(start_year=2022, end_year=2024):
    start = datetime(start_year, 1, 1)
    end   = datetime(end_year,   12, 31)
    dt    = start + timedelta(days=random.randint(0, (end - start).days))
    hour  = random.choice([9,10,11,14,15,16,17])
    minute= random.choice([0,15,30,45])
    return dt.replace(hour=hour, minute=minute).strftime("%Y-%m-%d %H:%M:%S")

def rand_phone():
    return f"+91-{random.randint(7000000000,9999999999)}"

def rand_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

# ── DDL ───────────────────────────────────────────────────────────────────────
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS patients (
    patient_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    dob          TEXT    NOT NULL,
    gender       TEXT    NOT NULL,
    blood_group  TEXT,
    phone        TEXT,
    email        TEXT,
    city         TEXT,
    created_at   TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS doctors (
    doctor_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    specialization  TEXT    NOT NULL,
    department      TEXT    NOT NULL,
    phone           TEXT,
    email           TEXT,
    experience_yrs  INTEGER,
    consultation_fee REAL
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      INTEGER NOT NULL,
    doctor_id       INTEGER NOT NULL,
    appointment_dt  TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'Scheduled',
    reason          TEXT,
    notes           TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)
);

CREATE TABLE IF NOT EXISTS treatments (
    treatment_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id  INTEGER NOT NULL,
    patient_id      INTEGER NOT NULL,
    doctor_id       INTEGER NOT NULL,
    treatment_name  TEXT    NOT NULL,
    diagnosis       TEXT,
    start_date      TEXT,
    end_date        TEXT,
    cost            REAL,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
    FOREIGN KEY (patient_id)     REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id)      REFERENCES doctors(doctor_id)
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      INTEGER NOT NULL,
    appointment_id  INTEGER,
    amount          REAL    NOT NULL,
    tax             REAL    DEFAULT 0.0,
    discount        REAL    DEFAULT 0.0,
    total_amount    REAL    NOT NULL,
    payment_status  TEXT    DEFAULT 'Pending',
    payment_method  TEXT,
    invoice_date    TEXT    NOT NULL,
    FOREIGN KEY (patient_id)    REFERENCES patients(patient_id),
    FOREIGN KEY (appointment_id)REFERENCES appointments(appointment_id)
);
"""

# ── seed functions ─────────────────────────────────────────────────────────────
def seed_doctors(cur):
    rows = []
    for i, (spec, dept) in enumerate(zip(SPECIALIZATIONS, DEPARTMENTS)):
        name  = f"Dr. {rand_name()}"
        phone = rand_phone()
        email = f"dr{i+1}@clinic.in"
        exp   = random.randint(2, 30)
        fee   = round(random.uniform(300, 2000), 2)
        rows.append((name, spec, dept, phone, email, exp, fee))
    cur.executemany(
        "INSERT INTO doctors (name,specialization,department,phone,email,experience_yrs,consultation_fee) VALUES (?,?,?,?,?,?,?)",
        rows
    )
    return len(rows)

def seed_patients(cur, n=200):
    rows = []
    for i in range(n):
        name  = rand_name()
        dob   = rand_date()
        gender= random.choice(GENDER_OPTIONS)
        bg    = random.choice(BLOOD_GROUPS)
        phone = rand_phone()
        email = f"patient{i+1}@mail.com"
        city  = random.choice(CITIES)
        rows.append((name, dob, gender, bg, phone, email, city))
    cur.executemany(
        "INSERT INTO patients (name,dob,gender,blood_group,phone,email,city) VALUES (?,?,?,?,?,?,?)",
        rows
    )
    return len(rows)

def seed_appointments(cur, n=500):
    rows = []
    for _ in range(n):
        pid    = random.randint(1, 200)
        did    = random.randint(1, 15)
        dt     = rand_appt_date()
        status = random.choice(STATUS_OPTIONS)
        reason = random.choice(DIAGNOSIS_LIST)
        notes  = f"Patient reported {reason.lower()} symptoms."
        rows.append((pid, did, dt, status, reason, notes))
    cur.executemany(
        "INSERT INTO appointments (patient_id,doctor_id,appointment_dt,status,reason,notes) VALUES (?,?,?,?,?,?)",
        rows
    )
    return len(rows)

def seed_treatments(cur, n=350):
    rows = []
    for _ in range(n):
        appt_id = random.randint(1, 500)
        pid     = random.randint(1, 200)
        did     = random.randint(1, 15)
        tname   = random.choice(TREATMENT_NAMES)
        diag    = random.choice(DIAGNOSIS_LIST)
        start   = rand_appt_date(2022, 2024)
        end_dt  = (datetime.strptime(start, "%Y-%m-%d %H:%M:%S") +
                   timedelta(days=random.randint(1,30))).strftime("%Y-%m-%d")
        cost    = round(random.uniform(500, 50000), 2)
        rows.append((appt_id, pid, did, tname, diag, start[:10], end_dt, cost))
    cur.executemany(
        "INSERT INTO treatments (appointment_id,patient_id,doctor_id,treatment_name,diagnosis,start_date,end_date,cost) VALUES (?,?,?,?,?,?,?,?)",
        rows
    )
    return len(rows)

def seed_invoices(cur, n=300):
    rows = []
    methods = ["Cash","Card","UPI","Net Banking","Insurance"]
    statuses= ["Paid","Pending","Overdue","Cancelled"]
    for _ in range(n):
        pid    = random.randint(1, 200)
        appt   = random.randint(1, 500)
        amt    = round(random.uniform(500, 50000), 2)
        tax    = round(amt * 0.05, 2)
        disc   = round(amt * random.uniform(0, 0.15), 2)
        total  = round(amt + tax - disc, 2)
        status = random.choice(statuses)
        method = random.choice(methods)
        date   = rand_appt_date(2022, 2024)[:10]
        rows.append((pid, appt, amt, tax, disc, total, status, method, date))
    cur.executemany(
        "INSERT INTO invoices (patient_id,appointment_id,amount,tax,discount,total_amount,payment_status,payment_method,invoice_date) VALUES (?,?,?,?,?,?,?,?,?)",
        rows
    )
    return len(rows)

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"[INFO] Removed existing {DB_PATH}")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Create schema
    cur.executescript(CREATE_TABLES_SQL)
    con.commit()
    print("[INFO] Tables created.")

    # Seed data
    random.seed(42)
    d = seed_doctors(cur);      con.commit(); print(f"[OK] Inserted {d} doctors")
    p = seed_patients(cur);     con.commit(); print(f"[OK] Inserted {p} patients")
    a = seed_appointments(cur); con.commit(); print(f"[OK] Inserted {a} appointments")
    t = seed_treatments(cur);   con.commit(); print(f"[OK] Inserted {t} treatments")
    i = seed_invoices(cur);     con.commit(); print(f"[OK] Inserted {i} invoices")

    # Summary
    print("\n── DATABASE SUMMARY ─────────────────────────────────")
    for tbl in ["patients","doctors","appointments","treatments","invoices"]:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"  {tbl:<15}: {cur.fetchone()[0]:>5} rows")

    con.close()
    print(f"\n[DONE] Database saved to: {DB_PATH}")

if __name__ == "__main__":
    main()
