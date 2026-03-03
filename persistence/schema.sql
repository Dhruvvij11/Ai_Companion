CREATE TABLE IF NOT EXISTS reminders (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    trigger_at INTEGER NOT NULL,
    recurrence TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    triggered_at INTEGER,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_reminders_status_trigger_at
ON reminders(status, trigger_at);
