/* =========================================================
   DIGI-CoC
   CHAIN OF CUSTODY
   ========================================================= */


/* ---------------------------------------------------------
   TEMPORARY FRONTEND DATA
   --------------------------------------------------------- */

let custodyRecords = [

    {
        evidenceId: "EV-2026-001",
        caseId: "DC-2026-001",
        currentHolder: "P-001",
        location: "Forensic Laboratory",
        lastVerified: "26 Aug 2026, 10:42",
        status: "Verified"
    },

    {
        evidenceId: "EV-2026-002",
        caseId: "DC-2026-001",
        currentHolder: "P-002",
        location: "Evidence Storage",
        lastVerified: "26 Aug 2026, 09:18",
        status: "Verified"
    },

    {
        evidenceId: "EV-2026-003",
        caseId: "DC-2026-002",
        currentHolder: "P-003",
        location: "Forensic Laboratory",
        lastVerified: "26 Aug 2026, 08:51",
        status: "Flagged"
    }

];


let custodyEvents = [

    {
        time: "26 Aug 2026, 10:42",
        evidenceId: "EV-2026-001",
        action: "Evidence received",
        personnel: "P-001",
        location: "Forensic Laboratory"
    },

    {
        time: "26 Aug 2026, 09:18",
        evidenceId: "EV-2026-002",
        action: "Evidence transferred",
        personnel: "P-002",
        location: "Evidence Storage"
    },

    {
        time: "26 Aug 2026, 08:51",
        evidenceId: "EV-2026-003",
        action: "Verification alert",
        personnel: "P-003",
        location: "Forensic Laboratory"
    }

];


/* ---------------------------------------------------------
   ELEMENTS
   --------------------------------------------------------- */

const tableBody =
    document.getElementById("custodyTableBody");

const eventsContainer =
    document.getElementById("custodyEvents");

const activeCustody =
    document.getElementById("activeCustody");

const transfersToday =
    document.getElementById("transfersToday");

const verificationStatus =
    document.getElementById("verificationStatus");

const searchInput =
    document.getElementById("custodySearch");

const modal =
    document.getElementById("transferModal");

const newTransferBtn =
    document.getElementById("newTransferBtn");

const closeTransferModal =
    document.getElementById("closeTransferModal");

const cancelTransferBtn =
    document.getElementById("cancelTransferBtn");

const transferForm =
    document.getElementById("transferForm");

const biometricStatus =
    document.getElementById("biometricStatus");
// ---------------------------------------------------------
// EVIDENCE PASSED FROM SCAN PAGE
// ---------------------------------------------------------

const urlParams = new URLSearchParams(window.location.search);

const scannedEvidenceId =
    urlParams.get("evidence_id");

const scannedTagId =
    urlParams.get("tag_id");

/* ---------------------------------------------------------
   RENDER CURRENT CUSTODY
   --------------------------------------------------------- */

function renderCustody(list = custodyRecords) {

    tableBody.innerHTML = "";


    if (list.length === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    No custody records found.
                </td>
            </tr>
        `;

        return;
    }


    list.forEach(record => {

        const row =
            document.createElement("tr");


        const statusClass =
            record.status.toLowerCase();


        row.innerHTML = `

            <td>
                <strong>
                    ${escapeHTML(record.evidenceId)}
                </strong>
            </td>


            <td>
                ${escapeHTML(record.caseId)}
            </td>


            <td>
                ${escapeHTML(record.currentHolder)}
            </td>


            <td>
                ${escapeHTML(record.location)}
            </td>


            <td>
                ${escapeHTML(record.lastVerified)}
            </td>


            <td>

                <span class="status-badge ${statusClass}">
                    ${escapeHTML(record.status)}
                </span>

            </td>


            <td>

                <button
                    class="table-action"
                    onclick="viewCustody('${record.evidenceId}')"
                >
                    View
                </button>

            </td>

        `;


        tableBody.appendChild(row);

    });

}


/* ---------------------------------------------------------
   RENDER EVENTS
   --------------------------------------------------------- */

function renderEvents() {

    eventsContainer.innerHTML = "";


    if (custodyEvents.length === 0) {

        eventsContainer.innerHTML = `
            <div class="empty-state">
                No custody events recorded.
            </div>
        `;

        return;
    }


    custodyEvents.forEach(event => {

        const element =
            document.createElement("div");


        element.className =
            "custody-event";


        element.innerHTML = `

            <div class="event-time">
                ${escapeHTML(event.time)}
            </div>


            <div class="event-main">

                <strong>
                    ${escapeHTML(event.action)}
                </strong>

                <span>
                    ${escapeHTML(event.evidenceId)}
                    ·
                    ${escapeHTML(event.location)}
                </span>

            </div>


            <div class="event-person">
                Personnel:
                <strong>
                    ${escapeHTML(event.personnel)}
                </strong>
            </div>

        `;


        eventsContainer.appendChild(element);

    });

}


/* ---------------------------------------------------------
   UPDATE STATS
   --------------------------------------------------------- */

function updateStats() {

    activeCustody.textContent =
        custodyRecords.length;


    transfersToday.textContent =
        custodyEvents.length;


    verificationStatus.textContent =
        "READY";

}


/* ---------------------------------------------------------
   SEARCH
   --------------------------------------------------------- */

searchInput.addEventListener(
    "input",
    () => {

        const query =
            searchInput.value
                .trim()
                .toLowerCase();


        if (!query) {

            renderCustody(custodyRecords);

            return;

        }


        const filtered =
            custodyRecords.filter(record =>

                record.evidenceId
                    .toLowerCase()
                    .includes(query)

                ||

                record.caseId
                    .toLowerCase()
                    .includes(query)

                ||

                record.currentHolder
                    .toLowerCase()
                    .includes(query)

                ||

                record.location
                    .toLowerCase()
                    .includes(query)

            );


        renderCustody(filtered);

    }
);


/* ---------------------------------------------------------
   MODAL
   --------------------------------------------------------- */

function openTransferModal() {

    modal.classList.add("show");

    biometricStatus.textContent =
        "Awaiting fingerprint verification";

    biometricStatus.style.color =
        "";

    // If this transfer came from the Scan Evidence Tag page,
    // automatically use the scanned evidence.
    if (scannedEvidenceId) {

        const evidenceInput =
            document.getElementById("transferEvidence");

        if (evidenceInput) {
            evidenceInput.value = scannedEvidenceId;
        }

    }

}


function closeModal() {

    modal.classList.remove("show");

    transferForm.reset();

}


newTransferBtn.addEventListener(
    "click",
    openTransferModal
);


closeTransferModal.addEventListener(
    "click",
    closeModal
);


cancelTransferBtn.addEventListener(
    "click",
    closeModal
);


modal.addEventListener(
    "click",
    event => {

        if (event.target === modal) {

            closeModal();

        }

    }
);


/* ---------------------------------------------------------
   TRANSFER FORM
   --------------------------------------------------------- */

transferForm.addEventListener(
    "submit",
    event => {

        event.preventDefault();


        const evidenceId =
            document
                .getElementById("transferEvidence")
                .value
                .trim();


        const personnelId =
            document
                .getElementById("transferPersonnel")
                .value
                .trim();


        const location =
            document
                .getElementById("transferLocation")
                .value
                .trim();


        const purpose =
            document
                .getElementById("transferPurpose")
                .value;


        if (
            !evidenceId ||
            !personnelId ||
            !location
        ) {

            return;

        }


        /*
         * TEMPORARY FRONTEND BEHAVIOUR
         *
         * Later this section will NOT simply accept
         * the form submission.
         *
         * The backend/hardware integration will:
         *
         * 1. Request fingerprint verification.
         * 2. ESP32 communicates with R307S.
         * 3. Fingerprint ID is returned.
         * 4. Backend checks authorized personnel.
         * 5. Verification is recorded.
         * 6. Custody event is created.
         *
         * For now we simulate successful verification.
         */


        biometricStatus.textContent =
            "Fingerprint verified — transfer recorded";


        biometricStatus.style.color =
            "var(--success)";


        const now =
            new Date();


        const formattedTime =
            now.toLocaleDateString(
                "en-GB",
                {
                    day: "2-digit",
                    month: "short",
                    year: "numeric"
                }
            )
            +
            ", "
            +
            now.toLocaleTimeString(
                "en-GB",
                {
                    hour: "2-digit",
                    minute: "2-digit"
                }
            );


        const existingRecord =
            custodyRecords.find(
                record =>
                    record.evidenceId === evidenceId
            );


        if (existingRecord) {

            existingRecord.currentHolder =
                personnelId;

            existingRecord.location =
                location;

            existingRecord.lastVerified =
                formattedTime;

            existingRecord.status =
                "Verified";

        } else {

            custodyRecords.unshift({

                evidenceId,

                caseId:
                    "Unknown",

                currentHolder:
                    personnelId,

                location,

                lastVerified:
                    formattedTime,

                status:
                    "Verified"

            });

        }


        custodyEvents.unshift({

            time:
                formattedTime,

            evidenceId,

            action:
                "Evidence transferred",

            personnel:
                personnelId,

            location,

            purpose

        });


        renderCustody();

        renderEvents();

        updateStats();


        setTimeout(
            closeModal,
            700
        );

    }
);


/* ---------------------------------------------------------
   VIEW CUSTODY
   --------------------------------------------------------- */

function viewCustody(evidenceId) {

    const record =
        custodyRecords.find(
            item =>
                item.evidenceId === evidenceId
        );


    if (!record) {

        return;

    }


    alert(

        `Evidence: ${record.evidenceId}\n` +

        `Case: ${record.caseId}\n` +

        `Current Holder: ${record.currentHolder}\n` +

        `Location: ${record.location}\n` +

        `Last Verified: ${record.lastVerified}\n` +

        `Status: ${record.status}`

    );

}


/* ---------------------------------------------------------
   HTML ESCAPE
   --------------------------------------------------------- */

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}

if (scannedEvidenceId && modal) {

    const evidenceInput =
        document.getElementById("transferEvidence");

    if (evidenceInput) {
        evidenceInput.value = scannedEvidenceId;
    }

    openTransferModal();

}
/* ---------------------------------------------------------
   INITIALIZE
   --------------------------------------------------------- */

renderCustody();

renderEvents();

updateStats();