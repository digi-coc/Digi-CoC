/* =========================================
   DIGI-CoC
   FRONTEND DASHBOARD
========================================= */


const dashboardData = {
    cases: [],
    evidence: [],
    personnel: [],
    custodyEvents: [],
    activity: []
};;


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