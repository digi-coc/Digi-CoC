
const express = require("express");
const db = require("./database");

const app = express();
const PORT = 3000;

// Allow the server to read JSON data
app.use(express.json());

// Test route
app.get("/", (req, res) => {
    res.json({
        message: "Digi-CoC backend is running!",
        status: "success"
    });
});
// Get all cases
app.get("/api/cases", (req, res) => {
    const cases = db.prepare(
        "SELECT * FROM cases ORDER BY id DESC"
    ).all();

    res.json(cases);
});

 // Create a new case
app.post("/api/cases", (req, res) => {
    const { case_id, case_title, case_type } = req.body;

    if (!case_id || !case_title) {
        return res.status(400).json({
            error: "Case ID and case title are required."
        });
    }

    try {
        const result = db.prepare(`
            INSERT INTO cases (case_id, case_title, case_type)
            VALUES (?, ?, ?)
        `).run(case_id, case_title, case_type || null);

        const newCase = db.prepare(
            "SELECT * FROM cases WHERE id = ?"
        ).get(result.lastInsertRowid);

        res.status(201).json(newCase);
    } catch (error) {
        if (error.code === "SQLITE_CONSTRAINT_UNIQUE") {
            return res.status(409).json({
                error: "That case ID already exists."
            });
        }

        console.error(error);
        res.status(500).json({
            error: "Could not create case."
        });
    }
});

 // Get all evidence
app.get("/api/evidence", (req, res) => {
    const evidence = db.prepare(`
        SELECT * FROM evidence
        ORDER BY id DESC
    `).all();

    res.json(evidence);
});

 // Register a new evidence item
app.post("/api/evidence", (req, res) => {
    const {
        evidence_id,
        case_id,
        item_name,
        description,
        tag_type,
        tag_id
    } = req.body;

    if (!evidence_id || !case_id || !item_name) {
        return res.status(400).json({
            error: "Evidence ID, case ID, and item name are required."
        });
    }

    try {
        const result = db.prepare(`
            INSERT INTO evidence (
                evidence_id,
                case_id,
                item_name,
                description,
                tag_type,
                tag_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        `).run(
            evidence_id,
            case_id,
            item_name,
            description || null,
            tag_type || null,
            tag_id || null
        );

        const newEvidence = db.prepare(
            "SELECT * FROM evidence WHERE id = ?"
        ).get(result.lastInsertRowid);

        res.status(201).json(newEvidence);
    } catch (error) {
        if (error.code === "SQLITE_CONSTRAINT_UNIQUE") {
            return res.status(409).json({
                error: "That evidence ID or tag ID already exists."
            });
        }

        if (error.code === "SQLITE_CONSTRAINT_FOREIGNKEY") {
            return res.status(400).json({
                error: "The specified case does not exist."
            });
        }

        console.error(error);
        res.status(500).json({
            error: "Could not register evidence."
        });
    }
});

 // Get all personnel
app.get("/api/personnel", (req, res) => {
    const personnel = db.prepare(`
        SELECT
            id,
            personnel_id,
            full_name,
            role,
            fingerprint_id,
            is_active,
            created_at
        FROM personnel
        ORDER BY id DESC
    `).all();

    res.json(personnel);
});

 // Register personnel
app.post("/api/personnel", (req, res) => {
    const {
        personnel_id,
        full_name,
        role,
        fingerprint_id
    } = req.body;

    if (!personnel_id || !full_name || !role) {
        return res.status(400).json({
            error: "Personnel ID, full name, and role are required."
        });
    }

    try {
        const result = db.prepare(`
            INSERT INTO personnel (
                personnel_id,
                full_name,
                role,
                fingerprint_id
            )
            VALUES (?, ?, ?, ?)
        `).run(
            personnel_id,
            full_name,
            role,
            fingerprint_id ?? null
        );

        const newPerson = db.prepare(`
            SELECT
                id,
                personnel_id,
                full_name,
                role,
                fingerprint_id,
                is_active,
                created_at
            FROM personnel
            WHERE id = ?
        `).get(result.lastInsertRowid);

        res.status(201).json(newPerson);
    } catch (error) {
        if (error.code === "SQLITE_CONSTRAINT_UNIQUE") {
            return res.status(409).json({
                error: "That personnel ID or fingerprint ID already exists."
            });
        }

        console.error(error);
        res.status(500).json({
            error: "Could not register personnel."
        });
    }
});

 // Get all custody events
app.get("/api/custody-events", (req, res) => {
    const events = db.prepare(`
        SELECT *
        FROM custody_events
        ORDER BY id DESC
    `).all();

    res.json(events);
});

app.post("/api/custody-events", (req, res) => {
    const {
        event_id,
        evidence_id,
        from_personnel_id,
        to_personnel_id,
        transfer_reason,
        location,
        verification_method
    } = req.body;

    if (
        !event_id ||
        !evidence_id ||
        !to_personnel_id ||
        !transfer_reason
    ) {
        return res.status(400).json({
            error: "Event ID, evidence ID, receiving personnel ID, and transfer reason are required."
        });
    }

    // This route currently supports development testing only.
    if (verification_method !== "SIMULATED-TEST-ONLY") {
        return res.status(400).json({
            error: "Real biometric verification is not integrated yet. Use the development test verification method only."
        });
    }

    try {
        const recordTransfer = db.transaction(() => {
            const evidence = db.prepare(`
                SELECT evidence_id, current_custodian_id
                FROM evidence
                WHERE evidence_id = ?
            `).get(evidence_id);

            if (!evidence) {
                throw new Error("EVIDENCE_NOT_FOUND");
            }

            const receiver = db.prepare(`
                SELECT personnel_id, is_active
                FROM personnel
                WHERE personnel_id = ?
            `).get(to_personnel_id);

            if (!receiver || receiver.is_active !== 1) {
                throw new Error("INVALID_RECEIVER");
            }

            // If custody has already been assigned, the sender
            // must match the currently recorded custodian.
            if (evidence.current_custodian_id !== null) {
                if (
                    !from_personnel_id ||
                    from_personnel_id !== evidence.current_custodian_id
                ) {
                    throw new Error("SENDER_MISMATCH");
                }

                const sender = db.prepare(`
                    SELECT personnel_id, is_active
                    FROM personnel
                    WHERE personnel_id = ?
                `).get(from_personnel_id);

                if (!sender || sender.is_active !== 1) {
                    throw new Error("INVALID_SENDER");
                }
            } else if (from_personnel_id) {
                throw new Error("NO_PREVIOUS_CUSTODIAN");
            }

            // Record the custody event.
            const result = db.prepare(`
                INSERT INTO custody_events (
                    event_id,
                    evidence_id,
                    from_personnel_id,
                    to_personnel_id,
                    transfer_reason,
                    location,
                    verification_method
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            `).run(
                event_id,
                evidence_id,
                from_personnel_id || null,
                to_personnel_id,
                transfer_reason,
                location || null,
                verification_method
            );

            // Update the custodian in the same transaction.
            db.prepare(`
                UPDATE evidence
                SET current_custodian_id = ?,
                    current_status = 'In Custody'
                WHERE evidence_id = ?
            `).run(to_personnel_id, evidence_id);

            return db.prepare(`
                SELECT * FROM custody_events WHERE id = ?
            `).get(result.lastInsertRowid);
        });

        const newEvent = recordTransfer();
console.log("Custody transfer saved:", newEvent.event_id);
        return res.status(201).json({
            message: "Development custody transfer recorded.",
            warning: "SIMULATED TEST ONLY — this does not prove biometric verification.",
            event: newEvent
        });

    } catch (error) {
        const errors = {
            EVIDENCE_NOT_FOUND: {
                status: 404,
                message: "Evidence record not found."
            },
            INVALID_RECEIVER: {
                status: 400,
                message: "Receiving personnel does not exist or is inactive."
            },
            INVALID_SENDER: {
                status: 400,
                message: "Sending personnel does not exist or is inactive."
            },
            SENDER_MISMATCH: {
                status: 409,
                message: "Transfer rejected: sender is not the recorded current custodian."
            },
            NO_PREVIOUS_CUSTODIAN: {
                status: 409,
                message: "Transfer rejected: evidence has no recorded current custodian, so a sender cannot be specified."
            }
        };

        const knownError = errors[error.message];

        if (knownError) {
            return res.status(knownError.status).json({
                error: knownError.message
            });
        }

        if (error.code === "SQLITE_CONSTRAINT_UNIQUE") {
            return res.status(409).json({
                error: "That event ID already exists."
            });
        }

        console.error("Custody transfer failed:", error);

        return res.status(500).json({
            error: "Could not record custody transfer."
        });
    }
});app.listen(PORT, () => {
    console.log(`Digi-CoC backend running at http://localhost:${PORT}`);
});
