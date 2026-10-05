# onIT — IT Ticketing System

> *"We're on it."* Fast IT support and ticket tracking for **UC-METC Multipurpose Cooperative**.

A modern, responsive IT Ticketing System web application tailored for daily operations by a **solo IT developer** managing the **UC-METC Multipurpose Cooperative** website, systems, and internal tech operations.

Built using **Pure Python 3.12 (Standard Library)**, **SQLite 3** relational database, **Tailwind CSS (Solid Purple theme)**, and zero external package dependencies.

---

## 🚀 Quick Start

### Option 1: Double-click to run (Windows)
Double-click [`run.bat`](file:///c:/Users/Admin/Documents/Coop%20Projects/Ticket-System/run.bat) in the root folder.

### Option 2: Run via Terminal
```powershell
python app.py
```
Then open your browser to: **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 🗄️ Relational Database (SQLite 3)

The application uses an **ACID-compliant SQLite 3 database** stored at [`data/onit.db`](file:///c:/Users/Admin/Documents/Coop%20Projects/Ticket-System/data/onit.db) for reliable daily production usage:

### Schema Overview:
- **`users`**:
  - `id` (INTEGER PRIMARY KEY)
  - `username`, `password`, `name`, `email`, `role`, `role_title`, `department`, `created_at`
- **`tickets`**:
  - `id` (TEXT PRIMARY KEY e.g. `TK-101`)
  - `submitter_name`, `submitter_email`, `submitter_role`, `issue_type`, `priority`, `status`, `subject`, `description`, `created_at`, `updated_at`
- **`ticket_timeline`**:
  - `id` (INTEGER PRIMARY KEY)
  - `ticket_id` (FOREIGN KEY REFERENCES `tickets(id)` ON DELETE CASCADE)
  - `timestamp`, `author`, `role`, `action`, `content`, `is_internal`
- **Indexes**:
  - `idx_tickets_status`, `idx_tickets_priority`, `idx_timeline_ticket` for fast search and query performance.

### Daily Backup:
To back up the system at the end of the day, copy the file:
```powershell
Copy-Item "data\onit.db" "data\onit_backup_$(Get-Date -Format 'yyyyMMdd').db"
```

---

## 🔐 Authentication & Roles

The system uses a clean, production **Login Page** (`/login`) with standard username and password fields (no demo buttons):

| Role | Username | Password | Dashboard View |
| :--- | :--- | :--- | :--- |
| **Cooperative General Manager** | `manager` | `manager` (or `manager123`) | **Cooperative Management Desk** (Issues tickets to IT, tracks progress) |
| **Solo IT Specialist / Lead** | `it` | `it` (or `it123`, `admin`) | **onIT Operations Console** (Kanban, Master Table, Triage, Notes) |


---

## 🎯 Primary Portals

### 1. 🎒 Cooperative Staff Portal
- **Personalized Greeting**: Greets the authenticated faculty/staff member.
- **Summary Metrics**: Real-time counts for *Total Submitted*, *Open & Active*, and *Resolved* tickets directly from SQL.
- **Submit New Ticket** ([`/submit`](http://127.0.0.1:5000/submit)):
  - Full Name & Email (auto-filled from database user account)
  - Issue Type: *Web Bug/Error*, *New Feature Request*, *Content Update*, *Password/Login Issue*
  - Priority: *Low*, *Medium*, *High*, *Critical*
  - Subject / Title & Detailed Description
- **Interactive "My Tickets" Table**:
  - Ticket ID, Date, Subject, Category, Priority, and Status Badges.
  - Colored badges: **Open (Blue)**, **In Progress (Orange)**, **Resolved (Green)**, **Closed (Slate)**.
  - Row click directly opens the full ticket resolution timeline.

### 2. ⚡ onIT Operations Console (IT Lead & System Developer)
- **Master Metrics Bar**: Total Active Tickets, Open Backlog, In Progress, Resolved, with critical alert beacons.
- **Dual View Modes**:
  - **Kanban Board**: 4 columns (*Open Backlog*, *In Progress*, *Resolved*, *Archived/Closed*).
  - **Master Data Table**: Tabular view with instant inline status dropdown triage.
- **Multi-Factor Filters**: Filter by Status, Priority, Category, or Keyword Search.
- **Ticket Detail & Triage**:
  - Change Status (*Open &rarr; In Progress &rarr; Resolved &rarr; Closed*).
  - Adjust Priority if staff miscategorized it.
  - **Timeline & Developer Updates**:
    - Add internal developer notes (e.g., *"Working on the fix now"* or *"Fixed the login page bug"*).
    - Mark notes as private **Internal Admin Notes** (visible only in IT Admin view).
    - One-click status shortcuts: *"Start Work"* (amber) and *"Mark Fixed"* (emerald).

---

## 📂 Project Architecture

```
Ticket-System/
├── app.py                     # Pure Python HTTP server & SQLite 3 ORM layer
├── run.bat                    # One-click Windows starter script
├── data/
│   └── onit.db                # SQLite 3 ACID relational database
└── README.md                  # System documentation
```
