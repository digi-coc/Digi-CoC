// =========================================================
// DIGI-CoC AUDIT LOGS
// Audit records are loaded from the backend after integration.
// =========================================================


// ---------------------------------------------------------
// DUMMY AUDIT EVENTS
// ---------------------------------------------------------

const auditEvents = []


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