# 🧠 IntelliQuery AI

### AI-Powered Natural Language to SQL Analytics Platform

> Ask questions in plain English → Get SQL queries → Retrieve data → Visualize insights instantly.

---

## 🚀 Overview

**IntelliQuery AI** is a production-ready AI analytics system that allows users to interact with a database using natural language.

Instead of writing SQL manually, users can simply ask:

> *"Show top 5 patients by total spending"*

…and the system will:

* 🧠 Generate SQL using AI
* 🛡️ Validate query safety
* 🗄️ Execute on database
* 📊 Return structured data
* 📈 Generate visual insights

---

## 🧩 Key Features

* 🔹 Natural Language → SQL (NL2SQL)
* 🔹 AI-powered query generation (Vanna 2.0)
* 🔹 Secure SQL validation (SELECT-only)
* 🔹 FastAPI backend (production-ready)
* 🔹 SQLite database (clinic dataset)
* 🔹 Automatic chart generation (Plotly)
* 🔹 Modern Streamlit dashboard (IntelliQuery UI)
* 🔹 Error handling & edge-case management

---
---

## 🎬 Demo
<img width="1919" height="698" alt="image" src="https://github.com/user-attachments/assets/8c84cf24-1da9-4092-85f7-bb537b593eb6" />
<img width="1488" height="789" alt="image" src="https://github.com/user-attachments/assets/0f4a4572-64fd-4cf4-a394-edc3d25976c3" />
<img width="1575" height="343" alt="image" src="https://github.com/user-attachments/assets/dea66770-f572-4d12-9763-e141ab22c82e" />

---

## 🏗️ System Architecture

```
User Input (Natural Language)
        │
        ▼
Streamlit Dashboard (UI)
        │
        ▼
FastAPI Backend (/chat)
        │
        ▼
Vanna AI (LLM Engine)
        │
        ▼
Generated SQL
        │
        ▼
SQL Validation Layer
        │
        ▼
SQLite Database
        │
        ▼
Results + Chart (JSON)
        │
        ▼
Dashboard Visualization
```

---

## 🖥️ Dashboard (UI)

### IntelliQuery AI Dashboard

* Clean AI SaaS-style interface
* KPI cards for quick insights
* Generated SQL viewer
* Data table + visualization
* Chat-style interaction

Run dashboard:

```bash
streamlit run dashboard.py
```

---

## ⚙️ Tech Stack

| Layer         | Technology             |
| ------------- | ---------------------- |
| AI Engine     | Vanna AI 2.0           |
| LLM           | Gemini / Groq / Ollama |
| Backend       | FastAPI                |
| Database      | SQLite                 |
| Visualization | Plotly                 |
| Frontend      | Streamlit              |


<!---
## 📁 Project Structure

```
project/
│
├── main.py               # FastAPI backend
├── vanna_setup.py       # AI model setup
├── seed_memory.py       # Training Q→SQL pairs
├── setup_database.py    # Database creation
├── dashboard.py         # Streamlit UI
├── requirements.txt
├── README.md
├── RESULTS.md
└── clinic.db
```

---
--->




# 🏥 NL2SQL Clinic System

> Natural Language → SQL → Results + Charts  
> Built with **Vanna 2.0 · FastAPI · SQLite · Gemini / Groq / Ollama**

---

## 📐 Architecture

```
User Question
     │
     ▼
┌─────────────────────┐
│   FastAPI  /chat    │  POST { "question": "..." }
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Vanna 2.0 Agent   │  ChromaDB vector store
│   (Gemini/Groq/     │  ← retrieves similar Q→SQL pairs
│    Ollama LLM)      │  → generates SQL
└────────┬────────────┘
         │ SQL
         ▼
┌─────────────────────┐
│  SQL Validator      │  Blocks INSERT/UPDATE/DELETE/DROP etc.
└────────┬────────────┘
         │ Safe SELECT
         ▼
┌─────────────────────┐
│  SQLite (clinic.db) │  5 tables, ~1 400 rows
└────────┬────────────┘
         │ Rows
         ▼
┌─────────────────────┐
│  Plotly Chart Gen   │  Auto-detects bar / line / pie / scatter
└────────┬────────────┘
         │
         ▼
JSON Response { sql, columns, rows, chart_json, message }
```

---

## 📁 File Structure

```
project/
├── setup_database.py   # Create SQLite DB + dummy data
├── vanna_setup.py      # Vanna 2.0 agent factory
├── seed_memory.py      # Train Vanna with 25 Q→SQL pairs
├── main.py             # FastAPI app (/chat + /health)
├── test_queries.py     # 20-question automated test suite
├── requirements.txt
├── .env.example        # Copy to .env and fill in API key
├── README.md
└── RESULTS.md
```

---

## ⚙️ Setup & Installation

### 1 · Prerequisites

- Python 3.10+
- pip

### 2 · Clone / create project folder

```bash
mkdir nl2sql_project && cd nl2sql_project
# copy all project files here
```

### 3 · Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4 · Install dependencies

```bash
pip install -r requirements.txt
```

### 5 · Configure API key

```bash
cp .env.example .env
```

Open `.env` and set your key:

| Provider | Variable | Where to get it |
|----------|----------|-----------------|
| Gemini (default) | `GEMINI_API_KEY` | https://aistudio.google.com/app/apikey |
| Groq | `GROQ_API_KEY` | https://console.groq.com/keys |
| Ollama (local) | *(no key needed)* | https://ollama.com |

To switch provider, change `LLM_PROVIDER=groq` or `LLM_PROVIDER=ollama` in `.env`.

---

## 🚀 Run the Project

Execute **in order**:

```bash
# Step 1 – create database with dummy data
python setup_database.py

# Step 2 – seed Vanna memory with Q→SQL examples
python seed_memory.py

# Step 3 – start the API server
uvicorn main:app --reload
```



## 🔌 API Reference

### `GET /health`

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "database": "connected",
  "db_tables": ["appointments","doctors","invoices","patients","treatments"],
  "provider": "gemini",
  "version": "1.0.0"
}
```

---

### `POST /chat`

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How many patients are from Mumbai?", "generate_chart": true}'
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | ✅ | Natural language question |
| `generate_chart` | bool | ❌ | Return Plotly JSON chart (default: true) |

**Response**

```json
{
  "question": "How many patients are from Mumbai?",
  "sql": "SELECT COUNT(*) AS total FROM patients WHERE city = 'Mumbai';",
  "columns": ["total"],
  "rows": [{"total": 22}],
  "row_count": 1,
  "chart_json": null,
  "message": "Query returned 1 row(s).",
  "error": null
}
```

---

### Interactive Docs

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |

---

## 🧪 Run Tests

```bash
# Make sure the server is running first!
python test_queries.py
```

Tests 20 questions and saves `test_results.json`.

---

## 🛡️ SQL Validation

The system **blocks** any SQL containing:

`INSERT` · `UPDATE` · `DELETE` · `DROP` · `ALTER` · `CREATE` · `TRUNCATE` · `EXEC` · `PRAGMA` · `ATTACH` · `sqlite_master` · comment injection (`--`) · stacked queries

Only `SELECT` and `WITH … SELECT` (CTEs) are allowed.

---

## 🗃️ Database Schema

### `patients` (200 rows)
| Column | Type |
|--------|------|
| patient_id | INTEGER PK |
| name | TEXT |
| dob | TEXT |
| gender | TEXT |
| blood_group | TEXT |
| phone | TEXT |
| email | TEXT |
| city | TEXT |
| created_at | TEXT |

### `doctors` (15 rows)
| Column | Type |
|--------|------|
| doctor_id | INTEGER PK |
| name | TEXT |
| specialization | TEXT |
| department | TEXT |
| experience_yrs | INTEGER |
| consultation_fee | REAL |

### `appointments` (500 rows)
| Column | Type |
|--------|------|
| appointment_id | INTEGER PK |
| patient_id | FK |
| doctor_id | FK |
| appointment_dt | TEXT |
| status | TEXT (Scheduled/Completed/Cancelled/No-Show) |
| reason | TEXT |

### `treatments` (350 rows)
| Column | Type |
|--------|------|
| treatment_id | INTEGER PK |
| appointment_id | FK |
| patient_id | FK |
| doctor_id | FK |
| treatment_name | TEXT |
| diagnosis | TEXT |
| cost | REAL |

### `invoices` (300 rows)
| Column | Type |
|--------|------|
| invoice_id | INTEGER PK |
| patient_id | FK |
| appointment_id | FK |
| amount / tax / discount / total_amount | REAL |
| payment_status | TEXT (Paid/Pending/Overdue/Cancelled) |
| payment_method | TEXT |
| invoice_date | TEXT |

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| `GEMINI_API_KEY not set` | Add key to `.env` |
| `clinic.db not found` | Run `python setup_database.py` first |
| `Vanna memory empty` | Run `python seed_memory.py` |
| Port 8000 in use | `uvicorn main:app --port 8001 --reload` |
| Ollama not responding | Start Ollama: `ollama serve` |

---
---

## 🛡️ Security & Validation

The system strictly enforces:

* ✅ Only SELECT queries allowed
* ❌ Blocks: INSERT, UPDATE, DELETE, DROP
* ❌ Prevents SQL injection
* ❌ Blocks system table access

---

## 📊 Sample Queries

* How many patients do we have?
* Show revenue by doctor
* Top 5 patients by spending
* Monthly appointment trends
* Patients by city

---

## 🧪 Testing

Run test cases:

```bash
python test_queries.py
```

---

## 📈 Performance & Evaluation

* Supports 20+ test queries
* Handles joins, aggregations, filters
* Generates accurate SQL for most cases
* Returns charts automatically

---

## 🧠 Future Improvements

* Chat history memory
* Query caching
* Streaming responses
* Role-based access
* Multi-database support

---

## 🎯 Conclusion

**IntelliQuery AI** demonstrates how AI can transform traditional database interaction into a seamless conversational experience.

This project showcases:

* AI integration
* Backend engineering
* Data visualization
* Production-level design

---

## 📬 Contact
**PAVAN AHIRE**
- GitHub: https://github.com/pavan-ahire
- LinkedIn: https://www.linkedin.com/in/pavan-ahire-260940364/

---
Feel free to connect or review the project.

⭐ If you found this useful, give it a star!
