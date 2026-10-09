
const Database = require("better-sqlite3");
const path = require("path");

// Create the temporary Digi-CoC database
const dbPath = path.join(__dirname, "digi-coc-dev.db");
const db = new Database(dbPath);

// Enable foreign-key relationships
db.pragma("foreign_keys = ON");

// Confirm the database is ready
console.log("Digi-CoC development database connected.");
db.exec(`
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT UNIQUE NOT NULL,
        case_title TEXT NOT NULL,
        case_type TEXT,
        status TEXT NOT NULL DEFAULT 'Open',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evidence_id TEXT UNIQUE NOT NULL,
        case_id TEXT NOT NULL,
        item_name TEXT NOT NULL,
        description TEXT,
        tag_type TEXT,
        tag_id TEXT UNIQUE,
        current_status TEXT NOT NULL DEFAULT 'Registered',
        current_custodian_id TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (case_id) REFERENCES cases(case_id)
    );
`);

console.log("Digi-CoC evidence table ready.");

db.exec(`
    CREATE TABLE IF NOT EXISTS personnel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        personnel_id TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        fingerprint_id INTEGER UNIQUE,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
`);

console.log("Digi-CoC personnel table ready.");

db.exec(`
    CREATE TABLE IF NOT EXISTS custody_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        evidence_id TEXT NOT NULL,
        from_personnel_id TEXT,
        to_personnel_id TEXT NOT NULL,
        transfer_reason TEXT NOT NULL,
        location TEXT,
        verification_method TEXT,
        event_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (evidence_id)
            REFERENCES evidence(evidence_id),
        FOREIGN KEY (from_personnel_id)
            REFERENCES personnel(personnel_id),
        FOREIGN KEY (to_personnel_id)
            REFERENCES personnel(personnel_id)
    );
`);
// Add tamper-detection fields to existing custody event tables.
const custodyColumns = db.prepare(
    "PRAGMA table_info(custody_events)"
).all();

if (!custodyColumns.some(column => column.name === "previous_hash")) {
    db.exec(`
        ALTER TABLE custody_events
        ADD COLUMN previous_hash TEXT;
    `);
}

if (!custodyColumns.some(column => column.name === "event_hash")) {
    db.exec(`
        ALTER TABLE custody_events
        ADD COLUMN event_hash TEXT;
    `);
}

console.log("Custody event hash fields checked.");
console.log("Digi-CoC custody events table ready.");

console.log("Digi-CoC cases table ready.");
// Add the current custodian field to existing databases if needed
const evidenceColumns = db.prepare(
    "PRAGMA table_info(evidence)"
).all();

if (!evidenceColumns.some(column => column.name === "current_custodian_id")) {
    db.exec(`
        ALTER TABLE evidence
        ADD COLUMN current_custodian_id TEXT;
    `);

    console.log("Evidence current custodian field added.");
}
module.exports = db;
