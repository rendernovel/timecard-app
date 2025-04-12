-- Initialize the database schema for timecard application with authentication

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0,
    created_at TEXT
);

-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create time_entries table
CREATE TABLE IF NOT EXISTS time_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    clock_in TEXT,
    clock_out TEXT,
    total_hours REAL,
    status TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees (id)
);

-- Create break_entries table
CREATE TABLE IF NOT EXISTS break_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time_entry_id INTEGER NOT NULL,
    start_time TEXT,
    end_time TEXT,
    duration REAL,
    FOREIGN KEY (time_entry_id) REFERENCES time_entries (id)
);

-- Create export_logs table
CREATE TABLE IF NOT EXISTS export_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    export_date TEXT,
    status TEXT,
    file_path TEXT,
    recipient_email TEXT
);

-- Insert admin user
INSERT OR IGNORE INTO users (username, email, password_hash, is_admin, created_at) 
VALUES 
    ('admin', 'admin@example.com', 'pbkdf2:sha256:600000$X20U9bNU9WvFzAiF$d50e74b3c8eeaaf43bd55087c3a63e71d45d38a3d69e8950f5f92f33b9927838', 1, datetime('now'));

-- Insert admin as employee
INSERT OR IGNORE INTO employees (user_id, name, email, created_at)
SELECT id, 'Administrator', email, datetime('now')
FROM users
WHERE username = 'admin'
AND NOT EXISTS (SELECT 1 FROM employees WHERE email = 'admin@example.com');
