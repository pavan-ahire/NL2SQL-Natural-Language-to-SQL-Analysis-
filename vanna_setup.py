import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_PATH        = os.getenv("DB_PATH", "clinic.db")
LLM_PROVIDER   = os.getenv("LLM_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
OLLAMA_HOST    = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL", "llama3")

_vanna_instance = None


def _make_gemini_vanna():
    from vanna.chromadb import ChromaDB_VectorStore
    try:
        from vanna.google import GoogleGeminiChat
        class GeminiVanna(ChromaDB_VectorStore, GoogleGeminiChat):
            def __init__(self, config=None):
                ChromaDB_VectorStore.__init__(self, config=config)
                GoogleGeminiChat.__init__(self, config=config)
        return GeminiVanna(config={
            "api_key": GEMINI_API_KEY,
            "model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        })
    except ImportError:
        pass

    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

    class ManualGeminiVanna(ChromaDB_VectorStore):
        def __init__(self, config=None):
            ChromaDB_VectorStore.__init__(self, config=config)
            self._model = genai.GenerativeModel(
                os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            )
        def system_message(self, msg):    return msg
        def user_message(self, msg):      return msg
        def assistant_message(self, msg): return msg
        def submit_prompt(self, prompt, **kwargs):
            if isinstance(prompt, list):
                text = "\n".join(
                    p if isinstance(p, str) else p.get("content", "")
                    for p in prompt
                )
            else:
                text = str(prompt)
            return self._model.generate_content(text).text

    return ManualGeminiVanna(config={})


def _make_groq_vanna():
    from vanna.chromadb import ChromaDB_VectorStore
    try:
        from vanna.groq import Groq as VannaGroq
        class GroqVanna(ChromaDB_VectorStore, VannaGroq):
            def __init__(self, config=None):
                ChromaDB_VectorStore.__init__(self, config=config)
                VannaGroq.__init__(self, config=config)
        return GroqVanna(config={
            "api_key": GROQ_API_KEY,
            "model": os.getenv("GROQ_MODEL", "llama3-70b-8192"),
        })
    except ImportError:
        pass

    from groq import Groq as GroqClient
    from vanna.chromadb import ChromaDB_VectorStore

    class ManualGroqVanna(ChromaDB_VectorStore):
        def __init__(self, config=None):
            ChromaDB_VectorStore.__init__(self, config=config)
            self._client = GroqClient(api_key=GROQ_API_KEY)
            self._model  = os.getenv("GROQ_MODEL", "llama3-70b-8192")

        def system_message(self, msg):    return {"role": "system",    "content": msg}
        def user_message(self, msg):      return {"role": "user",      "content": msg}
        def assistant_message(self, msg): return {"role": "assistant", "content": msg}

        def submit_prompt(self, prompt, **kwargs):
            if isinstance(prompt, list):
                messages = []
                for p in prompt:
                    if isinstance(p, dict):
                        messages.append(p)
                    else:
                        messages.append({"role": "user", "content": str(p)})
            else:
                messages = [{"role": "user", "content": str(prompt)}]
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=messages
            )
            return resp.choices[0].message.content

    return ManualGroqVanna(config={})


def get_vanna_instance():
    global _vanna_instance
    if _vanna_instance is not None:
        return _vanna_instance

    print(f"[Vanna] Initialising with provider: {LLM_PROVIDER.upper()}")

    if LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            raise EnvironmentError("GEMINI_API_KEY not set in .env")
        vn = _make_gemini_vanna()

    elif LLM_PROVIDER == "groq":
        if not GROQ_API_KEY:
            raise EnvironmentError("GROQ_API_KEY not set in .env")
        vn = _make_groq_vanna()

    else:
        raise ValueError(f"Unknown LLM_PROVIDER='{LLM_PROVIDER}'. Use gemini or groq.")

    def run_sql_sqlite(sql: str):
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]
        con.close()
        return rows

    vn.run_sql        = run_sql_sqlite
    vn.run_sql_is_set = True
    _train_schema(vn)
    _vanna_instance = vn
    print("[Vanna] Instance ready.")
    return vn


def _train_schema(vn):
    ddl_list = [
        "CREATE TABLE patients (patient_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, dob TEXT NOT NULL, gender TEXT NOT NULL, blood_group TEXT, phone TEXT, email TEXT, city TEXT, created_at TEXT DEFAULT (datetime('now')));",
        "CREATE TABLE doctors (doctor_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, specialization TEXT NOT NULL, department TEXT NOT NULL, phone TEXT, email TEXT, experience_yrs INTEGER, consultation_fee REAL);",
        "CREATE TABLE appointments (appointment_id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER NOT NULL REFERENCES patients(patient_id), doctor_id INTEGER NOT NULL REFERENCES doctors(doctor_id), appointment_dt TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Scheduled', reason TEXT, notes TEXT);",
        "CREATE TABLE treatments (treatment_id INTEGER PRIMARY KEY AUTOINCREMENT, appointment_id INTEGER NOT NULL, patient_id INTEGER NOT NULL, doctor_id INTEGER NOT NULL, treatment_name TEXT NOT NULL, diagnosis TEXT, start_date TEXT, end_date TEXT, cost REAL);",
        "CREATE TABLE invoices (invoice_id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER NOT NULL, appointment_id INTEGER, amount REAL NOT NULL, tax REAL DEFAULT 0.0, discount REAL DEFAULT 0.0, total_amount REAL NOT NULL, payment_status TEXT DEFAULT 'Pending', payment_method TEXT, invoice_date TEXT NOT NULL);",
    ]
    for ddl in ddl_list:
        vn.train(ddl=ddl)
    vn.train(documentation="Clinic DB. Tables: patients, doctors, appointments (status: Scheduled/Completed/Cancelled/No-Show), treatments (diagnosis,cost), invoices (payment_status: Paid/Pending/Overdue/Cancelled). Use strftime('%Y',col) for year filter.")
    print("[Vanna] Schema training complete.")


if __name__ == "__main__":
    vn = get_vanna_instance()
    result = vn.run_sql("SELECT COUNT(*) as total FROM patients;")
    print(f"[Test] Patient count: {result}")
    print("[OK] vanna_setup.py self-test passed.")