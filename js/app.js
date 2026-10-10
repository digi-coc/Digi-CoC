/* =========================================
   DIGI-CoC
   FRONTEND DASHBOARD
========================================= */


/*
    TEMPORARY FRONTEND DATA

    This is ONLY for testing the frontend.

    Later the backend developer will replace
    these arrays with real API/database data.
*/


const dashboardData = {

    /* =====================================
       CASES
    ===================================== */

    cases: [

        {
            caseNumber: "DC-2026-001",
            firNumber: "FIR-123/2026",
            status: "Active",
            evidenceCount: 2
        },

        {
            caseNumber: "DC-2026-002",
            firNumber: "FIR-124/2026",
            status: "Active",
            evidenceCount: 1
        },

        {
            caseNumber: "DC-2026-003",
            firNumber: "FIR-118/2026",
            status: "Closed",
            evidenceCount: 0
        }

    ],


    /* =====================================
       EVIDENCE
    ===================================== */

    evidence: [

        {
            evidenceID: "EV-2026-001",
            caseID: "DC-2026-001",
            status: "In Custody"
        },

        {
            evidenceID: "EV-2026-002",
            caseID: "DC-2026-001",
            status: "In Custody"
        },

        {
            evidenceID: "EV-2026-003",
            caseID: "DC-2026-002",
            status: "Flagged"
        }

    ],


    /* =====================================
       PERSONNEL
    ===================================== */

    personnel: [

        {
            personnelID: "P-001",
            name: "Personnel 001",
            role: "Forensic Officer",
            status: "Active"
        },

        {
            personnelID: "P-002",
            name: "Personnel 002",
            role: "Evidence Handler",
            status: "Active"
        },

        {
            personnelID: "P-003",
            name: "Personnel 003",
            role: "Evidence Handler",
            status: "Active"
        }

    ],


    /* =====================================
       CUSTODY EVENTS
    ===================================== */

    custodyEvents: [

        {
            eventID: "COC-2026-001",
            evidenceID: "EV-2026-001",
            personnelID: "P-001",
            status: "Verified"
        },

        {
            eventID: "COC-2026-002",
            evidenceID: "EV-2026-002",
            personnelID: "P-002",
            status: "Verified"
        },

        {
            eventID: "COC-2026-003",
            evidenceID: "EV-2026-003",
            personnelID: "P-003",
            status: "Flagged"
        }

    ],


    /* =====================================
       RECENT ACTIVITY
    ===================================== */

    activity: [

        {
            title: "Evidence EV-2026-001 registered",
            time: "Today, 09:21"
        },

        {
            title: "Custody transfer verified for EV-2026-001",
            time: "Today, 10:05"
        },

        {
            title: "Fingerprint verification successful",
            time: "Today, 10:18"
        },

        {
            title: "Unauthorized fingerprint attempt detected",
            time: "Today, 10:42"
        },

        {
            title: "Personnel P-004 registered",
            time: "Today, 11:03"
        },

        {
            title: "RFID Scanner DEV-002 reported offline",
            time: "Today, 11:26"
        }

    ]

};


/* =========================================
   UPDATE DASHBOARD STATISTICS
========================================= */

function updateDashboardStatistics() {

    const activeCasesCount =
        document.getElementById("activeCasesCount");

    const evidenceCount =
        document.getElementById("evidenceCount");

    const personnelCount =
        document.getElementById("personnelCount");

    const custodyEventsCount =
        document.getElementById("custodyEventsCount");


    /* -------------------------------------
       ACTIVE CASES
    ------------------------------------- */

    const activeCases =
        dashboardData.cases.filter(
            caseItem =>
                caseItem.status.toLowerCase() === "active"
        );


    if (activeCasesCount) {

        activeCasesCount.textContent =
            activeCases.length;

    }


    /* -------------------------------------
       TOTAL EVIDENCE
    ------------------------------------- */

    if (evidenceCount) {

        evidenceCount.textContent =
            dashboardData.evidence.length;

    }


    /* -------------------------------------
       TOTAL PERSONNEL
    ------------------------------------- */

    if (personnelCount) {

        personnelCount.textContent =
            dashboardData.personnel.length;

    }


    /* -------------------------------------
       CUSTODY EVENTS
    ------------------------------------- */

    if (custodyEventsCount) {

        custodyEventsCount.textContent =
            dashboardData.custodyEvents.length;

    }

}


/* =========================================
   RENDER RECENT CASES
========================================= */

function renderRecentCases() {

    const table =
        document.getElementById("recentCasesTable");


    if (!table) {
        return;
    }


    /* -------------------------------------
       EMPTY STATE
    ------------------------------------- */

    if (dashboardData.cases.length === 0) {

        table.innerHTML = `
            <tr class="empty-row">
                <td colspan="3">
                    No cases registered yet.
                </td>
            </tr>
        `;

        return;

    }


    /* -------------------------------------
       CASE ROWS
    ------------------------------------- */

    table.innerHTML =
        dashboardData.cases
            .slice(0, 5)
            .map(caseItem => {

                return `
                    <tr>

                        <td>

                            <a
                                href="case.html"
                                class="dashboard-case-link"
                            >
                                ${escapeHTML(
                                    caseItem.caseNumber
                                )}
                            </a>

                        </td>


                        <td>
                            ${escapeHTML(
                                caseItem.evidenceCount
                            )}
                        </td>


                        <td>

                            <span class="status-badge">
                                ${escapeHTML(
                                    caseItem.status
                                )}
                            </span>

                        </td>

                    </tr>
                `;

            })
            .join("");

}


/* =========================================
   ACTIVITY → PAGE LINK
========================================= */

function getActivityLink(title) {

    const text =
        title.toLowerCase();


    /* -------------------------------------
       EVIDENCE
    ------------------------------------- */

    if (
        text.includes("evidence")
    ) {

        return "evidence.html";

    }


    /* -------------------------------------
       CUSTODY
    ------------------------------------- */

    if (
        text.includes("custody") ||
        text.includes("transfer")
    ) {

        return "custody.html";

    }


    /* -------------------------------------
       FINGERPRINT / SECURITY
    ------------------------------------- */

    if (
        text.includes("fingerprint") ||
        text.includes("unauthorized")
    ) {

        return "audit.html";

    }


    /* -------------------------------------
       PERSONNEL
    ------------------------------------- */

    if (
        text.includes("personnel")
    ) {

        return "personnel.html";

    }


    /* -------------------------------------
       DEVICES / RFID
    ------------------------------------- */

    if (
        text.includes("rfid") ||
        text.includes("device")
    ) {

        return "devices.html";

    }


    /* -------------------------------------
       REPORTS
    ------------------------------------- */

    if (
        text.includes("report")
    ) {

        return "reports.html";

    }


    /* -------------------------------------
       DEFAULT
    ------------------------------------- */

    return "audit.html";

}


/* =========================================
   RENDER RECENT ACTIVITY
========================================= */

function renderActivity() {

    const activityList =
        document.getElementById("activityList");


    if (!activityList) {
        return;
    }


    /* -------------------------------------
       EMPTY STATE
    ------------------------------------- */

    if (dashboardData.activity.length === 0) {

        activityList.innerHTML = `
            <div class="empty-activity">
                No system activity yet.
            </div>
        `;

        return;

    }


    /* -------------------------------------
       ACTIVITY ITEMS
    ------------------------------------- */

    activityList.innerHTML =
        dashboardData.activity
            .slice(0, 6)
            .map(activity => {

                const link =
                    getActivityLink(
                        activity.title
                    );


                return `

                    <a
                        href="${link}"
                        class="activity-item"
                    >

                        <strong>
                            ${escapeHTML(
                                activity.title
                            )}
                        </strong>

                        <span>
                            ${escapeHTML(
                                activity.time
                            )}
                        </span>

                    </a>

                `;

            })
            .join("");

}


/* =========================================
   BASIC HTML ESCAPING
========================================= */

function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}


/* =========================================
   INITIALIZE DASHBOARD
========================================= */

function initializeDashboard() {

    updateDashboardStatistics();

    renderRecentCases();

    renderActivity();

}


/* =========================================
   START
========================================= */

document.addEventListener(
    "DOMContentLoaded",
    initializeDashboard
);