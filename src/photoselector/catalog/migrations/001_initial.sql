CREATE TABLE IF NOT EXISTS photo (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    filename TEXT NOT NULL,
    mtime_ns INTEGER NOT NULL,
    size_bytes INTEGER NOT NULL,
    taken_at TEXT,
    width INTEGER,
    height INTEGER,
    orientation INTEGER NOT NULL DEFAULT 1,
    format TEXT NOT NULL,
    phash TEXT,
    group_id INTEGER,
    stars INTEGER CHECK (stars IS NULL OR (stars >= 1 AND stars <= 5)),
    color TEXT CHECK (
        color IS NULL
        OR color IN ('red', 'yellow', 'green', 'blue', 'purple')
    ),
    rotate_quarters INTEGER NOT NULL DEFAULT 0
        CHECK (rotate_quarters BETWEEN 0 AND 3),
    scanned_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS selection (
    photo_id INTEGER PRIMARY KEY REFERENCES photo (id) ON DELETE CASCADE,
    rating TEXT NOT NULL CHECK (rating IN ('pick', 'reject')),
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS action_log (
    id INTEGER PRIMARY KEY,
    seq INTEGER NOT NULL UNIQUE,
    op TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS project_data (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS drive_auth (
    account_id TEXT PRIMARY KEY,
    email TEXT,
    folder_id TEXT,
    folder_name TEXT,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_photo_filename ON photo (filename);
CREATE INDEX IF NOT EXISTS idx_photo_taken_at ON photo (taken_at);
CREATE INDEX IF NOT EXISTS idx_photo_group_id ON photo (group_id);
CREATE INDEX IF NOT EXISTS idx_selection_rating ON selection (rating);
