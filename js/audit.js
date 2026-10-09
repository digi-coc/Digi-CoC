// =========================================================
// DIGI-CoC AUDIT LOGS
// Temporary frontend data
// Backend integration will replace this later.
// =========================================================


// ---------------------------------------------------------
// DUMMY AUDIT EVENTS
// ---------------------------------------------------------

const auditEvents = [

    {
        id: "AUD-2026-0001",
        timestamp: "2026-09-16 09:14:22",
        type: "authentication",
        actor: "P-001",
        reference: "SYSTEM",
        action: "Personnel authenticated",
        severity: "normal",
        status: "success",
        details: "Authorized personnel authentication completed."
    },

    {
        id: "AUD-2026-0002",
        timestamp: "2026-09-16 09:21:08",
        type: "evidence",
        actor: "P-001",
        reference: "EV-2026-001",
        action: "Evidence registered",
        severity: "normal",
        status: "success",
        details: "New evidence item registered under case DC-2026-001."
    },

    {
        id: "AUD-2026-0003",
        timestamp: "2026-09-16 10:05:31",
        type: "custody",
        actor: "P-002",
        reference: "EV-2026-001",
        action: "Custody transfer recorded",
        severity: "normal",
        status: "success",
        details: "Evidence custody transferred after successful identity verification."
    },

    {
        id: "AUD-2026-0004",
        timestamp: "2026-09-16 10:18:44",
        type: "security",
        actor: "DEV-001",
        reference: "EV-2026-002",
        action: "Fingerprint verification",
        severity: "normal",
        status: "success",
        details: "Fingerprint matched an authorized evidence handler."
    },

    {
        id: "AUD-2026-0005",
        timestamp: "2026-09-16 10:42:13",
        type: "security",
        actor: "DEV-001",
        reference: "EV-2026-003",
        action: "Fingerprint verification failed",
        severity: "critical",
        status: "denied",
        details: "Fingerprint did not match an authorized evidence handler."
    },

    {
        id: "AUD-2026-0006",
        timestamp: "2026-09-16 10:42:14",
        type: "security",
        actor: "DEV-001",
        reference: "EV-2026-003",
        action: "Unauthorized attempt detected",
        severity: "critical",
        status: "flagged",
        details: "Unauthorized biometric attempt associated with evidence EV-2026-003."
    },

    {
        id: "AUD-2026-0007",
        timestamp: "2026-09-16 11:03:56",
        type: "personnel",
        actor: "P-ADMIN",
        reference: "P-004",
        action: "Personnel registered",
        severity: "normal",
        status: "success",
        details: "New authorized personnel record created."
    },

    {
        id: "AUD-2026-0008",
        timestamp: "2026-09-16 11:26:41",
        type: "device",
        actor: "DEV-002",
        reference: "DEVICE",
        action: "Device status changed",
        severity: "warning",
        status: "flagged",
        details: "RFID scanner reported offline."
    },

    {
        id: "AUD-2026-0009",
        timestamp: "2026-09-16 12:14:03",
        type: "report",
        actor: "P-001",
        reference: "DC-2026-001",
        action: "Chain of custody report generated",
        severity: "normal",
        status: "success",
        details: "Full chain of custody report generated for case DC-2026-001."
    },

    {
        id: "AUD-2026-0010",
        timestamp: "2026-09-16 12:47:19",
        type: "system",
        actor: "SYSTEM",
        reference: "SYSTEM",
        action: "System synchronization",
        severity: "normal",
        status: "success",
        details: "System records synchronized with central database."
    }

];


// ---------------------------------------------------------
// ELEMENTS
// ---------------------------------------------------------

const auditTableBody =
    document.getElementById("auditTableBody");

const auditEmptyState =
    document.getElementById("auditEmptyState");

const auditSearch =
    document.getElementById("auditSearch");

const eventTypeFilter =
    document.getElementById("eventTypeFilter");

const severityFilter =
    document.getElementById("severityFilter");


// ---------------------------------------------------------
// STATISTICS
// ---------------------------------------------------------

function updateAuditStats(events) {

    const totalEvents =
        document.getElementById("totalEvents");

    const todayEvents =
        document.getElementById("todayEvents");

    const securityEvents =
        document.getElementById("securityEvents");

    const unauthorizedEvents =
        document.getElementById("unauthorizedEvents");


    totalEvents.textContent =
        events.length;


    const today =
        "2026-09-16";

    const todayCount =
        events.filter(event =>
            event.timestamp.startsWith(today)
        ).length;

    todayEvents.textContent =
        todayCount;


    const securityCount =
        events.filter(event =>
            event.type === "security" ||
            event.type === "authentication"
        ).length;

    securityEvents.textContent =
        securityCount;


    const unauthorizedCount =
        events.filter(event =>
            event.status === "denied" ||
            event.status === "flagged"
        ).length;

    unauthorizedEvents.textContent =
        unauthorizedCount;

}


// ---------------------------------------------------------
// ESCAPE HTML
// ---------------------------------------------------------

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


// ---------------------------------------------------------
// RENDER AUDIT TABLE
// ---------------------------------------------------------

function renderAuditLogs(events) {

    auditTableBody.innerHTML = "";


    if (events.length === 0) {

        auditEmptyState.style.display =
            "block";

        return;

    }


    auditEmptyState.style.display =
        "none";


    events.forEach(event => {

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>
                ${escapeHTML(event.timestamp)}
            </td>

            <td>
                <span class="audit-event-id">
                    ${escapeHTML(event.id)}
                </span>
            </td>

            <td>
                ${escapeHTML(formatEventType(event.type))}
            </td>

            <td>
                ${escapeHTML(event.actor)}
            </td>

            <td>
                <span class="audit-reference">
                    ${escapeHTML(event.reference)}
                </span>
            </td>

            <td>
                <span class="audit-action">
                    ${escapeHTML(event.action)}
                </span>
            </td>

            <td>
                <span class="audit-severity ${escapeHTML(event.severity)}">
                    ${escapeHTML(event.severity)}
                </span>
            </td>

            <td>
                <span class="audit-status ${escapeHTML(event.status)}">
                    ${escapeHTML(formatStatus(event.status))}
                </span>
            </td>

            <td>

                <button
                    class="audit-details-btn"
                    onclick="viewAuditDetails('${escapeHTML(event.id)}')"
                >
                    View
                </button>

            </td>

        `;


        auditTableBody.appendChild(row);

    });

}


// ---------------------------------------------------------
// FORMAT EVENT TYPE
// ---------------------------------------------------------

function formatEventType(type) {

    const labels = {

        authentication: "Authentication",

        personnel: "Personnel",

        evidence: "Evidence",

        custody: "Custody",

        security: "Security",

        device: "Device",

        report: "Report",

        system: "System"

    };

    return labels[type] || type;

}


// ---------------------------------------------------------
// FORMAT STATUS
// ---------------------------------------------------------

function formatStatus(status) {

    const labels = {

        success: "Successful",

        denied: "Denied",

        flagged: "Flagged"

    };

    return labels[status] || status;

}


// ---------------------------------------------------------
// FILTER EVENTS
// ---------------------------------------------------------

function filterAuditEvents() {

    const searchTerm =
        auditSearch.value
            .trim()
            .toLowerCase();


    const selectedType =
        eventTypeFilter.value;


    const selectedSeverity =
        severityFilter.value;


    const filteredEvents =
        auditEvents.filter(event => {

            const searchableText = [

                event.id,

                event.timestamp,

                event.type,

                event.actor,

                event.reference,

                event.action,

                event.severity,

                event.status,

                event.details

            ]
            .join(" ")
            .toLowerCase();


            const matchesSearch =
                searchableText.includes(searchTerm);


            const matchesType =
                selectedType === "all" ||
                event.type === selectedType;


            const matchesSeverity =
                selectedSeverity === "all" ||
                event.severity === selectedSeverity;


            return (
                matchesSearch &&
                matchesType &&
                matchesSeverity
            );

        });


    renderAuditLogs(filteredEvents);

}


// ---------------------------------------------------------
// VIEW DETAILS
// ---------------------------------------------------------

function viewAuditDetails(eventID) {

    const event =
        auditEvents.find(item =>
            item.id === eventID
        );


    if (!event) {
        return;
    }


    alert(

        "AUDIT EVENT DETAILS\n\n" +

        "Event ID: " +
        event.id +

        "\nTimestamp: " +
        event.timestamp +

        "\nEvent Type: " +
        formatEventType(event.type) +

        "\nActor: " +
        event.actor +

        "\nReference: " +
        event.reference +

        "\nAction: " +
        event.action +

        "\nSeverity: " +
        event.severity +

        "\nStatus: " +
        formatStatus(event.status) +

        "\n\nDetails:\n" +
        event.details

    );

}


// ---------------------------------------------------------
// FILTER LISTENERS
// ---------------------------------------------------------

auditSearch.addEventListener(
    "input",
    filterAuditEvents
);

eventTypeFilter.addEventListener(
    "change",
    filterAuditEvents
);

severityFilter.addEventListener(
    "change",
    filterAuditEvents
);


// ---------------------------------------------------------
// INITIALIZE
// ---------------------------------------------------------

updateAuditStats(auditEvents);

renderAuditLogs(auditEvents);