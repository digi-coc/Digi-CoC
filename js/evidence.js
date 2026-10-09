/* =========================================================
   DIGI-CoC
   EVIDENCE MANAGEMENT
   ========================================================= */


/* ---------------------------------------------------------
   TEMPORARY FRONTEND DATA
   --------------------------------------------------------- */

let evidence = [

    {
        evidenceId: "EV-2026-001",
        systemCaseId: "DC-2026-001",
        evidenceType: "Clothing",
        description: "Black jacket recovered from scene.",
        collectionLocation: "Crime Scene A",
        collectionDate: "26 Aug 2026",
        collectedBy: "P-001",

        tagType: "RFID",
        tagId: "RFID-0001",

        status: "In Custody"
    },


    {
        evidenceId: "EV-2026-002",
        systemCaseId: "DC-2026-001",
        evidenceType: "Document",
        description: "Handwritten document recovered from room.",
        collectionLocation: "Crime Scene A",
        collectionDate: "26 Aug 2026",
        collectedBy: "P-002",

        tagType: "RFID",
        tagId: "RFID-0002",

        status: "In Custody"
    },


    {
        evidenceId: "EV-2026-003",
        systemCaseId: "DC-2026-002",
        evidenceType: "Mobile Device",
        description: "Mobile phone recovered from suspect.",
        collectionLocation: "Police Station",
        collectionDate: "25 Aug 2026",
        collectedBy: "P-001",

        tagType: "RFID",
        tagId: "RFID-0003",

        status: "Flagged"
    }

];


/* ---------------------------------------------------------
   ELEMENTS
   --------------------------------------------------------- */

const tableBody =
    document.getElementById("evidenceTableBody");

const totalEvidence =
    document.getElementById("totalEvidence");

const inCustody =
    document.getElementById("inCustody");

const flaggedEvidence =
    document.getElementById("flaggedEvidence");

const searchInput =
    document.getElementById("evidenceSearch");

const modal =
    document.getElementById("evidenceModal");

const addEvidenceBtn =
    document.getElementById("addEvidenceBtn");

const closeEvidenceModal =
    document.getElementById("closeEvidenceModal");

const cancelEvidenceBtn =
    document.getElementById("cancelEvidenceBtn");

const evidenceForm =
    document.getElementById("evidenceForm");

const tagTypeInput =
    document.getElementById("tagType");

const tagIdInput =
    document.getElementById("tagId");

const tagStatus =
    document.getElementById("tagStatus");

const tagStatusValue =
    document.getElementById("tagStatusValue");


/* ---------------------------------------------------------
   TAG STATUS
   --------------------------------------------------------- */

function updateTagStatus() {

    const tagId =
        tagIdInput.value.trim();

    if (!tagId) {

        tagStatusValue.textContent =
            "Not assigned";

        tagStatus.classList.remove(
            "tag-assigned"
        );

        return;
    }


    const duplicate =
        evidence.some(
            item =>
                item.tagId &&
                item.tagId.toLowerCase() ===
                tagId.toLowerCase()
        );


    if (duplicate) {

        tagStatusValue.textContent =
            "Tag ID already assigned";

        tagStatus.classList.remove(
            "tag-assigned"
        );

        tagStatus.classList.add(
            "tag-error"
        );

        return;
    }


    tagStatusValue.textContent =
        `${tagTypeInput.value} tag ready`;

    tagStatus.classList.remove(
        "tag-error"
    );

    tagStatus.classList.add(
        "tag-assigned"
    );

}


/* ---------------------------------------------------------
   TAG INPUT EVENTS
   --------------------------------------------------------- */

tagIdInput.addEventListener(
    "input",
    updateTagStatus
);


tagTypeInput.addEventListener(
    "change",
    updateTagStatus
);


/* ---------------------------------------------------------
   RENDER EVIDENCE
   --------------------------------------------------------- */

function renderEvidence(list = evidence) {

    tableBody.innerHTML = "";


    if (list.length === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    No evidence found.
                </td>
            </tr>
        `;

        return;
    }


    list.forEach(item => {

        const row =
            document.createElement("tr");


        const statusClass =
            item.status
                .toLowerCase()
                .replaceAll(" ", "-");


        row.innerHTML = `

            <td>
                <strong>
                    ${escapeHTML(item.evidenceId)}
                </strong>
            </td>


            <td>
                ${escapeHTML(item.systemCaseId)}
            </td>


            <td>
                ${escapeHTML(item.evidenceType)}
            </td>


            <td>

                <div>
                    <strong>
                        ${escapeHTML(item.tagId || "Not assigned")}
                    </strong>

                    <small style="display:block;">
                        ${escapeHTML(item.tagType || "")}
                    </small>
                </div>

            </td>


            <td>
                ${escapeHTML(item.collectionDate)}
            </td>


            <td>
                ${escapeHTML(item.collectedBy)}
            </td>


            <td>

                <span class="status-badge ${statusClass}">
                    ${escapeHTML(item.status)}
                </span>

            </td>


            <td>

                <button
                    class="table-action"
                    onclick="viewEvidence('${escapeHTML(item.evidenceId)}')"
                >
                    View
                </button>

            </td>

        `;


        tableBody.appendChild(row);

    });

}


/* ---------------------------------------------------------
   STATISTICS
   --------------------------------------------------------- */

function updateStats() {

    totalEvidence.textContent =
        evidence.length;


    inCustody.textContent =
        evidence.filter(
            item =>
                item.status === "In Custody"
        ).length;


    flaggedEvidence.textContent =
        evidence.filter(
            item =>
                item.status === "Flagged"
        ).length;

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

            renderEvidence(evidence);

            return;
        }


        const filtered =
            evidence.filter(item =>

                item.evidenceId
                    .toLowerCase()
                    .includes(query)

                ||

                item.systemCaseId
                    .toLowerCase()
                    .includes(query)

                ||

                item.evidenceType
                    .toLowerCase()
                    .includes(query)

                ||

                item.tagId
                    ?.toLowerCase()
                    .includes(query)

                ||

                item.status
                    .toLowerCase()
                    .includes(query)

            );


        renderEvidence(filtered);

    }
);


/* ---------------------------------------------------------
   OPEN MODAL
   --------------------------------------------------------- */

function openEvidenceModal() {

    modal.classList.add("show");

}


/* ---------------------------------------------------------
   CLOSE MODAL
   --------------------------------------------------------- */

function closeModal() {

    modal.classList.remove("show");

    evidenceForm.reset();

    tagStatusValue.textContent =
        "Not assigned";

    tagStatus.classList.remove(
        "tag-assigned",
        "tag-error"
    );

}


/* ---------------------------------------------------------
   BUTTONS
   --------------------------------------------------------- */

addEvidenceBtn.addEventListener(
    "click",
    openEvidenceModal
);


closeEvidenceModal.addEventListener(
    "click",
    closeModal
);


cancelEvidenceBtn.addEventListener(
    "click",
    closeModal
);


/* ---------------------------------------------------------
   CLOSE OUTSIDE MODAL
   --------------------------------------------------------- */

modal.addEventListener(
    "click",
    event => {

        if (event.target === modal) {

            closeModal();

        }

    }
);


/* ---------------------------------------------------------
   REGISTER EVIDENCE
   --------------------------------------------------------- */

evidenceForm.addEventListener(
    "submit",
    event => {

        event.preventDefault();


        const systemCaseId =
            document
                .getElementById("evidenceCase")
                .value
                .trim();


        const evidenceType =
            document
                .getElementById("evidenceType")
                .value
                .trim();


        const description =
            document
                .getElementById("evidenceDescription")
                .value
                .trim();


        const collectionLocation =
            document
                .getElementById("collectionLocation")
                .value
                .trim();


        const collectionDate =
            document
                .getElementById("collectionDate")
                .value;


        const collectedBy =
            document
                .getElementById("collectedBy")
                .value
                .trim();


        const tagType =
            tagTypeInput.value;


        const tagId =
            tagIdInput.value.trim();


        /* -------------------------------------------------
           BASIC VALIDATION
           ------------------------------------------------- */

        if (
            !systemCaseId ||
            !evidenceType ||
            !description ||
            !collectionLocation ||
            !collectionDate ||
            !collectedBy ||
            !tagType ||
            !tagId
        ) {

            alert(
                "Please complete all evidence and tag information."
            );

            return;

        }


        /* -------------------------------------------------
           DUPLICATE TAG CHECK
           ------------------------------------------------- */

        const duplicateTag =
            evidence.some(
                item =>
                    item.tagId &&
                    item.tagId.toLowerCase() ===
                    tagId.toLowerCase()
            );


        if (duplicateTag) {

            alert(
                "This Evidence Tag ID is already assigned to another evidence item."
            );

            return;

        }


        /* -------------------------------------------------
           GENERATE EVIDENCE ID
           ------------------------------------------------- */

        const nextNumber =
            evidence.length + 1;


        const newEvidenceId =
            `EV-${new Date().getFullYear()}-${String(nextNumber).padStart(3, "0")}`;


        /* -------------------------------------------------
           FORMAT DATE
           ------------------------------------------------- */

        const formattedDate =
            new Date(
                collectionDate + "T00:00:00"
            ).toLocaleDateString(
                "en-GB",
                {
                    day: "2-digit",
                    month: "short",
                    year: "numeric"
                }
            );


        /* -------------------------------------------------
           CREATE EVIDENCE RECORD
           ------------------------------------------------- */

        const newEvidence = {

            evidenceId:
                newEvidenceId,

            systemCaseId,

            evidenceType,

            description,

            collectionLocation,

            collectionDate:
                formattedDate,

            collectedBy,

            tagType,

            tagId,

            status:
                "In Custody"

        };


        /* -------------------------------------------------
           STORE FRONTEND RECORD
           ------------------------------------------------- */

        evidence.unshift(
            newEvidence
        );


        /* -------------------------------------------------
           UPDATE UI
           ------------------------------------------------- */

        renderEvidence();

        updateStats();

        closeModal();


        /* -------------------------------------------------
           CONFIRMATION
           ------------------------------------------------- */

        alert(
            `Evidence ${newEvidenceId} registered successfully.\n\n` +
            `Tag: ${tagType}\n` +
            `Tag ID: ${tagId}\n\n` +
            `Evidence is now marked as In Custody.`
        );

    }
);


/* ---------------------------------------------------------
   VIEW EVIDENCE
   --------------------------------------------------------- */

function viewEvidence(evidenceId) {

    const selectedEvidence =
        evidence.find(
            item =>
                item.evidenceId === evidenceId
        );


    if (!selectedEvidence) {

        return;

    }


    alert(

        `Evidence: ${selectedEvidence.evidenceId}\n` +

        `Case: ${selectedEvidence.systemCaseId}\n` +

        `Type: ${selectedEvidence.evidenceType}\n` +

        `Description: ${selectedEvidence.description}\n` +

        `Collection Location: ${selectedEvidence.collectionLocation}\n` +

        `Collected By: ${selectedEvidence.collectedBy}\n` +

        `Tag Type: ${selectedEvidence.tagType}\n` +

        `Tag ID: ${selectedEvidence.tagId}\n` +

        `Status: ${selectedEvidence.status}`

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


/* ---------------------------------------------------------
   INITIALIZE
   --------------------------------------------------------- */

renderEvidence();

updateStats();