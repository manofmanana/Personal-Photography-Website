PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  kind TEXT NOT NULL DEFAULT 'Journal' CHECK (kind IN ('Journal','Note','Essay')),
  body TEXT NOT NULL,
  image_url TEXT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subscribers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  message TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 🔹 New table for Gallery photos
CREATE TABLE IF NOT EXISTS gallery (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT NOT NULL, -- relative path to file in static/gallery_uploads/
  tag TEXT NOT NULL CHECK (tag IN ('nature','portraits','candids','experimental')),
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
