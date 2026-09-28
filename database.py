import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "forensics.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT DEFAULT 'Investigator',
        created_at TEXT NOT NULL,
        last_module TEXT DEFAULT '📊 Dashboard'
    );
    """)

    # Ensure last_module column exists if table was created previously
    cursor.execute("PRAGMA table_info(users)")
    user_cols = [col[1] for col in cursor.fetchall()]
    if "last_module" not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN last_module TEXT DEFAULT '📊 Dashboard'")

    # Cases Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id TEXT PRIMARY KEY,
        case_name TEXT NOT NULL,
        investigator TEXT NOT NULL,
        created_date TEXT NOT NULL,
        status TEXT DEFAULT 'In Progress',
        priority TEXT DEFAULT 'Medium',
        description TEXT,
        client_org TEXT DEFAULT 'Internal Incident Response'
    );
    """)

    # Evidence Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence (
        evidence_id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        evidence_type TEXT NOT NULL,
        description TEXT,
        source_device TEXT,
        serial_number TEXT,
        collection_date TEXT NOT NULL,
        file_hash_sha256 TEXT NOT NULL,
        file_hash_md5 TEXT,
        storage_location TEXT,
        custody_chain TEXT,
        FOREIGN KEY (case_id) REFERENCES cases (case_id) ON DELETE CASCADE
    );
    """)

    # Findings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS findings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT NOT NULL,
        category TEXT NOT NULL,
        artifact_name TEXT NOT NULL,
        description TEXT NOT NULL,
        severity TEXT NOT NULL,
        file_path_location TEXT,
        hash_value TEXT,
        investigator_notes TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (case_id) REFERENCES cases (case_id) ON DELETE CASCADE
    );
    """)

    # Audit Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT,
        timestamp TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, pwd_hash))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user(username, password, full_name, role="Investigator"):
    conn = get_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, pwd_hash, full_name, role, created_at)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_user_last_module(username, module_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET last_module = ? WHERE username = ?", (module_name, username))
    conn.commit()
    conn.close()

def get_user_last_module(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT last_module FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row["last_module"]:
        return row["last_module"]
    return "📊 Dashboard"

# Case CRUD
def get_all_cases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases ORDER BY created_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_case_by_id(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_case(case_id, case_name, investigator, created_date, status, priority, description, client_org="Internal"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cases (case_id, case_name, investigator, created_date, status, priority, description, client_org) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (case_id, case_name, investigator, created_date, status, priority, description, client_org)
    )
    conn.commit()
    conn.close()

def update_case_status(case_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE cases SET status = ? WHERE case_id = ?", (status, case_id))
    conn.commit()
    conn.close()

def update_case_details(case_id, case_name, investigator, status, priority, description, client_org):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE cases 
        SET case_name = ?, investigator = ?, status = ?, priority = ?, description = ?, client_org = ?
        WHERE case_id = ?
    """, (case_name, investigator, status, priority, description, client_org, case_id))
    conn.commit()
    conn.close()

def delete_case(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM evidence WHERE case_id = ?", (case_id,))
    cursor.execute("DELETE FROM findings WHERE case_id = ?", (case_id,))
    cursor.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))
    conn.commit()
    conn.close()

# Evidence CRUD
def get_evidence_by_case(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evidence WHERE case_id = ? ORDER BY collection_date DESC", (case_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_evidence():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evidence ORDER BY collection_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_evidence(evidence_id, case_id, evidence_type, description, source_device, serial_number, collection_date, sha256_hash, md5_hash, storage_loc, custody):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO evidence 
        (evidence_id, case_id, evidence_type, description, source_device, serial_number, collection_date, file_hash_sha256, file_hash_md5, storage_location, custody_chain)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (evidence_id, case_id, evidence_type, description, source_device, serial_number, collection_date, sha256_hash, md5_hash, storage_loc, custody)
    )
    conn.commit()
    conn.close()

# Findings CRUD
def get_findings_by_case(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM findings WHERE case_id = ? ORDER BY timestamp DESC", (case_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_findings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM findings ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_finding(case_id, category, artifact_name, description, severity, file_path_location, hash_value, investigator_notes):
    conn = get_connection()
    cursor = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """INSERT INTO findings 
        (case_id, category, artifact_name, description, severity, file_path_location, hash_value, investigator_notes, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (case_id, category, artifact_name, description, severity, file_path_location, hash_value, investigator_notes, ts)
    )
    conn.commit()
    conn.close()

# Audit Log CRUD
def log_action(user, action, details=""):
    conn = get_connection()
    cursor = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO audit_logs (user, action, details, timestamp) VALUES (?, ?, ?, ?)", (user, action, details, ts))
    conn.commit()
    conn.close()

def get_audit_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
