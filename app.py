import http.server
import urllib.parse
import sqlite3
import os
import sys
import html
import io
from datetime import datetime
from http import cookies

PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
DB_FILE = os.path.join(os.path.dirname(__file__), "data", "onit.db")

# Organization and Website Branding
APP_NAME = "onIT"
ORG_NAME = "UC-METC Multipurpose Cooperative"

# Official Accounts: Manager (Issues tickets) and IT (Solves tickets)
INITIAL_USERS = [
    {
        "username": "manager",
        "password": "manager",
        "name": "General Manager",
        "email": "manager@uc-metc.edu.ph",
        "role": "manager",
        "role_title": "Cooperative General Manager",
        "department": "Executive & Cooperative Management"
    },
    {
        "username": "it",
        "password": "it",
        "name": "IT Specialist",
        "email": "it@uc-metc.edu.ph",
        "role": "admin",
        "role_title": "IT Lead & System Developer",
        "department": "UC-METC IT Operations Desk"
    },
    {
        "username": "admin",
        "password": "admin",
        "name": "IT Specialist",
        "email": "it@uc-metc.edu.ph",
        "role": "admin",
        "role_title": "IT Lead & System Developer",
        "department": "UC-METC IT Operations Desk"
    }
]

INITIAL_TICKETS = [
    {
        "id": "TK-104",
        "submitter_name": "General Manager",
        "submitter_email": "manager@uc-metc.edu.ph",
        "submitter_role": "Cooperative General Manager",
        "issue_type": "Password/Login Issue",
        "priority": "Critical",
        "status": "Open",
        "subject": "Cooperative Loan & Savings Portal session timeout during payroll submission",
        "description": "Faculty members and maritime instructors are experiencing immediate session token expiration when attempting to submit dividend and loan verification forms on the cooperative portal. Instructors cannot complete clearance before Friday's deadline.",
        "created_at": "2026-10-04 09:15",
        "timeline": [
            {
                "timestamp": "2026-10-04 09:15",
                "author": "General Manager",
                "role": "Manager",
                "action": "Ticket Issued",
                "content": "Issued priority ticket to IT: Urgent fix needed for cooperative portal session timeout.",
                "is_internal": 0
            },
            {
                "timestamp": "2026-10-04 09:40",
                "author": "IT Specialist",
                "role": "IT Admin",
                "action": "Developer Note",
                "content": "Investigating authentication session expiry in auth_handler.py. Checking Redis session timeout limits for faculty accounts.",
                "is_internal": 1
            }
        ]
    },
    {
        "id": "TK-103",
        "submitter_name": "General Manager",
        "submitter_email": "manager@uc-metc.edu.ph",
        "submitter_role": "Cooperative General Manager",
        "issue_type": "Web Bug/Error",
        "priority": "High",
        "status": "In Progress",
        "subject": "Maritime Bridge Simulator reservation schedule throwing 500 error",
        "description": "When instructors try to generate the simulator slot booking schedule spreadsheet from /reports/export-schedule, the server spins for 15 seconds and returns a 500 Internal Server Error. Need this resolved before cadet practical exams.",
        "created_at": "2026-10-03 14:20",
        "timeline": [
            {
                "timestamp": "2026-10-03 14:20",
                "author": "General Manager",
                "role": "Manager",
                "action": "Ticket Issued",
                "content": "Forwarded faculty concern to IT: Simulator booking report fails to generate.",
                "is_internal": 0
            },
            {
                "timestamp": "2026-10-03 15:05",
                "author": "IT Specialist",
                "role": "IT Admin",
                "action": "Status Changed",
                "content": "Status updated from Open to In Progress.",
                "is_internal": 0
            },
            {
                "timestamp": "2026-10-03 16:30",
                "author": "IT Specialist",
                "role": "IT Admin",
                "action": "Developer Note",
                "content": "Identified memory spike when sanitizing maritime cadet roster special characters. Working on the fix now.",
                "is_internal": 1
            }
        ]
    },
    {
        "id": "TK-102",
        "submitter_name": "General Manager",
        "submitter_email": "manager@uc-metc.edu.ph",
        "submitter_role": "Cooperative General Manager",
        "issue_type": "Content Update",
        "priority": "Low",
        "status": "In Progress",
        "subject": "Update Q4 Cooperative cafeteria meal voucher & uniform allowance notice PDF",
        "description": "Please replace the previous month cafeteria schedule on the cooperative community portal with the revised Q4 voucher guidelines and maritime uniform allowance notice.",
        "created_at": "2026-10-02 11:00",
        "timeline": [
            {
                "timestamp": "2026-10-02 11:00",
                "author": "General Manager",
                "role": "Manager",
                "action": "Ticket Issued",
                "content": "Submitted request for Q4 voucher guidelines and PDF upload to community site.",
                "is_internal": 0
            },
            {
                "timestamp": "2026-10-02 13:10",
                "author": "IT Specialist",
                "role": "IT Admin",
                "action": "Status Changed",
                "content": "Status updated from Open to In Progress.",
                "is_internal": 0
            },
            {
                "timestamp": "2026-10-02 14:00",
                "author": "IT Specialist",
                "role": "IT Admin",
                "action": "Public Update",
                "content": "New PDF documents compressed and uploaded to UC-METC assets storage. Testing mobile download speed.",
                "is_internal": 0
            }
        ]
    },
    {
        "id": "TK-101",
        "submitter_name": "General Manager",
        "submitter_email": "manager@uc-metc.edu.ph",
        "submitter_role": "Cooperative General Manager",
        "issue_type": "New Feature Request",
        "priority": "Medium",
        "status": "Resolved",
        "subject": "Add maritime sea-duty pre-deployment requirement checklist",
        "description": "Our cooperative members and graduating cadets requested a downloadable interactive pre-deployment checklist in the student portal navbar for sea-duty documentation.",
        "created_at": "2026-09-28 10:30",
        "timeline": [
            {
                "timestamp": "2026-09-28 10:30",
                "author": "General Manager",
                "role": "Manager",
                "action": "Ticket Issued",
                "content": "Approved management initiative: Cadet sea-duty interactive checklist.",
                "is_internal": 0
            },
            {
                "timestamp": "2026-09-29 09:00",
                "author": "IT Specialist",
                "role": "IT Admin",
                "action": "Status Changed",
                "content": "Status updated from Open to In Progress.",
                "is_internal": 0
            },
            {
                "timestamp": "2026-10-01 16:45",
                "author": "IT Specialist",
                "role": "IT Admin",
                "action": "Developer Note",
                "content": "Built interactive checklist widget with automated PDF export. Deployed to production.",
                "is_internal": 0
            },
            {
                "timestamp": "2026-10-02 10:00",
                "author": "IT Specialist",
                "role": "IT Admin",
                "action": "Status Changed",
                "content": "Status updated from In Progress to Resolved.",
                "is_internal": 0
            },
            {
                "timestamp": "2026-10-02 10:05",
                "author": "General Manager",
                "role": "Manager",
                "action": "Comment",
                "content": "Verified on management workstation, looks great. Thank you!",
                "is_internal": 0
            }
        ]
    }
]

# ==========================================
# DATABASE LAYER (SQLITE 3)
# ==========================================

def get_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    with conn:
        # Users Table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            role_title TEXT NOT NULL,
            department TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        # Tickets Table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            submitter_name TEXT NOT NULL,
            submitter_email TEXT NOT NULL,
            submitter_role TEXT NOT NULL,
            issue_type TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            submitter_username TEXT
        )
        """)

        # Ticket Timeline & Comments Table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS ticket_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            author TEXT NOT NULL,
            role TEXT NOT NULL,
            action TEXT NOT NULL,
            content TEXT NOT NULL,
            is_internal INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (ticket_id) REFERENCES tickets (id) ON DELETE CASCADE
        )
        """)

        conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timeline_ticket ON ticket_timeline(ticket_id)")

        # Ensure submitter_username column exists in existing SQLite databases
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(tickets)")
        cols = [r["name"] if isinstance(r, sqlite3.Row) else r[1] for r in cursor.fetchall()]
        if "submitter_username" not in cols:
            conn.execute("ALTER TABLE tickets ADD COLUMN submitter_username TEXT")
        
        # Priority 1: Match by submitter full name exactly to user full name
        conn.execute("""
        UPDATE tickets
        SET submitter_username = (
            SELECT username FROM users
            WHERE LOWER(users.name) = LOWER(tickets.submitter_name)
            LIMIT 1
        )
        WHERE submitter_name IN (SELECT name FROM users)
        """)

        # Priority 2: Fallback for any tickets still missing submitter_username by email
        conn.execute("""
        UPDATE tickets
        SET submitter_username = (
            SELECT username FROM users
            WHERE LOWER(users.email) = LOWER(tickets.submitter_email)
            LIMIT 1
        )
        WHERE submitter_username IS NULL OR submitter_username = ''
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_submitter ON tickets(submitter_username)")
        
        # Clean up any automated system dispatch notifications from timeline
        conn.execute("DELETE FROM ticket_timeline WHERE author = 'System Dispatch' OR action = 'Resolution Dispatched'")

        # User Settings & Notification Preferences Table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            username TEXT PRIMARY KEY,
            urgent_alerts INTEGER DEFAULT 1,
            ticket_emails INTEGER DEFAULT 1,
            resolution_updates INTEGER DEFAULT 1,
            daily_summary INTEGER DEFAULT 0
        )
        """)

        # Seed initial users if database is newly initialized
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            for u in INITIAL_USERS:
                conn.execute("""
                INSERT INTO users (username, password, name, email, role, role_title, department, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (u["username"], u["password"], u["name"], u["email"], u["role"], u["role_title"], u["department"], now_str))
        else:
            conn.execute("UPDATE users SET role_title = 'IT Lead & System Developer' WHERE role = 'admin'")

        # Database ready for real tickets created by user
        pass

    conn.close()

def seed_default_tickets(conn):
    for t in INITIAL_TICKETS:
        conn.execute("""
        INSERT INTO tickets (id, submitter_name, submitter_email, submitter_role, issue_type, priority, status, subject, description, created_at, updated_at, submitter_username)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (t["id"], t["submitter_name"], t["submitter_email"], t["submitter_role"], t["issue_type"], t["priority"], t["status"], t["subject"], t["description"], t["created_at"], t["created_at"], "manager"))
        
        for ev in t["timeline"]:
            conn.execute("""
            INSERT INTO ticket_timeline (ticket_id, timestamp, author, role, action, content, is_internal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (t["id"], ev["timestamp"], ev["author"], ev["role"], ev["action"], ev["content"], ev["is_internal"]))

def verify_user_password(stored_password, entered_password):
    if not entered_password:
        return False
    if stored_password == entered_password:
        return True
    # Support initial default credentials and aliases accepted on the login page
    if stored_password in ["it", "it123", "admin", "admin123"] and entered_password in ["it", "it123", "admin", "admin123"]:
        return True
    if stored_password in ["manager", "manager123"] and entered_password in ["manager", "manager123"]:
        return True
    return False

def get_user_by_credentials(username_or_email, password):
    conn = get_db()
    cursor = conn.cursor()
    
    # Allow password match with 'manager' or 'manager123' / 'it' or 'it123' for convenience
    allowed_passwords = [password]
    if password in ["manager", "manager123"]:
        allowed_passwords = ["manager", "manager123"]
    elif password in ["it", "it123", "admin", "admin123"]:
        allowed_passwords = ["it", "it123", "admin", "admin123"]

    placeholders = ",".join(["?"] * len(allowed_passwords))
    query = f"""
    SELECT * FROM users 
    WHERE (LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)) 
      AND password IN ({placeholders})
    """
    params = [username_or_email, username_or_email] + allowed_passwords
    cursor.execute(query, params)
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_username(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_settings(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_settings WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "username": username,
        "urgent_alerts": 1,
        "resolution_updates": 1,
        "daily_summary": 0
    }

def save_user_settings(username, urgent_alerts, resolution_updates, daily_summary):
    conn = get_db()
    with conn:
        conn.execute("""
        INSERT INTO user_settings (username, urgent_alerts, resolution_updates, daily_summary)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            urgent_alerts = excluded.urgent_alerts,
            resolution_updates = excluded.resolution_updates,
            daily_summary = excluded.daily_summary
        """, (username, urgent_alerts, resolution_updates, daily_summary))
    conn.close()

def load_tickets_from_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tickets

def get_ticket_from_db(ticket_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    ticket_row = cursor.fetchone()
    if not ticket_row:
        conn.close()
        return None
    ticket = dict(ticket_row)
    
    cursor.execute("SELECT * FROM ticket_timeline WHERE ticket_id = ? ORDER BY id ASC", (ticket_id,))
    ticket["timeline"] = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return ticket

def format_time_12h(ts_str):
    if not ts_str:
        return ""
    ts_str = str(ts_str).strip()
    if "AM" in ts_str or "PM" in ts_str:
        return ts_str
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(ts_str, fmt)
            return dt.strftime("%Y-%m-%d %I:%M %p")
        except ValueError:
            pass
    return ts_str

def get_now_timestamp_12h():
    return datetime.now().strftime("%Y-%m-%d %I:%M %p")

def insert_ticket(full_name, email, submitter_role, issue_type, priority, subject, description, submitter_username=None, submitter_is_admin=False):
    conn = get_db()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tickets")
        existing_ids = [r["id"] for r in cursor.fetchall()]
        nums = []
        for tid in existing_ids:
            try:
                nums.append(int(tid.replace("TK-", "")))
            except ValueError:
                pass
        next_num = max(nums, default=100) + 1
        new_id = f"TK-{next_num}"
        now_str = get_now_timestamp_12h()

        cursor.execute("""
        INSERT INTO tickets (id, submitter_name, submitter_email, submitter_role, issue_type, priority, status, subject, description, created_at, updated_at, submitter_username)
        VALUES (?, ?, ?, ?, ?, ?, 'Open', ?, ?, ?, ?, ?)
        """, (new_id, full_name, email, submitter_role, issue_type, priority, subject, description, now_str, now_str, submitter_username))

        timeline_role = "IT Specialist" if (submitter_is_admin or "IT" in str(submitter_role)) else "Manager"
        timeline_action = "Ticket Created" if submitter_is_admin else "Ticket Issued"
        timeline_content = f"New ticket logged: {subject}" if submitter_is_admin else f"New ticket issued to IT: {subject}"

        cursor.execute("""
        INSERT INTO ticket_timeline (ticket_id, timestamp, author, role, action, content, is_internal)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (new_id, now_str, full_name, timeline_role, timeline_action, timeline_content))

    conn.close()
    return new_id

def update_ticket_status_db(ticket_id, new_status, author="IT Specialist"):
    conn = get_db()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM tickets WHERE id = ?", (ticket_id,))
        row = cursor.fetchone()
        if row and row["status"] != new_status:
            old_status = row["status"]
            now_str = get_now_timestamp_12h()
            cursor.execute("UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?", (new_status, now_str, ticket_id))
            cursor.execute("""
            INSERT INTO ticket_timeline (ticket_id, timestamp, author, role, action, content, is_internal)
            VALUES (?, ?, ?, 'IT Specialist', 'Status Changed', ?, 0)
            """, (ticket_id, now_str, author, f"Status updated from '{old_status}' to '{new_status}'."))
    conn.close()

def update_ticket_priority_db(ticket_id, new_priority, author="IT Specialist"):
    conn = get_db()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT priority FROM tickets WHERE id = ?", (ticket_id,))
        row = cursor.fetchone()
        if row and row["priority"] != new_priority:
            old_priority = row["priority"]
            now_str = get_now_timestamp_12h()
            cursor.execute("UPDATE tickets SET priority = ?, updated_at = ? WHERE id = ?", (new_priority, now_str, ticket_id))
            cursor.execute("""
            INSERT INTO ticket_timeline (ticket_id, timestamp, author, role, action, content, is_internal)
            VALUES (?, ?, ?, 'IT Specialist', 'Priority Adjusted', ?, 1)
            """, (ticket_id, now_str, author, f"Priority re-classified from '{old_priority}' to '{new_priority}'."))
    conn.close()

def add_ticket_comment_db(ticket_id, author, role_label, action, content, is_internal):
    conn = get_db()
    with conn:
        cursor = conn.cursor()
        now_str = get_now_timestamp_12h()
        cursor.execute("UPDATE tickets SET updated_at = ? WHERE id = ?", (now_str, ticket_id))
        cursor.execute("""
        INSERT INTO ticket_timeline (ticket_id, timestamp, author, role, action, content, is_internal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ticket_id, now_str, author, role_label, action, content, 1 if is_internal else 0))
    conn.close()

def is_ticket_creator(ticket, user):
    if not ticket or not user:
        return False
    sub_user = (ticket.get("submitter_username") or "").strip().lower()
    cur_user = (user.get("username") or "").strip().lower()
    if sub_user and cur_user and sub_user == cur_user:
        return True

    # Fallback for legacy records: match author's display name
    sub_name = (ticket.get("submitter_name") or "").strip().lower()
    cur_name = (user.get("name") or "").strip().lower()
    if sub_name and cur_name and sub_name == cur_name:
        return True

    # Fallback to email only if submitter_username is not set
    sub_email = (ticket.get("submitter_email") or "").strip().lower()
    cur_email = (user.get("email") or "").strip().lower()
    if not sub_user and sub_email and cur_email and sub_email == cur_email:
        return True
    return False

def can_manage_ticket(ticket, user):
    """Strict author-only permission: only the author who created the ticket can edit or delete it. No one else can."""
    return is_ticket_creator(ticket, user)

def update_ticket_content_db(ticket_id, subject, description, issue_type, priority, editor_name="User", editor_role="Author"):
    conn = get_db()
    with conn:
        cursor = conn.cursor()
        now_str = get_now_timestamp_12h()
        cursor.execute("""
        UPDATE tickets
        SET subject = ?, description = ?, issue_type = ?, priority = ?, updated_at = ?
        WHERE id = ?
        """, (subject, description, issue_type, priority, now_str, ticket_id))

        cursor.execute("""
        INSERT INTO ticket_timeline (ticket_id, timestamp, author, role, action, content, is_internal)
        VALUES (?, ?, ?, ?, 'Ticket Edited', 'Ticket details (subject, description, or category/priority) were updated by the creator.', 0)
        """, (ticket_id, now_str, editor_name, editor_role))
    conn.close()

def delete_ticket_db(ticket_id):
    conn = get_db()
    with conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ticket_timeline WHERE ticket_id = ?", (ticket_id,))
        cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    conn.close()

def reset_db_data():
    conn = get_db()
    with conn:
        conn.execute("DELETE FROM ticket_timeline")
        conn.execute("DELETE FROM tickets")
        seed_default_tickets(conn)
    conn.close()

def compute_metrics(tickets):
    total = len(tickets)
    open_c = sum(1 for t in tickets if t["status"] == "Open")
    in_prog = sum(1 for t in tickets if t["status"] == "In Progress")
    resolved = sum(1 for t in tickets if t["status"] == "Resolved")
    closed = sum(1 for t in tickets if t["status"] == "Closed")
    critical = sum(1 for t in tickets if t["priority"] == "Critical" and t["status"] in ["Open", "In Progress"])
    return {
        "total": total,
        "active": open_c + in_prog,
        "open": open_c,
        "in_progress": in_prog,
        "resolved": resolved,
        "closed": closed,
        "critical": critical
    }

def get_status_badge(status):
    if status == "Open":
        return '<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200"><span class="w-1.5 h-1.5 rounded-full bg-blue-600"></span><span>Open</span></span>'
    elif status == "In Progress":
        return '<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200"><span class="w-1.5 h-1.5 rounded-full bg-amber-600 animate-pulse"></span><span>In Progress</span></span>'
    elif status == "Resolved":
        return '<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200"><i data-lucide="check" class="w-3.5 h-3.5"></i><span>Resolved</span></span>'
    else:
        return '<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200"><span>Closed</span></span>'

def get_priority_badge(priority):
    if priority == "Critical":
        return '<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300"><span class="w-2 h-2 rounded-full bg-rose-600 animate-pulse"></span><span>Critical</span></span>'
    elif priority == "High":
        return '<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-orange-50 text-orange-700 border border-orange-200">High</span>'
    elif priority == "Medium":
        return '<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">Medium</span>'
    else:
        return '<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">Low</span>'

def get_issue_badge(issue_type):
    if issue_type == "Web Bug/Error":
        return '<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200"><i data-lucide="bug" class="w-3.5 h-3.5"></i><span>Web Bug/Error</span></span>'
    elif issue_type == "New Feature Request":
        return '<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-purple-50 text-purple-700 border border-purple-200"><i data-lucide="sparkles" class="w-3.5 h-3.5"></i><span>New Feature Request</span></span>'
    elif issue_type == "Content Update":
        return '<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-cyan-50 text-cyan-700 border border-cyan-200"><i data-lucide="file-text" class="w-3.5 h-3.5"></i><span>Content Update</span></span>'
    else:
        return '<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200"><i data-lucide="key-round" class="w-3.5 h-3.5"></i><span>Password/Login</span></span>'

def get_onit_logo_svg(size=40, extra_class=""):
    uid = f"onit_{size}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}" class="{extra_class} shrink-0 select-none">
  <defs>
    <linearGradient id="bg_{uid}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#9333ea" />
      <stop offset="50%" stop-color="#7e22ce" />
      <stop offset="100%" stop-color="#4c1d95" />
    </linearGradient>
    <linearGradient id="glow_{uid}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.45" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.0" />
    </linearGradient>
    <linearGradient id="beam_{uid}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#e9d5ff" />
      <stop offset="100%" stop-color="#ffffff" />
    </linearGradient>
    <filter id="shadow_{uid}" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="0" dy="3.5" stdDeviation="4" flood-color="#3b0764" flood-opacity="0.32" />
    </filter>
  </defs>
  <!-- Modern Ticket Silhouette with Notched Edges -->
  <path d="M 22 8 H 78 Q 92 8 92 22 V 38 A 12 12 0 0 0 92 62 V 78 Q 92 92 78 92 H 22 Q 8 92 8 78 V 62 A 12 12 0 0 0 8 38 V 22 Q 8 8 22 8 Z"
        fill="url(#bg_{uid})" filter="url(#shadow_{uid})" />
  <!-- Gloss Top Highlight -->
  <path d="M 22 9.5 H 78 Q 90.5 9.5 90.5 22 V 38" fill="none" stroke="url(#glow_{uid})" stroke-width="2" stroke-linecap="round" />
  <!-- Perforation Guide Accent Dots -->
  <circle cx="8" cy="50" r="1.5" fill="#c084fc" opacity="0.6" />
  <circle cx="92" cy="50" r="1.5" fill="#c084fc" opacity="0.6" />
  <!-- Illuminated Power 'ON' Tech Emblem -->
  <path d="M 66 37 A 22 22 0 1 1 34 37" fill="none" stroke="#ffffff" stroke-width="6.5" stroke-linecap="round" />
  <line x1="50" y1="21" x2="50" y2="45" stroke="url(#beam_{uid})" stroke-width="6.5" stroke-linecap="round" />
  <!-- Core Active Tech Pulse Node -->
  <circle cx="50" cy="57" r="3.5" fill="#e9d5ff" />
</svg>"""

# ==========================================
# CLEAN LOGIN PAGE (NO DEMO BUTTONS)
# ==========================================

def render_login_page(error_msg=None):
    err_box = ""
    if error_msg:
        err_box = f"""
        <div class="mb-5 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold flex items-center gap-2">
          <i data-lucide="alert-circle" class="w-4 h-4 text-rose-600 shrink-0"></i>
          <span>{html.escape(error_msg)}</span>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html lang="en" class="h-full bg-slate-100/70 antialiased">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sign In | onIT &bull; UC-METC Multipurpose Cooperative</title>
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%239333ea'/%3E%3Cstop offset='100%25' stop-color='%234c1d95'/%3E%3C/linearGradient%3E%3C/defs%3E%3Cpath d='M 22 8 H 78 Q 92 8 92 22 V 38 A 12 12 0 0 0 92 62 V 78 Q 92 92 78 92 H 22 Q 8 92 8 78 V 62 A 12 12 0 0 0 8 38 V 22 Q 8 8 22 8 Z' fill='url(%23g)'/%3E%3Cpath d='M 66 37 A 22 22 0 1 1 34 37' fill='none' stroke='%23ffffff' stroke-width='7' stroke-linecap='round'/%3E%3Cline x1='50' y1='21' x2='50' y2='45' stroke='%23ffffff' stroke-width='7' stroke-linecap='round'/%3E%3Ccircle cx='50' cy='57' r='4' fill='%23e9d5ff'/%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    .input-field {{
      transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
    }}
    .input-field:hover {{
      border-color: #a855f7;
      background-color: #ffffff;
    }}
    .input-field:focus {{
      border-color: #7e22ce;
      background-color: #ffffff;
      box-shadow: 0 0 0 3px rgba(126, 34, 206, 0.15);
      outline: none;
    }}
    .input-group:focus-within .input-icon {{
      color: #7e22ce;
    }}
    .input-group:hover .input-icon {{
      color: #a855f7;
    }}
    .input-icon {{
      transition: color 0.2s ease;
    }}
    .custom-checkbox input:checked + .checkbox-box {{
      background-color: #7e22ce;
      border-color: #7e22ce;
    }}
    .custom-checkbox input:checked + .checkbox-box svg {{
      opacity: 1;
      transform: scale(1);
    }}
    .custom-checkbox:hover .checkbox-box {{
      border-color: #a855f7;
      transform: scale(1.08);
    }}
    .custom-checkbox:active .checkbox-box {{
      transform: scale(0.95);
    }}
  </style>
</head>
<body class="min-h-full flex items-center justify-center p-4 sm:p-6 bg-slate-100/70 text-slate-800 selection:bg-purple-700 selection:text-white">

  <div class="w-full max-w-md">
    
    <!-- onIT BRAND LOGO & HEADER (BRIGHT THEME) -->
    <div class="text-center mb-8">
      <div class="inline-flex items-center justify-center gap-2 px-3.5 py-1.5 rounded-full bg-purple-50 border border-purple-200 mb-3 shadow-sm">
        <span class="w-2 h-2 rounded-full bg-purple-600"></span>
        <span class="text-xs font-bold uppercase tracking-wider text-purple-700">{ORG_NAME}</span>
      </div>

      <div class="flex items-center justify-center gap-3.5 my-3">
        <div class="transition-transform hover:scale-105 duration-200">
          {get_onit_logo_svg(52)}
        </div>
        <div class="text-left">
          <h1 class="text-4xl font-black tracking-tight text-slate-900 leading-none">
            on<span class="text-purple-700">IT</span>
          </h1>
          <p class="text-[11px] font-bold text-slate-500 uppercase tracking-widest mt-1">Ticketing Desk</p>
        </div>
      </div>

      <p class="text-xs text-slate-500 mt-2.5 max-w-xs mx-auto">
        Sign in to access your cooperative management desk or IT operations console.
      </p>
    </div>

    <!-- CLEAN BRIGHT LOGIN CARD -->
    <div class="bg-white rounded-3xl p-7 sm:p-9 shadow-xl shadow-slate-200/80 text-slate-800 border border-slate-200/90">
      {err_box}

      <form action="/login" method="POST" id="loginForm" class="space-y-4">
        <div>
          <label for="username" class="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
            Username
          </label>
          <div class="relative input-group">
            <i data-lucide="user" class="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 input-icon pointer-events-none"></i>
            <input type="text" id="username" name="username" required autofocus placeholder="Enter your username"
                   class="input-field w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-50 text-slate-900 font-medium">
          </div>
        </div>

        <div>
          <label for="password" class="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
            Password
          </label>
          <div class="relative input-group">
            <i data-lucide="lock" class="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 input-icon pointer-events-none"></i>
            <input type="password" id="password" name="password" required placeholder="Enter your password"
                   class="input-field w-full pl-10 pr-11 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-50 text-slate-900 font-medium">
            <button type="button" id="togglePwdBtn" onclick="togglePasswordVisibility()" title="Show/Hide password"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-purple-700 transition-colors p-1 rounded-lg cursor-pointer focus:outline-none">
              <i data-lucide="eye" id="togglePwdIcon" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

        <!-- Remember Me Checkbox -->
        <div class="flex items-center pt-1.5 pb-0.5">
          <label class="custom-checkbox inline-flex items-center gap-2.5 cursor-pointer select-none group">
            <input type="checkbox" id="rememberMe" name="remember" class="sr-only">
            <div class="checkbox-box w-4 h-4 rounded border-2 border-slate-300 bg-slate-50 flex items-center justify-center transition-all duration-200">
              <svg class="w-2.5 h-2.5 text-white stroke-[3.5] opacity-0 transition-all duration-200 transform scale-50" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <span class="text-xs font-semibold text-slate-600 group-hover:text-purple-900 transition-colors">Remember me</span>
          </label>
        </div>

        <div class="pt-2">
          <button type="submit" class="w-full py-3.5 rounded-xl bg-purple-700 hover:bg-purple-800 text-white font-bold text-sm shadow-md shadow-purple-900/20 hover:shadow-lg hover:shadow-purple-900/30 transition-all flex items-center justify-center gap-2 cursor-pointer">
            <span>Sign In to onIT</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
        </div>
      </form>

      <div class="mt-6 pt-5 border-t border-slate-100 flex items-center justify-center">
        <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200/80 text-emerald-700 text-xs font-semibold shadow-xs">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span>All Systems Operational &bull; IT Desk Ready</span>
        </div>
      </div>
    </div>

    <!-- FOOTER -->
    <div class="text-center text-slate-400 text-xs mt-6">
      <p>{ORG_NAME} &bull; Internal IT Operations</p>
    </div>

  </div>

  <script>
    lucide.createIcons();

    function togglePasswordVisibility() {{
      const pwd = document.getElementById('password');
      const icon = document.getElementById('togglePwdIcon');
      if (pwd.type === 'password') {{
        pwd.type = 'text';
        icon.setAttribute('data-lucide', 'eye-off');
      }} else {{
        pwd.type = 'password';
        icon.setAttribute('data-lucide', 'eye');
      }}
      lucide.createIcons();
    }}

    // Load saved credentials if remembered
    document.addEventListener('DOMContentLoaded', function() {{
      const savedUser = localStorage.getItem('onit_remember_username');
      const savedPass = localStorage.getItem('onit_remember_password');
      const rememberCheckbox = document.getElementById('rememberMe');
      const userInput = document.getElementById('username');
      const passInput = document.getElementById('password');

      if (savedUser) {{
        userInput.value = savedUser;
        if (rememberCheckbox) rememberCheckbox.checked = true;
      }}
      if (savedPass) {{
        passInput.value = savedPass;
      }}
    }});

    // Save or clear credentials on submit
    const form = document.getElementById('loginForm');
    if (form) {{
      form.addEventListener('submit', function() {{
        const rememberCheckbox = document.getElementById('rememberMe');
        const userInput = document.getElementById('username');
        const passInput = document.getElementById('password');

        if (rememberCheckbox && rememberCheckbox.checked) {{
          localStorage.setItem('onit_remember_username', userInput.value);
          localStorage.setItem('onit_remember_password', passInput.value);
        }} else {{
          localStorage.removeItem('onit_remember_username');
          localStorage.removeItem('onit_remember_password');
        }}
      }});
    }}
  </script>
</body>
</html>"""

def render_layout(title, content, user=None, flash_msg=None, flash_type="success", modal_html=""):
    if isinstance(content, tuple):
        content, extracted_modal = content
        if not modal_html:
            modal_html = extracted_modal

    is_admin = (user and user.get("role") == "admin")
    
    flash_html = ""
    if flash_msg:
        border_col = "border-emerald-200 bg-emerald-50 text-emerald-800" if flash_type == "success" else "border-rose-200 bg-rose-50 text-rose-800"
        flash_html = f"""
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4 w-full">
          <div class="flex items-center justify-between p-4 rounded-xl border text-sm font-medium {border_col} shadow-sm">
            <div class="flex items-center gap-3">
              <i data-lucide="check-circle" class="w-5 h-5 shrink-0"></i>
              <span>{html.escape(flash_msg)}</span>
            </div>
            <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-slate-600 p-1">&times;</button>
          </div>
        </div>
        """

    user_name = html.escape(user["name"]) if user else "Guest"
    user_role_label = user.get("role_title", "User") if user else ""
    avatar_char = user["name"][0] if user else "U"

    user_badge = f"""
    <div class="flex items-center gap-1.5 sm:gap-2.5 bg-slate-100/90 pl-1.5 sm:pl-2 pr-2 sm:pr-2.5 py-1 sm:py-1.5 rounded-2xl border border-slate-200 shadow-inner shrink-0">
      <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl {'bg-purple-900 text-purple-200' if is_admin else 'bg-purple-700 text-white'} flex items-center justify-center font-bold text-xs shadow-sm shrink-0">
        {avatar_char}
      </div>
      <div class="text-left hidden md:block">
        <p class="text-xs font-bold text-slate-800 leading-tight">{user_name}</p>
        <p class="text-[10px] text-slate-500 font-medium">{user_role_label}</p>
      </div>
      <a href="/settings" class="p-1 sm:p-1.5 rounded-lg text-slate-400 hover:text-purple-700 hover:bg-purple-50 transition-colors" title="Account & System Settings">
        <i data-lucide="settings" class="w-3.5 h-3.5 sm:w-4 sm:h-4"></i>
      </a>
      <a href="/logout" class="p-1 sm:p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors" title="Sign Out">
        <i data-lucide="log-out" class="w-3.5 h-3.5 sm:w-4 sm:h-4"></i>
      </a>
    </div>
    """

    action_btn = ""

    return f"""<!DOCTYPE html>
<html lang="en" class="h-full bg-slate-50 antialiased">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' stop-color='%239333ea'/%3E%3Cstop offset='100%25' stop-color='%234c1d95'/%3E%3C/linearGradient%3E%3C/defs%3E%3Cpath d='M 22 8 H 78 Q 92 8 92 22 V 38 A 12 12 0 0 0 92 62 V 78 Q 92 92 78 92 H 22 Q 8 92 8 78 V 62 A 12 12 0 0 0 8 38 V 22 Q 8 8 22 8 Z' fill='url(%23g)'/%3E%3Cpath d='M 66 37 A 22 22 0 1 1 34 37' fill='none' stroke='%23ffffff' stroke-width='7' stroke-linecap='round'/%3E%3Cline x1='50' y1='21' x2='50' y2='45' stroke='%23ffffff' stroke-width='7' stroke-linecap='round'/%3E%3Ccircle cx='50' cy='57' r='4' fill='%23e9d5ff'/%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    code, pre, .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #f1f5f9; }}
    ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 9999px; }}

    @keyframes entranceDown {{
      0% {{
        opacity: 0;
        transform: translateY(-14px);
      }}
      100% {{
        opacity: 1;
        transform: none;
      }}
    }}
    @keyframes entranceUp {{
      0% {{
        opacity: 0;
        transform: translateY(18px);
      }}
      100% {{
        opacity: 1;
        transform: none;
      }}
    }}
    .animate-entrance-1 {{
      animation: entranceDown 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}
    .animate-entrance-2 {{
      animation: entranceUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.08s both;
    }}
    .animate-entrance-3 {{
      animation: entranceUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.16s both;
    }}
    .animate-entrance-4 {{
      animation: entranceUp 0.55s cubic-bezier(0.16, 1, 0.3, 1) 0.24s both;
    }}
    @keyframes pageEntrance {{
      0% {{
        opacity: 0;
        transform: translateY(12px);
      }}
      100% {{
        opacity: 1;
        transform: none;
      }}
    }}
    .animate-page-entrance {{
      animation: pageEntrance 0.35s cubic-bezier(0.16, 1, 0.3, 1) both;
    }}

    /* Custom Animated Dropdown Component */
    .custom-dropdown-container {{
      position: relative;
      display: inline-block;
      width: 100%;
      user-select: none;
      z-index: 20;
    }}
    .custom-dropdown-container.open {{
      z-index: 99999 !important;
    }}
    .custom-dropdown-trigger {{
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: space-between;
      text-align: left;
      cursor: pointer;
      outline: none;
      transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
    }}
    .custom-dropdown-trigger:hover {{
      border-color: #a855f7 !important;
    }}
    .custom-dropdown-container.open .custom-dropdown-trigger {{
      border-color: #7e22ce !important;
      box-shadow: 0 0 0 3px rgba(126, 34, 206, 0.15) !important;
    }}
    .custom-dropdown-arrow {{
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), color 0.2s ease;
    }}
    .custom-dropdown-container.open .custom-dropdown-arrow {{
      transform: rotate(180deg);
      color: #7e22ce;
    }}

    /* Animated Dropdown Menu List (Higher z-index to float over cards) */
    .custom-dropdown-menu {{
      position: absolute;
      top: calc(100% + 5px);
      left: 0;
      right: 0;
      z-index: 99999 !important;
      border-radius: 0.85rem;
      padding: 0.35rem;
      box-shadow: 0 16px 36px -4px rgba(15, 23, 42, 0.18), 0 6px 16px -2px rgba(15, 23, 42, 0.08);
      transform-origin: top center;
      opacity: 0;
      transform: translateY(-8px) scale(0.98);
      pointer-events: none;
      visibility: hidden;
      transition: opacity 0.18s cubic-bezier(0.16, 1, 0.3, 1),
                  transform 0.18s cubic-bezier(0.16, 1, 0.3, 1),
                  visibility 0.18s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .custom-dropdown-container.open .custom-dropdown-menu {{
      opacity: 1;
      transform: translateY(0) scale(1);
      pointer-events: auto;
      visibility: visible;
    }}
    .custom-dropdown-item {{
      border-radius: 0.55rem;
      padding: 0.5rem 0.75rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      transition: background-color 0.15s ease, color 0.15s ease;
    }}

    /* Textbox and Textarea Animations (Identical to Login Page) */
    .input-field,
    input[type="text"],
    input[type="search"],
    textarea {{
      transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease !important;
      outline: none !important;
    }}
    .input-field:hover,
    input[type="text"]:hover,
    input[type="search"]:hover,
    textarea:hover {{
      border-color: #a855f7 !important;
      background-color: #ffffff !important;
    }}
    .input-field:focus,
    input[type="text"]:focus,
    input[type="search"]:focus,
    textarea:focus {{
      border-color: #7e22ce !important;
      background-color: #ffffff !important;
      box-shadow: 0 0 0 3px rgba(126, 34, 206, 0.15) !important;
      outline: none !important;
    }}

    /* Toggle Switch Styles */
    .toggle-switch {{
      position: relative;
      display: inline-flex;
      align-items: center;
      cursor: pointer;
    }}
    .toggle-switch input {{
      position: absolute;
      opacity: 0;
      width: 0;
      height: 0;
    }}
    .toggle-slider {{
      width: 2.75rem;
      height: 1.5rem;
      background-color: #cbd5e1;
      border-radius: 9999px;
      transition: background-color 0.2s ease;
      position: relative;
    }}
    .toggle-slider::after {{
      content: '';
      position: absolute;
      top: 2px;
      left: 2px;
      width: 1.25rem;
      height: 1.25rem;
      background-color: white;
      border-radius: 9999px;
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }}
    .toggle-switch input:checked + .toggle-slider {{
      background-color: #7e22ce;
    }}
    .toggle-switch input:checked + .toggle-slider::after {{
      transform: translateX(1.25rem);
    }}
  </style>
</head>
<body class="min-h-full flex flex-col text-slate-800 selection:bg-purple-700 selection:text-white">

  <!-- TOP HEADER WITH onIT SOLID PURPLE BRANDING & USER PROFILE -->
  <header class="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-sm transition-all">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16 sm:h-20 gap-2">
        
        <!-- onIT Brand Logo (Bespoke Ticket & Power Emblem) -->
        <a href="/" class="flex items-center gap-2 sm:gap-3 group shrink-0 min-w-0">
          <div class="transition-transform duration-200 group-hover:scale-105 shrink-0">
            {get_onit_logo_svg(36, "sm:hidden")}
            {get_onit_logo_svg(42, "hidden sm:block")}
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-1.5 sm:gap-2">
              <span class="font-black text-lg sm:text-xl tracking-tight text-slate-900 group-hover:text-purple-700 transition-colors">
                on<span class="text-purple-700">IT</span>
              </span>
              <span class="hidden sm:inline-flex text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 whitespace-nowrap">
                {ORG_NAME}
              </span>
              <span class="inline-flex sm:hidden text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-md bg-purple-50 text-purple-700 border border-purple-200 whitespace-nowrap">
                UC-METC
              </span>
            </div>
            <p class="text-[11px] sm:text-xs text-slate-500 font-medium whitespace-nowrap">
              IT Helpdesk <span class="hidden sm:inline">&bull; Operations & Triage</span>
            </p>
          </div>
        </a>

        <!-- Right Side: User Profile -->
        <div class="flex items-center gap-2 sm:gap-4 shrink-0">
          {user_badge}
        </div>

      </div>
    </div>
  </header>

  {flash_html}

  <main class="animate-page-entrance flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
    {content}
  </main>

  <footer class="bg-white border-t border-slate-200 py-6 mt-12 text-slate-500 text-xs">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-2.5">
        {get_onit_logo_svg(20)}
        <span><strong>onIT</strong> &bull; Official IT Helpdesk of {ORG_NAME}</span>
      </div>
      <div>
        <span>&copy; {datetime.now().year} {ORG_NAME}. All rights reserved.</span>
      </div>
    </div>
  </footer>

  {modal_html}

  <script>
    lucide.createIcons();

    // Universal Animated Custom Dropdowns
    function initCustomDropdowns() {{
      document.querySelectorAll('select').forEach(function(select) {{
        if (select.dataset.customized === 'true') return;
        select.dataset.customized = 'true';

        // Keep select in DOM for native form submission, but hide visually
        select.style.display = 'none';

        var isDark = select.classList.contains('dark-select') || select.closest('.bg-slate-900, .bg-slate-800');
        var isCompact = select.classList.contains('text-xs') && select.classList.contains('px-2.5');

        var container = document.createElement('div');
        container.className = 'custom-dropdown-container';
        if (select.className.includes('flex-1')) container.classList.add('flex-1');

        var currentOption = select.options[select.selectedIndex] || select.options[0];
        var currentText = currentOption ? currentOption.text : 'Select...';

        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'custom-dropdown-trigger ' +
          (isDark
            ? 'bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2 text-xs font-bold'
            : (isCompact
                ? 'bg-white border border-slate-200 text-slate-800 rounded-lg px-2.5 py-1 text-xs font-bold'
                : 'bg-white border border-slate-200 text-slate-700 rounded-xl px-3 py-2 text-xs sm:text-sm font-medium'
              )
          );

        var labelSpan = document.createElement('span');
        labelSpan.className = 'truncate pr-2';
        labelSpan.textContent = currentText;

        var arrow = document.createElement('span');
        arrow.className = 'custom-dropdown-arrow shrink-0 text-slate-400 flex items-center';
        arrow.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>';

        btn.appendChild(labelSpan);
        btn.appendChild(arrow);

        var menu = document.createElement('div');
        menu.className = 'custom-dropdown-menu max-h-60 overflow-y-auto ' +
          (isDark
            ? 'bg-slate-900 border border-slate-700 text-white'
            : 'bg-white border border-slate-200 text-slate-700'
          );

        Array.from(select.options).forEach(function(opt) {{
          var item = document.createElement('div');
          item.className = 'custom-dropdown-item text-xs sm:text-sm ' +
            (isDark
              ? 'hover:bg-slate-800 hover:text-purple-300'
              : 'hover:bg-purple-50 hover:text-purple-700'
            ) +
            (opt.selected
              ? (isDark ? ' bg-slate-800/80 text-purple-300 font-bold' : ' bg-purple-50 text-purple-700 font-bold')
              : ''
            );

          var itemLabel = document.createElement('span');
          itemLabel.textContent = opt.text;
          item.appendChild(itemLabel);

          if (opt.selected) {{
            var check = document.createElement('span');
            check.className = 'text-purple-600 text-xs shrink-0 ml-2 checkmark-icon';
            check.innerHTML = '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></polyline></svg>';
            item.appendChild(check);
          }}

          item.addEventListener('click', function(e) {{
            e.stopPropagation();
            select.value = opt.value;
            labelSpan.textContent = opt.text;

            menu.querySelectorAll('.custom-dropdown-item').forEach(function(it) {{
              it.classList.remove('bg-purple-50', 'bg-slate-800/80', 'text-purple-700', 'text-purple-300', 'font-bold');
              var ch = it.querySelector('.checkmark-icon');
              if (ch) ch.remove();
            }});
            item.classList.add(isDark ? 'bg-slate-800/80' : 'bg-purple-50', isDark ? 'text-purple-300' : 'text-purple-700', 'font-bold');
            var newCheck = document.createElement('span');
            newCheck.className = 'text-purple-600 text-xs shrink-0 ml-2 checkmark-icon';
            newCheck.innerHTML = '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></polyline></svg>';
            item.appendChild(newCheck);

            container.classList.remove('open');

            select.dispatchEvent(new Event('change', {{ bubbles: true }}));
            if (select.form && select.getAttribute('onchange') && select.getAttribute('onchange').includes('submit')) {{
              select.form.submit();
            }}
          }});

          menu.appendChild(item);
        }});

        btn.addEventListener('click', function(e) {{
          e.stopPropagation();
          var wasOpen = container.classList.contains('open');
          document.querySelectorAll('.custom-dropdown-container.open').forEach(function(c) {{
            if (c !== container) {{
              c.classList.remove('open');
              var card = c.closest('.animate-entrance-3, form');
              if (card) card.style.zIndex = '';
            }}
          }});
          var parentCard = container.closest('.animate-entrance-3, form');
          if (wasOpen) {{
            container.classList.remove('open');
            if (parentCard) parentCard.style.zIndex = '';
          }} else {{
            container.classList.add('open');
            if (parentCard) parentCard.style.zIndex = '50';
          }}
        }});

        container.appendChild(btn);
        container.appendChild(menu);
        select.parentNode.insertBefore(container, select.nextSibling);

        var siblingIcon = select.parentNode.querySelector('.select-chevron, i[data-lucide="chevron-down"]');
        if (siblingIcon) {{
          siblingIcon.style.display = 'none';
        }}
      }});
    }}

    document.addEventListener('click', function() {{
      document.querySelectorAll('.custom-dropdown-container.open').forEach(function(c) {{
        c.classList.remove('open');
        var card = c.closest('.animate-entrance-3, form');
        if (card) card.style.zIndex = '';
      }});
    }});

    document.addEventListener('keydown', function(e) {{
      if (e.key === 'Escape') {{
        document.querySelectorAll('.custom-dropdown-container.open').forEach(function(c) {{
          c.classList.remove('open');
          var card = c.closest('.animate-entrance-3, form');
          if (card) card.style.zIndex = '';
        }});
        var delModal = document.getElementById('deleteModal');
        if (delModal) delModal.classList.add('hidden');
      }}
    }});

    function togglePasswordVisibilityField(inputId, iconId) {{
      var pwd = document.getElementById(inputId);
      var icon = document.getElementById(iconId);
      if (!pwd || !icon) return;
      if (pwd.type === 'password') {{
        pwd.type = 'text';
        icon.setAttribute('data-lucide', 'eye-off');
      }} else {{
        pwd.type = 'password';
        icon.setAttribute('data-lucide', 'eye');
      }}
      lucide.createIcons();
    }}

    function hoistModals() {{
      document.querySelectorAll('#deleteModal, [id$="Modal"]').forEach(function(m) {{
        if (m.parentElement && m.parentElement !== document.body) {{
          document.body.appendChild(m);
        }}
      }});
    }}

    function openDeleteModal() {{
      var m = document.getElementById('deleteModal');
      if (m) {{
        if (m.parentElement !== document.body) {{
          document.body.appendChild(m);
        }}
        m.classList.remove('hidden');
        m.style.display = 'flex';
      }}
    }}

    function closeDeleteModal() {{
      var m = document.getElementById('deleteModal');
      if (m) {{
        m.classList.add('hidden');
        m.style.display = 'none';
      }}
    }}

    document.addEventListener('DOMContentLoaded', function() {{
      initCustomDropdowns();
      hoistModals();
    }});
    initCustomDropdowns();
    hoistModals();
  </script>
</body>
</html>"""

# ==========================================
# MANAGER PORTAL (ISSUES TICKETS TO IT)
# ==========================================

def render_manager_dashboard(tickets, user, search_q=""):
    metrics = compute_metrics(tickets)
    
    rows = []
    filtered = tickets
    if search_q:
        q = search_q.lower()
        filtered = [t for t in filtered if q in t["id"].lower() or q in t["subject"].lower() or q in t["description"].lower() or q in t["submitter_name"].lower()]

    for t in filtered:
        is_mine = is_ticket_creator(t, user)
        mine_tag = '<span class="inline-flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200">Yours</span>' if is_mine else ''
        quick_actions = f'''<a href="/edit-ticket?id={t['id']}" onclick="event.stopPropagation()" class="p-1 rounded text-slate-400 hover:text-purple-700 hover:bg-purple-100 transition-colors" title="Edit your ticket"><i data-lucide="edit-3" class="w-3.5 h-3.5"></i></a>''' if is_mine else ''
        rows.append(f"""
        <tr class="hover:bg-purple-50/40 transition-colors cursor-pointer group" onclick="window.location='/ticket?id={t['id']}'">
          <td class="px-5 py-4 whitespace-nowrap">
            <div class="flex items-center gap-1.5">
              <span class="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-200 group-hover:border-purple-300 group-hover:bg-purple-50 group-hover:text-purple-700 transition-colors">
                {html.escape(t['id'])}
              </span>
              {mine_tag}
            </div>
          </td>
          <td class="px-5 py-4 whitespace-nowrap text-xs text-slate-500 font-mono">{format_time_12h(t['created_at'])}</td>
          <td class="px-5 py-4">
            <div class="max-w-md">
              <p class="font-semibold text-slate-900 group-hover:text-purple-700 transition-colors text-sm line-clamp-1">{html.escape(t['subject'])}</p>
              <p class="text-xs text-slate-400 mt-0.5 line-clamp-1">Issued by {html.escape(t['submitter_name'])} &bull; {html.escape(t['submitter_role'])}</p>
            </div>
          </td>
          <td class="px-5 py-4 whitespace-nowrap">{get_issue_badge(t['issue_type'])}</td>
          <td class="px-5 py-4 whitespace-nowrap">{get_priority_badge(t['priority'])}</td>
          <td class="px-5 py-4 whitespace-nowrap">{get_status_badge(t['status'])}</td>
          <td class="px-5 py-4 whitespace-nowrap text-right text-xs">
            <div class="flex items-center justify-end gap-2">
              {quick_actions}
              <span class="text-purple-700 font-semibold group-hover:translate-x-1 inline-flex items-center gap-1 transition-transform">
                <span>Track</span>
                <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
              </span>
            </div>
          </td>
        </tr>
        """)

    table_body = "\n".join(rows) if rows else """
    <tr>
      <td colspan="7" class="px-6 py-12 text-center text-slate-500">
        <p class="font-semibold text-slate-800 text-sm">No tickets found</p>
        <p class="text-xs text-slate-500 mt-1">Issue a new ticket to assign work to IT.</p>
      </td>
    </tr>
    """

    return f"""
    <div class="space-y-8">
      <!-- HERO BANNER (SOLID PURPLE) -->
      <div class="animate-entrance-1 relative overflow-hidden rounded-3xl bg-purple-700 p-6 sm:p-8 text-white shadow-xl shadow-purple-950/10">
        <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div class="space-y-2 max-w-2xl">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-800/90 text-xs font-semibold text-purple-100 border border-purple-500/40">
              <span class="w-2 h-2 rounded-full bg-purple-300"></span>
              <span>Management Portal &bull; {ORG_NAME}</span>
            </div>
            <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Welcome back, {html.escape(user['name'])}! 👋
            </h1>
            <p class="text-purple-100 text-sm sm:text-base leading-relaxed">
              Issue operational tickets, website bug reports, and cooperative priorities directly to your <strong>IT Specialist</strong>. Track resolution progress in real time.
            </p>
          </div>
          <div>
            <a href="/submit" class="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-white text-purple-800 hover:bg-purple-50 font-bold text-sm shadow-md hover:shadow-lg transition-all transform hover:-translate-y-0.5">
              <i data-lucide="plus-circle" class="w-5 h-5 text-purple-700"></i>
              <span>Issue New Ticket</span>
            </a>
          </div>
        </div>
      </div>

      <!-- METRICS CARDS -->
      <div class="animate-entrance-2 grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow">
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-500">Total Issued</p>
          <p class="text-3xl font-extrabold text-slate-900 mt-1">{metrics['total']}</p>
          <p class="text-xs text-slate-400 mt-1">Management requests</p>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-blue-200/80 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden">
          <div class="absolute top-0 left-0 right-0 h-1 bg-blue-500"></div>
          <p class="text-xs font-semibold uppercase tracking-wider text-blue-700">Pending IT Resolution</p>
          <p class="text-3xl font-extrabold text-blue-900 mt-1">{metrics['open'] + metrics['in_progress']}</p>
          <div class="flex items-center gap-2 mt-1 text-xs text-blue-600">
            <span>{metrics['open']} Open</span>
            <span>&bull;</span>
            <span>{metrics['in_progress']} In Progress</span>
          </div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-emerald-200/80 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden">
          <div class="absolute top-0 left-0 right-0 h-1 bg-emerald-500"></div>
          <p class="text-xs font-semibold uppercase tracking-wider text-emerald-700">Completed & Verified</p>
          <p class="text-3xl font-extrabold text-emerald-900 mt-1">{metrics['resolved'] + metrics['closed']}</p>
          <p class="text-xs text-emerald-600 mt-1">Resolved by IT</p>
        </div>
      </div>

      <!-- MY TICKETS TABLE -->
      <div class="animate-entrance-3 bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div class="p-5 sm:p-6 border-b border-slate-200/80 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 bg-slate-50/50">
          <div>
            <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2">
              <i data-lucide="clipboard-list" class="w-5 h-5 text-purple-700"></i>
              <span>Management Issued Tickets Queue</span>
            </h2>
            <p class="text-xs text-slate-500 mt-0.5">Click any ticket row to inspect IT progress notes and updates</p>
          </div>

          <form method="GET" action="/" class="flex items-center gap-2">
            <div class="relative w-full sm:w-72">
              <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none"></i>
              <input type="text" name="q" value="{html.escape(search_q)}" placeholder="Search tickets by subject or ID..." 
                     class="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-purple-700 bg-white">
            </div>
            <button type="submit" class="px-3.5 py-2 rounded-xl bg-purple-700 hover:bg-purple-800 text-white text-xs font-semibold">
              Search
            </button>
            {f'<a href="/" class="px-2.5 py-2 rounded-xl text-slate-500 hover:text-slate-700 text-xs font-semibold">Clear</a>' if search_q else ''}
          </form>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm text-slate-600 divide-y divide-slate-200/80">
            <thead class="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              <tr>
                <th scope="col" class="px-5 py-3.5">Ticket ID</th>
                <th scope="col" class="px-5 py-3.5">Date</th>
                <th scope="col" class="px-5 py-3.5">Subject</th>
                <th scope="col" class="px-5 py-3.5">Type</th>
                <th scope="col" class="px-5 py-3.5">Priority</th>
                <th scope="col" class="px-5 py-3.5">Status</th>
                <th scope="col" class="px-5 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 bg-white">
              {table_body}
            </tbody>
          </table>
        </div>
      </div>
    </div>
    """

# ==========================================
# IT CONSOLE (SOLO IT SPECIALIST)
# ==========================================

def render_admin_dashboard(tickets, user, view_mode="kanban", status_f="all", priority_f="all", category_f="all", search_q=""):
    metrics = compute_metrics(tickets)
    
    filtered = tickets
    if status_f != "all":
        filtered = [t for t in filtered if t["status"].lower().replace(" ", "_") == status_f.lower().replace(" ", "_")]
    if priority_f != "all":
        filtered = [t for t in filtered if t["priority"].lower() == priority_f.lower()]
    if category_f != "all":
        filtered = [t for t in filtered if t["issue_type"].lower().replace(" ", "_") == category_f.lower().replace(" ", "_")]
    if search_q:
        q = search_q.lower()
        filtered = [t for t in filtered if q in t["id"].lower() or q in t["subject"].lower() or q in t["description"].lower() or q in t["submitter_name"].lower()]

    user_settings = get_user_settings(user["username"]) if user else {}
    show_urgent = user_settings.get("urgent_alerts", 1)
    critical_alert = f'<div class="mt-3 pt-2.5 border-t border-slate-100 flex items-center gap-1.5 text-xs text-rose-600 font-bold"><span class="w-2 h-2 rounded-full bg-rose-600 animate-ping"></span><span>{metrics["critical"]} Critical issue active!</span></div>' if (metrics["critical"] > 0 and show_urgent) else ''

    show_daily_summary = user_settings.get("daily_summary", 0)
    daily_briefing_html = ""
    if show_daily_summary:
        open_count = metrics['open'] + metrics['in_progress']
        daily_briefing_html = f"""
        <div class="animate-entrance-2 p-4 rounded-2xl bg-purple-50/80 border border-purple-200/80 flex items-center justify-between shadow-sm">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-purple-700 text-white flex items-center justify-center shadow-sm">
              <i data-lucide="bell" class="w-4 h-4"></i>
            </div>
            <div>
              <p class="text-[11px] font-bold uppercase tracking-wider text-purple-700">Daily Task Briefing</p>
              <p class="text-xs sm:text-sm font-semibold text-slate-800">You have {open_count} active management task{'s' if open_count != 1 else ''} awaiting action ({metrics['open']} open backlog, {metrics['in_progress']} in progress).</p>
            </div>
          </div>
          <span class="hidden sm:inline-flex items-center gap-1 px-3 py-1 rounded-full bg-white text-purple-700 border border-purple-200 text-xs font-bold shadow-xs">
            <i data-lucide="clock" class="w-3.5 h-3.5"></i>
            <span>Daily Digest Active</span>
          </span>
        </div>
        """

    if view_mode == "kanban":
        kanban_cols = {"Open": [], "In Progress": [], "Resolved": [], "Closed": []}
        for t in filtered:
            if t["status"] in kanban_cols:
                kanban_cols[t["status"]].append(t)
        
        def render_col_cards(items):
            if not items:
                return '<div class="h-32 border-2 border-dashed border-slate-200 rounded-xl flex items-center justify-center text-xs text-slate-400 font-medium">No tickets in this column</div>'
            cards = []
            for t in items:
                is_mine = is_ticket_creator(t, user)
                creator_badge = '<span class="text-[10px] font-bold text-purple-700 bg-purple-50 px-1.5 py-0.5 rounded border border-purple-200">Yours</span>' if is_mine else ''
                cards.append(f"""
                <div class="bg-white rounded-xl p-4 border border-slate-200 shadow-sm hover:shadow-md hover:border-purple-500 transition-all cursor-pointer group" onclick="window.location='/ticket?id={t['id']}'">
                  <div class="flex items-center justify-between gap-2 mb-2">
                    <div class="flex items-center gap-1.5">
                      <span class="font-mono text-xs font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">{t['id']}</span>
                      {creator_badge}
                    </div>
                    {get_priority_badge(t['priority'])}
                  </div>
                  <h4 class="font-bold text-slate-900 text-sm group-hover:text-purple-700 transition-colors line-clamp-2">{html.escape(t['subject'])}</h4>
                  <p class="text-xs text-slate-500 mt-2 line-clamp-2 leading-relaxed">{html.escape(t['description'])}</p>
                  <div class="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                    <span>{html.escape(t['submitter_name'])}</span>
                    <span>{t['created_at'].split(' ')[0]}</span>
                  </div>
                </div>
                """)
            return "\n".join(cards)

        content_view = f"""
        <div class="animate-entrance-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
          <!-- OPEN -->
          <div class="flex flex-col bg-slate-100/80 rounded-2xl border border-slate-200 p-4 min-h-[480px]">
            <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-200">
              <div class="flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-blue-500"></span>
                <h2 class="font-bold text-sm text-slate-900">Open Backlog</h2>
              </div>
              <span class="px-2 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-700 border border-blue-200">{len(kanban_cols['Open'])}</span>
            </div>
            <div class="space-y-3 flex-1 overflow-y-auto">{render_col_cards(kanban_cols['Open'])}</div>
          </div>

          <!-- IN PROGRESS -->
          <div class="flex flex-col bg-slate-100/80 rounded-2xl border border-slate-200 p-4 min-h-[480px]">
            <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-200">
              <div class="flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-amber-500 animate-pulse"></span>
                <h2 class="font-bold text-sm text-slate-900">In Progress</h2>
              </div>
              <span class="px-2 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">{len(kanban_cols['In Progress'])}</span>
            </div>
            <div class="space-y-3 flex-1 overflow-y-auto">{render_col_cards(kanban_cols['In Progress'])}</div>
          </div>

          <!-- RESOLVED -->
          <div class="flex flex-col bg-slate-100/80 rounded-2xl border border-slate-200 p-4 min-h-[480px]">
            <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-200">
              <div class="flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-emerald-500"></span>
                <h2 class="font-bold text-sm text-slate-900">Resolved</h2>
              </div>
              <span class="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">{len(kanban_cols['Resolved'])}</span>
            </div>
            <div class="space-y-3 flex-1 overflow-y-auto">{render_col_cards(kanban_cols['Resolved'])}</div>
          </div>

          <!-- CLOSED -->
          <div class="flex flex-col bg-slate-100/80 rounded-2xl border border-slate-200 p-4 min-h-[480px]">
            <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-200">
              <div class="flex items-center gap-2">
                <span class="w-3 h-3 rounded-full bg-slate-400"></span>
                <h2 class="font-bold text-sm text-slate-900">Archived / Closed</h2>
              </div>
              <span class="px-2 py-0.5 rounded-full text-xs font-bold bg-slate-200 text-slate-700 border border-slate-300">{len(kanban_cols['Closed'])}</span>
            </div>
            <div class="space-y-3 flex-1 overflow-y-auto">{render_col_cards(kanban_cols['Closed'])}</div>
          </div>
        </div>
        """
    else:
        table_rows = []
        for t in filtered:
            is_mine = is_ticket_creator(t, user)
            can_manage = can_manage_ticket(t, user)
            creator_badge = '<span class="text-[10px] font-bold text-purple-700 bg-purple-50 px-1.5 py-0.5 rounded border border-purple-200">Yours</span>' if is_mine else ''
            quick_edit = f'''<a href="/edit-ticket?id={t['id']}" class="p-1 rounded hover:bg-purple-100 text-slate-400 hover:text-purple-700 transition-colors" title="Edit ticket"><i data-lucide="edit-3" class="w-3.5 h-3.5"></i></a>''' if can_manage else ''
            table_rows.append(f"""
            <tr class="hover:bg-slate-50/80 transition-colors">
              <td class="px-5 py-4 whitespace-nowrap">
                <div class="flex items-center gap-1.5">
                  <a href="/ticket?id={t['id']}" class="font-mono text-xs font-bold text-purple-700 bg-purple-50 hover:bg-purple-100 px-2.5 py-1 rounded-md border border-purple-200">{t['id']}</a>
                  {creator_badge}
                </div>
              </td>
              <td class="px-5 py-4 whitespace-nowrap text-xs text-slate-500 font-mono">{format_time_12h(t['created_at'])}</td>
              <td class="px-5 py-4 whitespace-nowrap">
                <p class="font-semibold text-slate-900 text-xs">{html.escape(t['submitter_name'])}</p>
                <p class="text-[11px] text-slate-400">{html.escape(t['submitter_role'])}</p>
              </td>
              <td class="px-5 py-4">
                <a href="/ticket?id={t['id']}" class="font-semibold text-slate-900 hover:text-purple-700 transition-colors text-sm line-clamp-1">{html.escape(t['subject'])}</a>
              </td>
              <td class="px-5 py-4 whitespace-nowrap">{get_issue_badge(t['issue_type'])}</td>
              <td class="px-5 py-4 whitespace-nowrap">{get_priority_badge(t['priority'])}</td>
              <td class="px-5 py-4 whitespace-nowrap">
                <form action="/update-status" method="POST" class="inline">
                  <input type="hidden" name="id" value="{t['id']}">
                  <select name="status" onchange="this.form.submit()" class="text-xs font-bold rounded-lg px-2.5 py-1 border bg-white">
                    <option value="Open" {'selected' if t['status']=='Open' else ''}>🔵 Open</option>
                    <option value="In Progress" {'selected' if t['status']=='In Progress' else ''}>🟠 In Progress</option>
                    <option value="Resolved" {'selected' if t['status']=='Resolved' else ''}>🟢 Resolved</option>
                    <option value="Closed" {'selected' if t['status']=='Closed' else ''}>⚪ Closed</option>
                  </select>
                </form>
              </td>
              <td class="px-5 py-4 whitespace-nowrap text-right">
                <div class="flex items-center justify-end gap-1.5">
                  {quick_edit}
                  <a href="/ticket?id={t['id']}" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold">Manage &rarr;</a>
                </div>
              </td>
            </tr>
            """)
        table_html = "\n".join(table_rows) if table_rows else '<tr><td colspan="8" class="p-8 text-center text-slate-500">No tickets found matching filters.</td></tr>'
        content_view = f"""
        <div class="animate-entrance-4 bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-slate-600 divide-y divide-slate-200/80">
              <thead class="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <tr>
                  <th scope="col" class="px-5 py-3.5">ID</th>
                  <th scope="col" class="px-5 py-3.5">Date</th>
                  <th scope="col" class="px-5 py-3.5">Submitter & Role</th>
                  <th scope="col" class="px-5 py-3.5">Subject</th>
                  <th scope="col" class="px-5 py-3.5">Category</th>
                  <th scope="col" class="px-5 py-3.5">Priority</th>
                  <th scope="col" class="px-5 py-3.5">Status</th>
                  <th scope="col" class="px-5 py-3.5 text-right">Quick Triage</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 bg-white">
                {table_html}
              </tbody>
            </table>
          </div>
        </div>
        """

    return f"""
    <div class="space-y-6">
      <!-- HEADER CONSOLE -->
      <div class="animate-entrance-1 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 text-white p-5 sm:p-6 rounded-3xl shadow-xl border border-slate-800">
        <div>
          <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
            <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-purple-900/60 text-purple-300 border border-purple-700/60 text-[10px] sm:text-xs font-semibold uppercase tracking-wider">
              <i data-lucide="shield" class="w-3 h-3 sm:w-3.5 sm:h-3.5 text-purple-400"></i>
              <span>onIT Operations Command</span>
            </span>
            <span class="hidden sm:inline text-xs text-slate-400">{ORG_NAME}</span>
          </div>
          <h1 class="text-xl sm:text-2xl font-black tracking-tight mt-1.5 text-white">Operations & Triage Console</h1>
          <p class="text-xs sm:text-sm text-slate-300 mt-1 max-w-xl">
            Logged in as <strong>{html.escape(user['name'])}</strong> &bull; Review incoming manager tickets, resolve system errors, and maintain cooperative IT uptime.
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <div class="flex items-center bg-slate-800 p-1 rounded-xl border border-slate-700">
            <a href="/?view_mode=kanban&status={status_f}&priority={priority_f}&category={category_f}&q={search_q}" class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all {'bg-purple-700 text-white shadow-sm' if view_mode=='kanban' else 'text-slate-400 hover:text-white'}">
              Kanban Board
            </a>
            <a href="/?view_mode=table&status={status_f}&priority={priority_f}&category={category_f}&q={search_q}" class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all {'bg-purple-700 text-white shadow-sm' if view_mode=='table' else 'text-slate-400 hover:text-white'}">
              Master Table
            </a>
          </div>
          <a href="/submit" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-purple-700 hover:bg-purple-800 text-white text-xs font-bold transition-colors">
            <i data-lucide="plus" class="w-4 h-4"></i><span>New Ticket</span>
          </a>
        </div>
      </div>

      {daily_briefing_html}

      <!-- MASTER METRICS BAR -->
      <div class="animate-entrance-2 grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm relative overflow-hidden">
          <p class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Total Active</p>
          <p class="text-3xl font-black text-slate-900 mt-1">{metrics['active']}</p>
          <p class="text-xs text-slate-400 mt-0.5">Requiring attention</p>
          {critical_alert}
        </div>

        <div class="bg-white p-5 rounded-2xl border border-blue-200/80 shadow-sm relative overflow-hidden">
          <div class="absolute top-0 left-0 right-0 h-1 bg-blue-500"></div>
          <p class="text-[11px] font-bold uppercase tracking-wider text-blue-700">Open Backlog</p>
          <p class="text-3xl font-black text-blue-900 mt-1">{metrics['open']}</p>
          <p class="text-xs text-blue-600 mt-0.5">Awaiting triage</p>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-amber-200/80 shadow-sm relative overflow-hidden">
          <div class="absolute top-0 left-0 right-0 h-1 bg-amber-500"></div>
          <p class="text-[11px] font-bold uppercase tracking-wider text-amber-700">In Progress</p>
          <p class="text-3xl font-black text-amber-900 mt-1">{metrics['in_progress']}</p>
          <p class="text-xs text-amber-600 mt-0.5">Actively working</p>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-emerald-200/80 shadow-sm relative overflow-hidden">
          <div class="absolute top-0 left-0 right-0 h-1 bg-emerald-500"></div>
          <p class="text-[11px] font-bold uppercase tracking-wider text-emerald-700">Resolved</p>
          <p class="text-3xl font-black text-emerald-900 mt-1">{metrics['resolved']}</p>
          <p class="text-xs text-emerald-600 mt-0.5">Fixed & verified</p>
        </div>
      </div>

      <!-- FILTER CONTROLS -->
      <div class="animate-entrance-3 relative z-30 bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm">
        <form method="GET" action="/" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          <input type="hidden" name="view_mode" value="{view_mode}">
          <div class="relative lg:col-span-2">
            <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2"></i>
            <input type="text" name="q" value="{html.escape(search_q)}" placeholder="Filter by ID, subject, manager name..." 
                   class="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-200 text-xs sm:text-sm focus:ring-2 focus:ring-purple-700 focus:outline-none">
          </div>
          <div class="relative">
            <select name="status" onchange="this.form.submit()" class="w-full pl-3 pr-8 py-2 rounded-xl border border-slate-200 text-xs sm:text-sm bg-white text-slate-700 appearance-none">
              <option value="all" {'selected' if status_f=='all' else ''}>All Statuses</option>
              <option value="open" {'selected' if status_f=='open' else ''}>🔵 Open</option>
              <option value="in_progress" {'selected' if status_f=='in_progress' else ''}>🟠 In Progress</option>
              <option value="resolved" {'selected' if status_f=='resolved' else ''}>🟢 Resolved</option>
              <option value="closed" {'selected' if status_f=='closed' else ''}>⚪ Closed</option>
            </select>
            <i data-lucide="chevron-down" class="select-chevron w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"></i>
          </div>
          <div class="relative">
            <select name="priority" onchange="this.form.submit()" class="w-full pl-3 pr-8 py-2 rounded-xl border border-slate-200 text-xs sm:text-sm bg-white text-slate-700 appearance-none">
              <option value="all" {'selected' if priority_f=='all' else ''}>All Priorities</option>
              <option value="critical" {'selected' if priority_f=='critical' else ''}>🚨 Critical</option>
              <option value="high" {'selected' if priority_f=='high' else ''}>High</option>
              <option value="medium" {'selected' if priority_f=='medium' else ''}>Medium</option>
              <option value="low" {'selected' if priority_f=='low' else ''}>Low</option>
            </select>
            <i data-lucide="chevron-down" class="select-chevron w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"></i>
          </div>
          <div class="relative">
            <select name="category" onchange="this.form.submit()" class="w-full pl-3 pr-8 py-2 rounded-xl border border-slate-200 text-xs sm:text-sm bg-white text-slate-700 appearance-none">
              <option value="all" {'selected' if category_f=='all' else ''}>All Categories</option>
              <option value="web_bug/error" {'selected' if category_f=='web_bug/error' else ''}>Web Bug/Error</option>
              <option value="new_feature_request" {'selected' if category_f=='new_feature_request' else ''}>New Feature Request</option>
              <option value="content_update" {'selected' if category_f=='content_update' else ''}>Content Update</option>
              <option value="password/login_issue" {'selected' if category_f=='password/login_issue' else ''}>Password/Login</option>
            </select>
            <i data-lucide="chevron-down" class="select-chevron w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"></i>
          </div>
        </form>
      </div>

      {content_view}
    </div>
    """

def render_ticket_detail(ticket, user):
    is_admin = (user and user.get("role") == "admin")
    can_manage = can_manage_ticket(ticket, user)

    creator_actions_top = ""
    delete_modal_html = ""
    if can_manage:
        creator_actions_top = f"""
        <div class="flex items-center gap-1.5">
          <a href="/edit-ticket?id={ticket['id']}" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 text-xs font-bold transition-all shadow-xs" title="Edit this ticket">
            <i data-lucide="edit-3" class="w-3.5 h-3.5"></i>
            <span>Edit</span>
          </a>
          <button type="button" onclick="openDeleteModal()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-bold transition-all shadow-xs cursor-pointer" title="Delete this ticket">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
            <span>Delete</span>
          </button>
        </div>
        """
        delete_modal_html = f"""
        <div id="deleteModal" onclick="if(event.target===this)closeDeleteModal()" class="hidden fixed inset-0 z-[99999] flex items-center justify-center p-4 backdrop-blur-md bg-slate-900/10 pointer-events-auto transition-all" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; width: 100vw; height: 100vh; z-index: 99999; backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);">
          <div class="bg-white rounded-2xl border border-slate-200/90 shadow-[0_25px_60px_-15px_rgba(15,23,42,0.35)] max-w-md w-full p-6 space-y-4 my-auto animate-entrance-1" onclick="event.stopPropagation()">
            <div class="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto">
              <i data-lucide="alert-triangle" class="w-6 h-6"></i>
            </div>
            <div class="text-center space-y-1.5">
              <h3 class="text-lg font-bold text-slate-900">Delete Ticket {ticket['id']}?</h3>
              <p class="text-xs sm:text-sm text-slate-500 leading-relaxed">
                Are you sure you want to permanently delete ticket <strong>{ticket['id']}</strong>? All associated timeline logs and comments will also be permanently deleted. <strong>This action cannot be undone.</strong>
              </p>
            </div>
            <form action="/delete-ticket" method="POST" class="pt-2 flex items-center justify-end gap-3">
              <input type="hidden" name="id" value="{ticket['id']}">
              <button type="button" onclick="closeDeleteModal()" class="px-4 py-2 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-bold transition-colors cursor-pointer">
                Cancel
              </button>
              <button type="submit" class="inline-flex items-center gap-1.5 px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shadow-md shadow-rose-900/20 transition-all cursor-pointer">
                <i data-lucide="trash-2" class="w-4 h-4"></i>
                <span>Yes, Delete Ticket</span>
              </button>
            </form>
          </div>
        </div>
        """
    
    events_html = []
    for ev in ticket.get("timeline", []):
        if ev.get("author") == "System Dispatch" or ev.get("action") == "Resolution Dispatched":
            continue
        if not ev.get("is_internal") or is_admin:
            is_int = bool(ev.get("is_internal", 0))
            is_it_role = ev.get("role") in ["IT Admin", "IT Specialist"] or "IT" in str(ev.get("role", ""))
            card_bg = "bg-amber-50/70 border-amber-200 text-amber-950" if is_int else ("bg-purple-50/60 border-purple-100 text-slate-800" if is_it_role else "bg-slate-50 border-slate-200 text-slate-800")
            dot_bg = "bg-amber-100 text-amber-800 border-2 border-amber-300" if is_int else ("bg-purple-100 text-purple-700 border-2 border-purple-300" if is_it_role else "bg-slate-100 text-slate-700 border-2 border-slate-300")
            badge_role = "bg-purple-700 text-white" if is_it_role else "bg-slate-200 text-slate-700"
            int_pill = '<span class="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-amber-200 text-amber-900"><i data-lucide="lock" class="w-2.5 h-2.5"></i> Internal IT Note</span>' if is_int else ''
            icon = "lock" if is_int else ("refresh-cw" if ev.get("action")=="Status Changed" else ("sparkles" if ev.get("action") in ["Ticket Created", "Ticket Issued"] else "message-square"))

            events_html.append(f"""
            <div class="relative flex items-start gap-4 text-xs sm:text-sm pl-1">
              <div class="w-7 h-7 rounded-full flex items-center justify-center shrink-0 z-10 {dot_bg}">
                <i data-lucide="{icon}" class="w-3.5 h-3.5"></i>
              </div>
              <div class="flex-1 p-4 rounded-xl border transition-all {card_bg}">
                <div class="flex flex-wrap items-center justify-between gap-1 mb-1.5">
                  <div class="flex items-center gap-2">
                    <span class="font-bold text-slate-900">{html.escape(ev.get('author',''))}</span>
                    <span class="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full {badge_role}">{html.escape(ev.get('role',''))}</span>
                    {int_pill}
                  </div>
                  <span class="text-[11px] text-slate-400 font-mono">{format_time_12h(ev.get('timestamp',''))}</span>
                </div>
                <p class="text-xs sm:text-sm leading-relaxed mt-1">{html.escape(ev.get('content',''))}</p>
              </div>
            </div>
            """)

    timeline_str = "\n".join(events_html)

    if is_admin:
        sidebar_controls = f"""
        <div class="bg-slate-900 text-white rounded-2xl border border-slate-800 p-6 shadow-xl space-y-6">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h2 class="font-bold text-sm text-purple-300 flex items-center gap-2">
              <i data-lucide="sliders" class="w-4 h-4 text-purple-400"></i>
              <span>onIT Developer Controls</span>
            </h2>
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          </div>

          <form action="/update-status" method="POST" class="space-y-2">
            <input type="hidden" name="id" value="{ticket['id']}">
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-400">Ticket Status</label>
            <div class="flex gap-2">
              <select name="status" class="dark-select flex-1 px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-xs font-bold focus:outline-none">
                <option value="Open" {'selected' if ticket['status']=='Open' else ''}>🔵 Open Backlog</option>
                <option value="In Progress" {'selected' if ticket['status']=='In Progress' else ''}>🟠 In Progress</option>
                <option value="Resolved" {'selected' if ticket['status']=='Resolved' else ''}>🟢 Resolved</option>
                <option value="Closed" {'selected' if ticket['status']=='Closed' else ''}>⚪ Closed / Archived</option>
              </select>
              <button type="submit" class="px-3.5 py-2 rounded-xl bg-purple-700 hover:bg-purple-800 text-white text-xs font-bold transition-colors">Apply</button>
            </div>
          </form>

          <form action="/update-priority" method="POST" class="space-y-2 pt-2 border-t border-slate-800">
            <input type="hidden" name="id" value="{ticket['id']}">
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-400">Priority Classification</label>
            <div class="flex gap-2">
              <select name="priority" class="dark-select flex-1 px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-xs font-bold focus:outline-none">
                <option value="Low" {'selected' if ticket['priority']=='Low' else ''}>Low Priority</option>
                <option value="Medium" {'selected' if ticket['priority']=='Medium' else ''}>Medium Priority</option>
                <option value="High" {'selected' if ticket['priority']=='High' else ''}>High Priority</option>
                <option value="Critical" {'selected' if ticket['priority']=='Critical' else ''}>🚨 Critical Priority</option>
              </select>
              <button type="submit" class="px-3.5 py-2 rounded-xl bg-purple-700 hover:bg-purple-800 text-white text-xs font-bold transition-colors">Update</button>
            </div>
          </form>

          <div class="pt-3 border-t border-slate-800 space-y-2">
            <p class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Quick Transition</p>
            <div class="grid grid-cols-2 gap-2">
              <form action="/update-status" method="POST">
                <input type="hidden" name="id" value="{ticket['id']}">
                <input type="hidden" name="status" value="In Progress">
                <button type="submit" class="w-full py-2 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-xs font-bold border border-amber-500/30">Start Work</button>
              </form>
              <form action="/update-status" method="POST">
                <input type="hidden" name="id" value="{ticket['id']}">
                <input type="hidden" name="status" value="Resolved">
                <button type="submit" class="w-full py-2 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 text-xs font-bold border border-emerald-500/30">Mark Fixed</button>
              </form>
            </div>
          </div>
        </div>
        """
    else:
        sidebar_controls = f"""
        <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4">
          <div class="flex items-center gap-2 pb-3 border-b border-slate-200">
            <i data-lucide="info" class="w-4 h-4 text-purple-700"></i>
            <h3 class="font-bold text-sm text-slate-900">Ticket Status Info</h3>
          </div>
          <div class="space-y-3 text-xs">
            <div>
              <p class="text-slate-400 uppercase font-semibold text-[10px]">Current Status</p>
              <p class="font-bold text-slate-800 text-sm mt-0.5">{ticket['status']}</p>
            </div>
            <div>
              <p class="text-slate-400 uppercase font-semibold text-[10px]">Assigned Specialist</p>
              <p class="font-bold text-slate-800 mt-0.5">IT Specialist &bull; <span class="font-normal text-slate-500">IT Lead</span></p>
            </div>
            <div>
              <p class="text-slate-400 uppercase font-semibold text-[10px]">Issued By</p>
              <p class="font-bold text-slate-800 mt-0.5">{html.escape(ticket['submitter_role'])}</p>
            </div>
          </div>
        </div>
        """

    comment_extra = '<label class="flex items-center gap-2 cursor-pointer select-none text-xs font-semibold text-slate-700"><input type="checkbox" name="is_internal" value="true" class="rounded border-slate-300 text-purple-700 w-4 h-4"><span class="flex items-center gap-1"><i data-lucide="lock" class="w-3.5 h-3.5 text-amber-600"></i><span>Make this an Internal Note (Visible only in IT view)</span></span></label>' if is_admin else '<span class="text-xs text-slate-400">Updates are posted directly to your IT Specialist.</span>'

    snippets = '<div class="hidden sm:flex items-center gap-1.5 text-xs"><span class="text-slate-400 text-[11px]">Quick snippets:</span><button type="button" onclick="document.getElementById(\'comment_box\').value=\'Working on the fix now. Testing across Chrome and mobile.\'" class="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-600 text-[10px] font-medium">Working on fix</button><button type="button" onclick="document.getElementById(\'comment_box\').value=\'Fixed the issue and verified in staging. Please test on your end.\'" class="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-600 text-[10px] font-medium">Fixed bug</button></div>' if is_admin else ''
    comment_placeholder = "Type your developer update or internal fix progress (e.g., 'Working on the fix now' or 'Fixed the login page bug')..." if is_admin else "Add follow-up notes, additional details, or feedback for your IT Specialist..."

    main_body = f"""
    <div class="space-y-6">
      <div class="animate-entrance-1 flex flex-wrap items-center justify-between gap-3">
        <a href="/" class="inline-flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-slate-500 hover:text-slate-800 transition-colors">
          <i data-lucide="arrow-left" class="w-4 h-4"></i>
          <span>Back to Dashboard</span>
        </a>
        <div class="flex items-center gap-2">
          {creator_actions_top}
          <span class="font-mono text-xs font-bold text-slate-700 bg-white border border-slate-200 px-3 py-1 rounded-lg">Ticket {ticket['id']}</span>
          {('<span class="px-2.5 py-1 rounded-lg bg-purple-900 text-purple-200 text-xs font-bold border border-purple-700 flex items-center gap-1"><i data-lucide="shield" class="w-3.5 h-3.5 text-purple-400"></i> Admin Mode</span>') if is_admin else ''}
        </div>
      </div>

      <div class="animate-entrance-2 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-7 shadow-sm space-y-5">
            <div class="flex flex-wrap items-center gap-2">
              {get_issue_badge(ticket['issue_type'])}
              {get_priority_badge(ticket['priority'])}
              {get_status_badge(ticket['status'])}
            </div>

            <h1 class="text-xl sm:text-2xl font-black text-slate-900 leading-snug">{html.escape(ticket['subject'])}</h1>

            <div class="flex items-center gap-3 p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 text-xs text-slate-600">
              <div class="w-8 h-8 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-xs shrink-0">
                {ticket['submitter_name'][0]}
              </div>
              <div>
                <p class="font-bold text-slate-800">{html.escape(ticket['submitter_name'])} <span class="font-normal text-slate-400">({html.escape(ticket['submitter_role'])})</span></p>
                <p class="text-slate-500 font-mono mt-0.5">Submitted on {format_time_12h(ticket['created_at'])}</p>
              </div>
            </div>

            <div class="space-y-2 pt-2">
              <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400">Detailed Description</h3>
              <div class="p-4 rounded-xl bg-slate-50/80 border border-slate-200/80 text-slate-700 text-sm leading-relaxed whitespace-pre-line">{html.escape(ticket['description'].strip())}</div>
            </div>
          </div>

          <!-- TIMELINE -->
          <div class="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-7 shadow-sm space-y-6">
            <div class="flex items-center justify-between pb-3 border-b border-slate-200">
              <div class="flex items-center gap-2">
                <i data-lucide="git-commit" class="w-5 h-5 text-purple-700"></i>
                <h2 class="text-base font-bold text-slate-900">Activity & Timeline</h2>
              </div>
              <span class="text-xs text-slate-400 font-medium">{len(ticket.get('timeline', []))} updates</span>
            </div>

            <div class="space-y-4 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-slate-200">
              {timeline_str}
            </div>

            <div class="pt-6 border-t border-slate-200">
              <form action="/add-comment" method="POST" class="space-y-3">
                <input type="hidden" name="id" value="{ticket['id']}">
                <div class="flex items-center justify-between">
                  <label for="comment_box" class="block text-xs font-bold uppercase tracking-wider text-slate-600">
                    {'Add Developer Timeline Update or Note' if is_admin else 'Follow-up or Instruction to IT'}
                  </label>
                  {snippets}
                </div>

                <textarea id="comment_box" name="comment" rows="3" required placeholder="{comment_placeholder}"
                          class="w-full p-3.5 rounded-xl border border-slate-200 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-purple-700 bg-slate-50/50"></textarea>

                <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
                  {comment_extra}
                  <button type="submit" class="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-purple-700 hover:bg-purple-800 text-white text-xs sm:text-sm font-bold shadow-md shadow-purple-900/20 transition-all">
                    <i data-lucide="send" class="w-4 h-4"></i>
                    <span>Post Update</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          {sidebar_controls}

          <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-3 text-xs">
            <h3 class="font-bold text-sm text-slate-900 pb-2 border-b border-slate-200">Database Record</h3>
            <div class="flex justify-between py-1"><span class="text-slate-500">Record ID:</span><span class="font-mono font-bold text-slate-800">{ticket['id']}</span></div>
            <div class="flex justify-between py-1"><span class="text-slate-500">Created:</span><span class="text-slate-800 font-mono">{format_time_12h(ticket['created_at'])}</span></div>
            <div class="flex justify-between py-1"><span class="text-slate-500">Issue Category:</span><span class="text-slate-800 font-medium">{ticket['issue_type']}</span></div>
            <div class="flex justify-between py-1"><span class="text-slate-500">Issued By:</span><span class="text-slate-800 font-medium">{html.escape(ticket['submitter_role'])}</span></div>
            <div class="flex justify-between py-1 pt-2 border-t border-slate-100"><span class="text-slate-500">Storage Engine:</span><span class="text-purple-700 font-mono font-bold">SQLite 3</span></div>
          </div>
        </div>
      </div>
    </div>
    """
    return (main_body, delete_modal_html)

def render_submit_ticket_form(user):
    default_name = html.escape(user["name"]) if user else ""
    default_email = html.escape(user["email"]) if user else ""

    return f"""
    <div class="max-w-3xl mx-auto space-y-6">
      <div class="animate-entrance-1 flex items-center justify-between">
        <a href="/" class="inline-flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-slate-500 hover:text-slate-800 transition-colors">
          <i data-lucide="arrow-left" class="w-4 h-4"></i>
          <span>Back to Dashboard</span>
        </a>
        <span class="text-xs text-slate-400 font-medium">Step 1 of 1: Request Details</span>
      </div>

      <div class="animate-entrance-2 bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <!-- SOLID PURPLE BANNER -->
        <div class="p-6 sm:p-8 bg-purple-700 text-white">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-purple-800 flex items-center justify-center text-white">
              <i data-lucide="plus-circle" class="w-6 h-6"></i>
            </div>
            <div>
              <h1 class="text-xl sm:text-2xl font-black">Issue Ticket to IT</h1>
              <p class="text-xs sm:text-sm text-purple-200 mt-0.5">{ORG_NAME} &bull; Powered by onIT</p>
            </div>
          </div>
        </div>

        <form action="/submit" method="POST" class="p-6 sm:p-8 space-y-6">
          <div>
            <label for="full_name" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
              Name <span class="text-rose-500">*</span>
            </label>
            <input type="text" id="full_name" name="full_name" required value="{default_name}" placeholder="Enter your name"
                   class="input-field w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-50/50 text-slate-900 font-medium">
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="issue_type" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Issue Type <span class="text-rose-500">*</span>
              </label>
              <div class="relative">
                <select id="issue_type" name="issue_type" required
                        class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm appearance-none bg-slate-50/50 text-slate-800">
                  <option value="Web Bug/Error">Web Bug / Error</option>
                  <option value="New Feature Request">New Feature Request</option>
                  <option value="Content Update">Content Update</option>
                  <option value="Password/Login Issue">Password / Login Issue</option>
                </select>
                <i data-lucide="chevron-down" class="select-chevron w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"></i>
              </div>
            </div>

            <div>
              <label for="priority" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Priority Level <span class="text-rose-500">*</span>
              </label>
              <div class="relative">
                <select id="priority" name="priority" required
                        class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm appearance-none bg-slate-50/50 text-slate-800">
                  <option value="Low">Low</option>
                  <option value="Medium" selected>Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>
                <i data-lucide="chevron-down" class="select-chevron w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"></i>
              </div>
            </div>
          </div>

          <div>
            <label for="subject" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
              Subject / Title <span class="text-rose-500">*</span>
            </label>
            <input type="text" id="subject" name="subject" required placeholder="Brief summary (e.g. 'Cooperative loan verification form timing out')"
                   class="input-field w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-50/50 text-slate-900 font-medium">
          </div>

          <div>
            <label for="description" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
              Detailed Description <span class="text-rose-500">*</span>
            </label>
            <textarea id="description" name="description" rows="5" required placeholder="Please provide specific details: which web page/URL, what browser, steps to reproduce..."
                      class="input-field w-full p-4 rounded-xl border border-slate-200 text-sm bg-slate-50/50 leading-relaxed text-slate-900 font-medium"></textarea>
            <p class="text-[11px] text-slate-400 mt-1.5">
              💡 The more details you share, the faster your IT Specialist can identify and fix the issue.
            </p>
          </div>

          <div class="pt-4 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
            <a href="/" class="w-full sm:w-auto text-center px-5 py-2.5 rounded-xl border border-slate-200 text-slate-600 hover:text-slate-900 text-xs sm:text-sm font-semibold">
              Cancel
            </a>
            <button type="submit" class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-purple-700 hover:bg-purple-800 text-white text-xs sm:text-sm font-bold shadow-md shadow-purple-900/20 transition-all">
              <i data-lucide="check" class="w-4 h-4"></i>
              <span>Assign Ticket to IT</span>
            </button>
          </div>
        </form>
      </div>
    </div>
    """

def render_edit_ticket_form(ticket, user):
    return f"""
    <div class="max-w-3xl mx-auto space-y-6">
      <div class="animate-entrance-1 flex items-center justify-between">
        <a href="/ticket?id={ticket['id']}" class="inline-flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-slate-500 hover:text-slate-800 transition-colors">
          <i data-lucide="arrow-left" class="w-4 h-4"></i>
          <span>Back to Ticket {ticket['id']}</span>
        </a>
        <span class="font-mono text-xs font-bold text-slate-700 bg-white border border-slate-200 px-3 py-1 rounded-lg">Editing {ticket['id']}</span>
      </div>

      <div class="animate-entrance-2 bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div class="p-6 sm:p-8 bg-purple-700 text-white">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-purple-800 flex items-center justify-center text-white">
              <i data-lucide="edit-3" class="w-6 h-6"></i>
            </div>
            <div>
              <h1 class="text-xl sm:text-2xl font-black">Edit Ticket {ticket['id']}</h1>
              <p class="text-xs sm:text-sm text-purple-200 mt-0.5">{ORG_NAME} &bull; Author Modifications</p>
            </div>
          </div>
        </div>

        <form action="/edit-ticket" method="POST" class="p-6 sm:p-8 space-y-6">
          <input type="hidden" name="id" value="{ticket['id']}">

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="issue_type" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Issue Type <span class="text-rose-500">*</span>
              </label>
              <div class="relative">
                <select id="issue_type" name="issue_type" required
                        class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm appearance-none bg-slate-50/50 text-slate-800">
                  <option value="Web Bug/Error" {'selected' if ticket['issue_type']=='Web Bug/Error' else ''}>Web Bug / Error</option>
                  <option value="New Feature Request" {'selected' if ticket['issue_type']=='New Feature Request' else ''}>New Feature Request</option>
                  <option value="Content Update" {'selected' if ticket['issue_type']=='Content Update' else ''}>Content Update</option>
                  <option value="Password/Login Issue" {'selected' if ticket['issue_type']=='Password/Login Issue' else ''}>Password / Login Issue</option>
                </select>
                <i data-lucide="chevron-down" class="select-chevron w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"></i>
              </div>
            </div>

            <div>
              <label for="priority" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                Priority Level <span class="text-rose-500">*</span>
              </label>
              <div class="relative">
                <select id="priority" name="priority" required
                        class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm appearance-none bg-slate-50/50 text-slate-800">
                  <option value="Low" {'selected' if ticket['priority']=='Low' else ''}>Low</option>
                  <option value="Medium" {'selected' if ticket['priority']=='Medium' else ''}>Medium</option>
                  <option value="High" {'selected' if ticket['priority']=='High' else ''}>High</option>
                  <option value="Critical" {'selected' if ticket['priority']=='Critical' else ''}>Critical</option>
                </select>
                <i data-lucide="chevron-down" class="select-chevron w-4 h-4 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"></i>
              </div>
            </div>
          </div>

          <div>
            <label for="subject" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
              Subject / Title <span class="text-rose-500">*</span>
            </label>
            <input type="text" id="subject" name="subject" required value="{html.escape(ticket['subject'])}" placeholder="Brief summary"
                   class="input-field w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-50/50 text-slate-900 font-medium">
          </div>

          <div>
            <label for="description" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
              Detailed Description <span class="text-rose-500">*</span>
            </label>
            <textarea id="description" name="description" rows="6" required placeholder="Detailed description..."
                      class="input-field w-full p-4 rounded-xl border border-slate-200 text-sm bg-slate-50/50 leading-relaxed text-slate-900 font-medium">{html.escape(ticket['description'])}</textarea>
            <p class="text-[11px] text-slate-400 mt-1.5">
              💡 As the ticket author, any edits made will be logged to the activity timeline.
            </p>
          </div>

          <div class="pt-4 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
            <a href="/ticket?id={ticket['id']}" class="w-full sm:w-auto text-center px-5 py-2.5 rounded-xl border border-slate-200 text-slate-600 hover:text-slate-900 text-xs sm:text-sm font-semibold">
              Cancel
            </a>
            <button type="submit" class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-purple-700 hover:bg-purple-800 text-white text-xs sm:text-sm font-bold shadow-md shadow-purple-900/20 transition-all">
              <i data-lucide="check" class="w-4 h-4"></i>
              <span>Save Changes</span>
            </button>
          </div>
        </form>
      </div>
    </div>
    """

# ==========================================
# SETTINGS & PREFERENCES PAGE
# ==========================================

def render_settings_page(user):
    is_admin = (user and user.get("role") == "admin")
    user_name = html.escape(user["name"]) if user else ""
    user_email = html.escape(user["email"]) if user else ""
    user_username = html.escape(user["username"]) if user else ""
    user_role = html.escape(user.get("role_title", "User")) if user else ""
    user_dept = html.escape(user.get("department", "UC-METC")) if user else ""
    avatar_char = user["name"][0] if user else "U"

    tickets = load_tickets_from_db()
    total_tickets = len(tickets)
    try:
        db_size_kb = round(os.path.getsize(DB_FILE) / 1024, 1)
    except Exception:
        db_size_kb = 0

    settings = get_user_settings(user["username"]) if user else {
        "urgent_alerts": 1,
        "ticket_emails": 1,
        "resolution_updates": 1,
        "daily_summary": 0
    }

    return f"""
    <div class="max-w-5xl mx-auto space-y-6">
      <!-- BREADCRUMB -->
      <div class="animate-entrance-1 flex items-center justify-between">
        <a href="/" class="inline-flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-slate-500 hover:text-slate-800 transition-colors">
          <i data-lucide="arrow-left" class="w-4 h-4"></i>
          <span>Back to Dashboard</span>
        </a>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-200 text-xs font-semibold">
          <span class="w-2 h-2 rounded-full bg-purple-600"></span>
          <span>System & Account Configuration</span>
        </div>
      </div>

      <!-- HERO BANNER -->
      <div class="animate-entrance-2 relative overflow-hidden rounded-3xl bg-purple-700 p-6 sm:p-8 text-white shadow-xl shadow-purple-950/10">
        <div class="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-800/90 text-xs font-semibold text-purple-100 border border-purple-500/40 mb-2">
              <i data-lucide="settings" class="w-3.5 h-3.5 text-purple-300"></i>
              <span>Preferences Center &bull; {ORG_NAME}</span>
            </div>
            <h1 class="text-2xl sm:text-3xl font-black tracking-tight">Settings & Preferences</h1>
            <p class="text-purple-100 text-xs sm:text-sm mt-1 max-w-xl">
              Configure personal profile credentials, notification alerts, and task dispatch preferences.
            </p>
          </div>
          <div class="shrink-0 flex items-center gap-3">
            <div class="w-14 h-14 rounded-2xl bg-white text-purple-800 font-black text-2xl flex items-center justify-center shadow-lg">
              {avatar_char}
            </div>
            <div>
              <p class="font-bold text-white text-sm">{user_name}</p>
              <p class="text-xs text-purple-200">{user_role}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- MAIN SETTINGS GRID -->
      <div class="animate-entrance-3 grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- LEFT COLUMN: SYSTEM HEALTH & QUICK INFO -->
        <div class="space-y-6">
          <!-- DATABASE & SYSTEM STATUS CARD -->
          <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-slate-100">
              <div class="flex items-center gap-2">
                <i data-lucide="database" class="w-4 h-4 text-purple-700"></i>
                <h3 class="font-bold text-sm text-slate-900">Database & System</h3>
              </div>
              <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-bold">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Active</span>
              </span>
            </div>

            <div class="space-y-2.5 text-xs">
              <div class="flex justify-between py-1 border-b border-slate-50">
                <span class="text-slate-500">Database Engine:</span>
                <span class="font-mono font-bold text-slate-800">SQLite {sqlite3.sqlite_version}</span>
              </div>
              <div class="flex justify-between py-1 border-b border-slate-50">
                <span class="text-slate-500">Total Tickets:</span>
                <span class="font-bold text-slate-800">{total_tickets} recorded</span>
              </div>
              <div class="flex justify-between py-1 border-b border-slate-50">
                <span class="text-slate-500">Time Format:</span>
                <span class="font-bold text-emerald-700">12-hour (hh:mm AM/PM)</span>
              </div>
              <div class="flex justify-between py-1">
                <span class="text-slate-500">System Platform:</span>
                <span class="font-mono text-slate-600">Python {sys.version.split(' ')[0]}</span>
              </div>
            </div>
          </div>

          <!-- COOPERATIVE TASK DESK CARD -->
          <div class="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-3 text-xs">
            <div class="flex items-center gap-2 pb-3 border-b border-slate-100">
              <i data-lucide="clipboard-list" class="w-4 h-4 text-purple-700"></i>
              <h3 class="font-bold text-sm text-slate-900">Task Management Desk</h3>
            </div>
            <p class="font-bold text-slate-800 text-sm">{ORG_NAME}</p>
            <p class="text-slate-500 leading-relaxed">
              Internal IT operations & task dispatch channel used by Cooperative Management to assign, prioritize, and track tasks for IT.
            </p>
          </div>
        </div>

        <!-- RIGHT TWO COLUMNS: EDITABLE FORMS -->
        <div class="lg:col-span-2 space-y-6">
          
          <!-- 1. ACCOUNT PROFILE FORM -->
          <div class="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-7 shadow-sm">
            <div class="flex items-center justify-between pb-4 mb-5 border-b border-slate-100">
              <div>
                <h2 class="text-base font-bold text-slate-900 flex items-center gap-2">
                  <i data-lucide="user" class="w-4 h-4 text-purple-700"></i>
                  <span>Profile Information</span>
                </h2>
                <p class="text-xs text-slate-500 mt-0.5">Update your display name and login username credentials.</p>
              </div>
              <span class="text-xs font-semibold px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 border border-slate-200">
                @{user_username}
              </span>
            </div>

            <form action="/settings/profile" method="POST" class="space-y-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label for="prof_name" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Display Name <span class="text-rose-500">*</span>
                  </label>
                  <input type="text" id="prof_name" name="name" required value="{user_name}"
                         class="input-field w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-50/50 text-slate-900 font-medium">
                </div>
                <div>
                  <label for="prof_username" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Login Username <span class="text-rose-500">*</span>
                  </label>
                  <div class="relative">
                    <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-xs pointer-events-none">@</span>
                    <input type="text" id="prof_username" name="username" required value="{user_username}" placeholder="username"
                           class="input-field w-full pl-8 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-50/50 text-slate-900 font-medium">
                  </div>
                </div>
              </div>

              <div>
                <label class="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                  Role Title
                </label>
                <input type="text" disabled value="{user_role}"
                       class="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-100 text-slate-500 font-medium cursor-not-allowed">
              </div>

              <div class="pt-2 flex justify-end">
                <button type="submit" class="px-5 py-2.5 rounded-xl bg-purple-700 hover:bg-purple-800 text-white font-bold text-xs sm:text-sm shadow-md shadow-purple-900/10 transition-all flex items-center gap-2 cursor-pointer">
                  <i data-lucide="check" class="w-4 h-4"></i>
                  <span>Save Profile</span>
                </button>
              </div>
            </form>
          </div>

          <!-- 2. CHANGE PASSWORD FORM -->
          <div class="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-7 shadow-sm">
            <div class="flex items-center justify-between pb-4 mb-5 border-b border-slate-100">
              <div>
                <h2 class="text-base font-bold text-slate-900 flex items-center gap-2">
                  <i data-lucide="lock" class="w-4 h-4 text-purple-700"></i>
                  <span>Security & Password</span>
                </h2>
                <p class="text-xs text-slate-500 mt-0.5">Ensure your account uses a secure password.</p>
              </div>
            </div>

            <form action="/settings/password" method="POST" class="space-y-4">
              <div>
                <label for="current_password" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Current Password <span class="text-rose-500">*</span>
                </label>
                <div class="relative">
                  <input type="password" id="current_password" name="current_password" required placeholder="Enter your current password"
                         class="input-field w-full pl-4 pr-11 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-50/50 text-slate-900">
                  <button type="button" onclick="togglePasswordVisibilityField('current_password', 'currentPwdIcon')" title="Show/Hide password"
                          class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-purple-700 transition-colors p-1 rounded-lg cursor-pointer focus:outline-none">
                    <i data-lucide="eye" id="currentPwdIcon" class="w-4 h-4"></i>
                  </button>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label for="new_password" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    New Password <span class="text-rose-500">*</span>
                  </label>
                  <div class="relative">
                    <input type="password" id="new_password" name="new_password" required placeholder="New password"
                           class="input-field w-full pl-4 pr-11 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-50/50 text-slate-900">
                    <button type="button" onclick="togglePasswordVisibilityField('new_password', 'newPwdIcon')" title="Show/Hide password"
                            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-purple-700 transition-colors p-1 rounded-lg cursor-pointer focus:outline-none">
                      <i data-lucide="eye" id="newPwdIcon" class="w-4 h-4"></i>
                    </button>
                  </div>
                </div>
                <div>
                  <label for="confirm_password" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                    Confirm New Password <span class="text-rose-500">*</span>
                  </label>
                  <div class="relative">
                    <input type="password" id="confirm_password" name="confirm_password" required placeholder="Repeat new password"
                           class="input-field w-full pl-4 pr-11 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-50/50 text-slate-900">
                    <button type="button" onclick="togglePasswordVisibilityField('confirm_password', 'confirmPwdIcon')" title="Show/Hide password"
                            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-purple-700 transition-colors p-1 rounded-lg cursor-pointer focus:outline-none">
                      <i data-lucide="eye" id="confirmPwdIcon" class="w-4 h-4"></i>
                    </button>
                  </div>
                </div>
              </div>

              <div class="pt-2 flex justify-end">
                <button type="submit" class="px-5 py-2.5 rounded-xl bg-purple-700 hover:bg-purple-800 text-white font-bold text-xs sm:text-sm shadow-md shadow-purple-900/10 transition-all flex items-center gap-2 cursor-pointer">
                  <i data-lucide="key" class="w-4 h-4"></i>
                  <span>Update Password</span>
                </button>
              </div>
            </form>
          </div>

          <!-- 3. NOTIFICATION & PREFERENCE SWITCHES -->
          <div class="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-7 shadow-sm">
            <div class="flex items-center justify-between pb-4 mb-5 border-b border-slate-100">
              <div>
                <h2 class="text-base font-bold text-slate-900 flex items-center gap-2">
                  <i data-lucide="bell" class="w-4 h-4 text-purple-700"></i>
                  <span>Notification Preferences</span>
                </h2>
                <p class="text-xs text-slate-500 mt-0.5">Control how and when you receive task and operational updates.</p>
              </div>
            </div>

            <form action="/settings/notifications" method="POST" class="space-y-4">
              <div class="divide-y divide-slate-100">
                <div class="flex items-center justify-between py-3">
                  <div>
                    <p class="text-xs sm:text-sm font-bold text-slate-800">Critical & High Priority Alert Beacon</p>
                    <p class="text-[11px] text-slate-500">Show visual pulsing alerts and banners for urgent operational issues.</p>
                  </div>
                  <label class="toggle-switch ml-4">
                    <input type="checkbox" name="urgent_alerts" {'checked' if settings.get('urgent_alerts') else ''}>
                    <span class="toggle-slider"></span>
                  </label>
                </div>

                <div class="flex items-center justify-between py-3">
                  <div>
                    <p class="text-xs sm:text-sm font-bold text-slate-800">Resolution & Timeline Updates</p>
                    <p class="text-[11px] text-slate-500">Notify Manager immediately when task status is changed to Resolved.</p>
                  </div>
                  <label class="toggle-switch ml-4">
                    <input type="checkbox" name="resolution_updates" {'checked' if settings.get('resolution_updates') else ''}>
                    <span class="toggle-slider"></span>
                  </label>
                </div>

                <div class="flex items-center justify-between py-3">
                  <div>
                    <p class="text-xs sm:text-sm font-bold text-slate-800">Daily Task Summary</p>
                    <p class="text-[11px] text-slate-500">Receive an operational breakdown of pending manager tasks every morning at 8:00 AM.</p>
                  </div>
                  <label class="toggle-switch ml-4">
                    <input type="checkbox" name="daily_summary" {'checked' if settings.get('daily_summary') else ''}>
                    <span class="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <div class="pt-3 flex justify-end">
                <button type="submit" class="px-5 py-2.5 rounded-xl bg-purple-700 hover:bg-purple-800 text-white font-bold text-xs sm:text-sm shadow-md shadow-purple-900/10 transition-all flex items-center gap-2 cursor-pointer">
                  <i data-lucide="check" class="w-4 h-4"></i>
                  <span>Save Preferences</span>
                </button>
              </div>
            </form>
          </div>

        </div>
      </div>
    </div>
    """

# ==========================================
# HTTP REQUEST HANDLER
# ==========================================

class TicketServerHandler(http.server.BaseHTTPRequestHandler):
    def get_current_user(self):
        cookie_header = self.headers.get("Cookie")
        if cookie_header:
            c = cookies.SimpleCookie()
            try:
                c.load(cookie_header)
                if "auth_user" in c:
                    username = c["auth_user"].value
                    return get_user_by_username(username)
            except Exception:
                pass
        return None

    def parse_post_data(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length).decode("utf-8")
        parsed = urllib.parse.parse_qs(post_body)
        return {k: v[0] for k, v in parsed.items()}

    def send_html_response(self, html_content, set_cookie_auth=None, clear_auth=False):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if set_cookie_auth:
            self.send_header("Set-Cookie", f"auth_user={set_cookie_auth}; Path=/; HttpOnly; SameSite=Lax")
        elif clear_auth:
            self.send_header("Set-Cookie", "auth_user=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def send_redirect(self, location, set_cookie_auth=None, clear_auth=False, remember_me=False):
        self.send_response(302)
        self.send_header("Location", location)
        if set_cookie_auth:
            max_age_str = "; Max-Age=2592000" if remember_me else ""
            self.send_header("Set-Cookie", f"auth_user={set_cookie_auth}; Path=/{max_age_str}; HttpOnly; SameSite=Lax")
        elif clear_auth:
            self.send_header("Set-Cookie", "auth_user=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # Logout route
        if path == "/logout":
            self.send_redirect("/login", clear_auth=True)
            return

        # Login page route
        if path == "/login":
            user = self.get_current_user()
            if user:
                self.send_redirect("/")
                return
            err = query.get("error", [None])[0]
            self.send_html_response(render_login_page(error_msg=err))
            return

        # Check authentication for all dashboard routes
        user = self.get_current_user()
        if not user:
            self.send_redirect("/login")
            return

        tickets = load_tickets_from_db()

        if path in ["/", ""]:
            view_mode = query.get("view_mode", ["kanban"])[0]
            status_f = query.get("status", ["all"])[0]
            priority_f = query.get("priority", ["all"])[0]
            category_f = query.get("category", ["all"])[0]
            search_q = query.get("q", [""])[0].strip()
            msg = query.get("msg", [None])[0]
            m_type = query.get("type", ["success"])[0]

            if user["role"] == "admin":
                content = render_admin_dashboard(tickets, user, view_mode, status_f, priority_f, category_f, search_q)
                page_html = render_layout(f"{APP_NAME} | Operations Console &bull; {ORG_NAME}", content, user=user, flash_msg=msg, flash_type=m_type)
            else:
                content = render_manager_dashboard(tickets, user, search_q)
                page_html = render_layout(f"{APP_NAME} | Management Portal &bull; {ORG_NAME}", content, user=user, flash_msg=msg, flash_type=m_type)
            
            self.send_html_response(page_html)

        elif path == "/submit":
            msg = query.get("msg", [None])[0]
            m_type = query.get("type", ["success"])[0]
            content = render_submit_ticket_form(user)
            page_html = render_layout(f"{APP_NAME} | Issue Ticket &bull; {ORG_NAME}", content, user=user, flash_msg=msg, flash_type=m_type)
            self.send_html_response(page_html)

        elif path == "/edit-ticket":
            t_id = query.get("id", [""])[0]
            ticket = get_ticket_from_db(t_id)
            if not ticket:
                self.send_redirect("/?msg=Ticket+not+found.&type=error")
                return
            if not can_manage_ticket(ticket, user):
                self.send_redirect(f"/ticket?id={t_id}&msg=Access+denied.+Only+the+author+who+created+this+ticket+can+edit+it.&type=error")
                return
            msg = query.get("msg", [None])[0]
            m_type = query.get("type", ["success"])[0]
            content = render_edit_ticket_form(ticket, user)
            page_html = render_layout(f"{APP_NAME} | Edit Ticket {ticket['id']}", content, user=user, flash_msg=msg, flash_type=m_type)
            self.send_html_response(page_html)

        elif path == "/settings":
            msg = query.get("msg", [None])[0]
            m_type = query.get("type", ["success"])[0]
            content = render_settings_page(user)
            page_html = render_layout(f"{APP_NAME} | Settings &bull; {ORG_NAME}", content, user=user, flash_msg=msg, flash_type=m_type)
            self.send_html_response(page_html)

        elif path == "/ticket":
            t_id = query.get("id", [""])[0]
            msg = query.get("msg", [None])[0]
            m_type = query.get("type", ["success"])[0]
            ticket = get_ticket_from_db(t_id)
            if not ticket:
                self.send_redirect("/?msg=Ticket+not+found.&type=error")
                return
            content = render_ticket_detail(ticket, user)
            page_html = render_layout(f"{APP_NAME} - {ticket['id']}: {ticket['subject']}", content, user=user, flash_msg=msg, flash_type=m_type)
            self.send_html_response(page_html)

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        post_data = self.parse_post_data()

        # Handle login POST
        if path == "/login":
            username = post_data.get("username", "").strip()
            password = post_data.get("password", "")
            remember = post_data.get("remember") in ["on", "true", "1"]

            user = get_user_by_credentials(username, password)
            if user:
                self.send_redirect("/", set_cookie_auth=user["username"], remember_me=remember)
            else:
                self.send_redirect("/login?error=Invalid+credentials.+Please+check+your+username+and+password.")
            return

        # Auth check for mutations
        user = self.get_current_user()
        if not user:
            self.send_redirect("/login")
            return

        if path == "/submit":
            full_name = post_data.get("full_name", "").strip() or user["name"]
            email = post_data.get("email", "").strip() or user["email"]
            issue_type = post_data.get("issue_type", "Web Bug/Error")
            priority = post_data.get("priority", "Medium")
            subject = post_data.get("subject", "").strip()
            description = post_data.get("description", "").strip()

            if subject and description:
                is_admin = (user.get("role") == "admin")
                submitter_role = "IT Specialist" if is_admin else user.get("role_title", "Cooperative General Manager")
                new_id = insert_ticket(
                    full_name=full_name,
                    email=email,
                    submitter_role=submitter_role,
                    issue_type=issue_type,
                    priority=priority,
                    subject=subject,
                    description=description,
                    submitter_username=user.get("username"),
                    submitter_is_admin=is_admin
                )
                self.send_redirect(f"/ticket?id={new_id}&msg=Ticket+{new_id}+issued+successfully!&type=success")
                return
            self.send_redirect("/submit?msg=Please+fill+in+all+required+fields.&type=error")

        elif path == "/edit-ticket":
            t_id = post_data.get("id", "").strip()
            ticket = get_ticket_from_db(t_id)
            if not ticket:
                self.send_redirect("/?msg=Ticket+not+found.&type=error")
                return
            if not can_manage_ticket(ticket, user):
                self.send_redirect(f"/ticket?id={t_id}&msg=Access+denied.+Only+the+author+who+created+this+ticket+can+edit+it.&type=error")
                return

            subject = post_data.get("subject", "").strip()
            description = post_data.get("description", "").strip()
            issue_type = post_data.get("issue_type", ticket.get("issue_type", "Web Bug/Error"))
            priority = post_data.get("priority", ticket.get("priority", "Medium"))

            if not subject or not description:
                self.send_redirect(f"/edit-ticket?id={t_id}&msg=Subject+and+description+are+required.&type=error")
                return

            editor_name = user.get("name", "Author")
            editor_role = user.get("role_title", "Author")
            update_ticket_content_db(t_id, subject, description, issue_type, priority, editor_name=editor_name, editor_role=editor_role)
            self.send_redirect(f"/ticket?id={t_id}&msg=Ticket+{t_id}+has+been+successfully+updated!&type=success")
            return

        elif path == "/delete-ticket":
            t_id = post_data.get("id", "").strip()
            ticket = get_ticket_from_db(t_id)
            if not ticket:
                self.send_redirect("/?msg=Ticket+not+found.&type=error")
                return
            if not can_manage_ticket(ticket, user):
                self.send_redirect(f"/ticket?id={t_id}&msg=Access+denied.+Only+the+author+who+created+this+ticket+can+delete+it.&type=error")
                return

            delete_ticket_db(t_id)
            self.send_redirect(f"/?msg=Ticket+{t_id}+has+been+permanently+deleted.&type=success")
            return

        elif path == "/settings/profile":
            new_name = post_data.get("name", "").strip()
            new_username = post_data.get("username", "").strip()

            if not new_name:
                self.send_redirect("/settings?msg=Display+name+cannot+be+empty.&type=error")
                return

            if not new_username:
                self.send_redirect("/settings?msg=Login+username+cannot+be+empty.&type=error")
                return

            safe_username = "".join(c for c in new_username if c.isalnum() or c in "_-.")
            if safe_username != new_username:
                self.send_redirect("/settings?msg=Username+can+only+contain+letters,+numbers,+underscores,+and+dots.&type=error")
                return

            conn = get_db()
            with conn:
                if new_username.lower() != user["username"].lower():
                    existing = conn.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?) AND id != ?", (new_username, user["id"])).fetchone()
                    if existing:
                        conn.close()
                        self.send_redirect("/settings?msg=Username+is+already+taken+by+another+account.&type=error")
                        return

                old_username = user["username"]
                conn.execute("UPDATE users SET name = ?, username = ? WHERE id = ?", (new_name, new_username, user["id"]))

                if old_username != new_username:
                    conn.execute("UPDATE user_settings SET username = ? WHERE username = ?", (new_username, old_username))

            conn.close()
            self.send_redirect("/settings?msg=Profile+and+login+username+updated+successfully!&type=success", set_cookie_auth=new_username)
            return

        elif path == "/settings/password":
            curr_pwd = post_data.get("current_password", "")
            new_pwd = post_data.get("new_password", "").strip()
            confirm_pwd = post_data.get("confirm_password", "").strip()

            if not verify_user_password(user["password"], curr_pwd):
                self.send_redirect("/settings?msg=Incorrect+current+password.&type=error")
                return

            if not new_pwd or new_pwd != confirm_pwd:
                self.send_redirect("/settings?msg=New+passwords+do+not+match+or+are+empty.&type=error")
                return

            conn = get_db()
            with conn:
                conn.execute("UPDATE users SET password = ? WHERE id = ?", (new_pwd, user["id"]))
            conn.close()
            self.send_redirect("/settings?msg=Password+updated+successfully!&type=success")
            return

        elif path == "/settings/notifications":
            urgent = 1 if post_data.get("urgent_alerts") else 0
            resol = 1 if post_data.get("resolution_updates") else 0
            daily = 1 if post_data.get("daily_summary") else 0
            save_user_settings(user["username"], urgent, resol, daily)
            self.send_redirect("/settings?msg=Notification+preferences+saved+successfully!&type=success")
            return

        elif path == "/update-status":
            t_id = post_data.get("id")
            new_status = post_data.get("status")
            if t_id and new_status in ["Open", "In Progress", "Resolved", "Closed"]:
                author_name = user["name"] if user else "IT Specialist"
                update_ticket_status_db(t_id, new_status, author=author_name)
            self.send_redirect(f"/ticket?id={t_id}")

        elif path == "/update-priority":
            t_id = post_data.get("id")
            new_priority = post_data.get("priority")
            if t_id and new_priority in ["Low", "Medium", "High", "Critical"]:
                author_name = user["name"] if user else "IT Specialist"
                update_ticket_priority_db(t_id, new_priority, author=author_name)
            self.send_redirect(f"/ticket?id={t_id}")

        elif path == "/add-comment":
            t_id = post_data.get("id")
            comment_text = post_data.get("comment", "").strip()
            is_internal = post_data.get("is_internal") == "true"
            if t_id and comment_text:
                if user["role"] == "admin":
                    author = user["name"] if user.get("name") else "IT Specialist"
                    role_label = "IT Specialist"
                    action = "Internal Note" if is_internal else "IT Update"
                else:
                    author = user["name"]
                    role_label = "Manager"
                    action = "Management Follow-up"
                    is_internal = False

                add_ticket_comment_db(t_id, author, role_label, action, comment_text, is_internal)
            self.send_redirect(f"/ticket?id={t_id}")

        elif path == "/reset":
            reset_db_data()
            self.send_redirect("/")

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

# ==========================================
# WSGI ADAPTER (FOR PYTHONANYWHERE & CLOUD)
# ==========================================

class WSGIHandlerAdapter:
    def __init__(self, environ):
        self.environ = environ
        self.path = environ.get("PATH_INFO", "/")
        qs = environ.get("QUERY_STRING", "")
        if qs:
            self.path += "?" + qs
        self.command = environ.get("REQUEST_METHOD", "GET")
        self.headers = {}
        for k, v in environ.items():
            if k.startswith("HTTP_"):
                header_name = k[5:].replace("_", "-").title()
                self.headers[header_name] = v
            elif k in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                self.headers[k.replace("_", "-").title()] = v
        self.rfile = environ.get("wsgi.input") or io.BytesIO(b"")
        self.wfile = io.BytesIO()
        self.status_code = 200
        self.response_headers = []

    def get_current_user(self):
        cookie_header = self.headers.get("Cookie")
        if cookie_header:
            c = cookies.SimpleCookie()
            try:
                c.load(cookie_header)
                if "auth_user" in c:
                    username = c["auth_user"].value
                    return get_user_by_username(username)
            except Exception:
                pass
        return None

    def parse_post_data(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length).decode("utf-8") if self.rfile else ""
        parsed = urllib.parse.parse_qs(post_body)
        return {k: v[0] for k, v in parsed.items()}

    def send_response(self, code, message=None):
        self.status_code = code

    def send_header(self, keyword, value):
        self.response_headers.append((keyword, str(value)))

    def end_headers(self):
        pass

    def send_html_response(self, html_content, set_cookie_auth=None, clear_auth=False):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if set_cookie_auth:
            self.send_header("Set-Cookie", f"auth_user={set_cookie_auth}; Path=/; HttpOnly; SameSite=Lax")
        elif clear_auth:
            self.send_header("Set-Cookie", "auth_user=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def send_redirect(self, location, set_cookie_auth=None, clear_auth=False, remember_me=False):
        self.send_response(302)
        self.send_header("Location", location)
        if set_cookie_auth:
            max_age_str = "; Max-Age=2592000" if remember_me else ""
            self.send_header("Set-Cookie", f"auth_user={set_cookie_auth}; Path=/{max_age_str}; HttpOnly; SameSite=Lax")
        elif clear_auth:
            self.send_header("Set-Cookie", "auth_user=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
        self.end_headers()

def application(environ, start_response):
    init_db()
    handler = WSGIHandlerAdapter(environ)
    if handler.command == "GET":
        TicketServerHandler.do_GET(handler)
    elif handler.command == "POST":
        TicketServerHandler.do_POST(handler)
    else:
        handler.send_response(405)
        handler.send_header("Content-Type", "text/plain")
        handler.end_headers()
        handler.wfile.write(b"Method Not Allowed")

    status_phrases = {
        200: "200 OK",
        302: "302 Found",
        404: "404 Not Found",
        405: "405 Method Not Allowed"
    }
    status_str = status_phrases.get(handler.status_code, f"{handler.status_code} Status")
    start_response(status_str, handler.response_headers)
    return [handler.wfile.getvalue()]

def main():
    print(f"================================================================")
    print(f" onIT — IT Ticketing System")
    print(f" Organization: {ORG_NAME}")
    print(f" Database: SQLite 3 ({DB_FILE})")
    print(f" Running on http://{HOST}:{PORT}/ (Local: http://127.0.0.1:{PORT}/)")
    print(f"================================================================")
    init_db()
    server = http.server.HTTPServer((HOST, PORT), TicketServerHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
