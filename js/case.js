// =====================================================
// DIGI-CoC CASE MANAGEMENT
// =====================================================

const cases = [
    {
        id: "DC-2026-001",
        caseNumber: "FIR-123/2026",
        title: "Homicide Investigation",
        description: "Investigation involving suspected homicide.",
        investigationInfo: "Crime scene examination and evidence collection.",
        otherMetadata: "Initial investigation",
        status: "Active",
        createdAt: "2026-09-16 10:30"
    },
    {
        id: "DC-2026-002",
        caseNumber: "FIR-124/2026",
        title: "Theft Investigation",
        description: "Investigation involving reported theft.",
        investigationInfo: "Collection and examination of physical evidence.",
        otherMetadata: "Under investigation",
        status: "Active",
        createdAt: "2026-09-15 14:20"
    },
    {
        id: "DC-2026-003",
        caseNumber: "FIR-118/2026",
        title: "Fraud Investigation",
        description: "Investigation involving suspected fraud.",
        investigationInfo: "Document and digital evidence examination.",
        otherMetadata: "Investigation completed",
        status: "Closed",
        createdAt: "2026-09-10 09:15"
    }
];


// =====================================================
// INITIALIZATION
// =====================================================

document.addEventListener("DOMContentLoaded", () => {

    renderCases();

    setupCaseModal();

    setupSearch();

});


// =====================================================
// RENDER CASES
// =====================================================

function renderCases(filteredCases = cases) {

    const tbody = document.querySelector("#casesTableBody");

    if (!tbody) {
        return;
    }

    if (filteredCases.length === 0) {

        tbody.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="empty-state">
                        <h3>No cases found</h3>
                        <p>No cases match your search.</p>
                    </div>
                </td>
            </tr>
        `;

        return;
    }

    tbody.innerHTML = filteredCases.map(caseItem => {

        const statusClass =
            caseItem.status.toLowerCase() === "active"
                ? "status-success"
                : "status-neutral";

        return `
            <tr>

                <td>
                    <a
                        href="case.html?id=${encodeURIComponent(caseItem.id)}"
                        class="table-link"
                    >
                        ${escapeHTML(caseItem.id)}
                    </a>
                </td>

                <td>
                    ${escapeHTML(caseItem.caseNumber)}
                </td>

                <td>
                    ${escapeHTML(caseItem.title)}
                </td>

                <td>
                    ${escapeHTML(caseItem.createdAt)}
                </td>

                <td>
                    <span class="status-badge ${statusClass}">
                        ${escapeHTML(caseItem.status)}
                    </span>
                </td>

                <td>
                    <a
                        href="case.html?id=${encodeURIComponent(caseItem.id)}"
                        class="table-action"
                    >
                        View
                    </a>
                </td>

            </tr>
        `;

    }).join("");

}


// =====================================================
// CASE MODAL
// =====================================================

function setupCaseModal() {

    const modal = document.getElementById("caseModal");

    const openButton = document.getElementById("openCaseModal");

    const closeButton = document.getElementById("closeCaseModal");

    const cancelButton = document.getElementById("cancelCase");

    const form = document.getElementById("caseForm");


    if (!modal || !openButton || !form) {
        return;
    }


    // Open modal

    openButton.addEventListener("click", () => {

        modal.classList.add("active");

    });


    // Close modal

    if (closeButton) {

        closeButton.addEventListener("click", () => {

            modal.classList.remove("active");

        });

    }


    // Cancel

    if (cancelButton) {

        cancelButton.addEventListener("click", () => {

            modal.classList.remove("active");

        });

    }


    // Submit

    form.addEventListener("submit", event => {

        event.preventDefault();

        createCase();

    });

}


// =====================================================
// CREATE CASE
// =====================================================

function createCase() {

    const caseNumber =
        document.getElementById("caseNumber")?.value.trim();

    const caseTitle =
        document.getElementById("caseTitle")?.value.trim();

    const description =
        document.getElementById("caseDescription")?.value.trim();

    const investigationInfo =
        document.getElementById("investigationInfo")?.value.trim();

    const otherMetadata =
        document.getElementById("otherMetadata")?.value.trim();

    const caseStatus =
        document.getElementById("caseStatus")?.value;


    if (!caseNumber || !caseTitle) {

        alert("Case Number / ID and Case Name / Title are required.");

        return;
    }


    // Generate system Case ID

    const newID = generateCaseID();


    const newCase = {

        id: newID,

        caseNumber: caseNumber,

        title: caseTitle,

        description: description || "",

        investigationInfo: investigationInfo || "",

        otherMetadata: otherMetadata || "",

        status: caseStatus || "Active",

        createdAt: getCurrentDateTime()

    };


    // Add to temporary frontend dataset

    cases.unshift(newCase);


    // Close modal

    const modal = document.getElementById("caseModal");

    if (modal) {

        modal.classList.remove("active");

    }


    // Reset form

    const form = document.getElementById("caseForm");

    if (form) {

        form.reset();

    }


    // Show created state

    showCaseCreated(newCase);


    // Refresh table

    renderCases();

}


// =====================================================
// CASE CREATED
// =====================================================

function showCaseCreated(caseItem) {

    const message = `

Case created successfully.

System Case ID:
${caseItem.id}

Case Number:
${caseItem.caseNumber}

You can now proceed to Evidence Registration.

`;


    const proceed = confirm(message + "\nProceed to Evidence Registration?");


    if (proceed) {

        window.location.href =
            `evidence.html?case_id=${encodeURIComponent(caseItem.id)}`;

    }

}


// =====================================================
// GENERATE CASE ID
// =====================================================

function generateCaseID() {

    const year = new Date().getFullYear();

    let highestNumber = 0;


    cases.forEach(caseItem => {

        const match =
            caseItem.id.match(/DC-\d{4}-(\d+)/);

        if (match) {

            const number =
                parseInt(match[1], 10);

            if (number > highestNumber) {

                highestNumber = number;

            }

        }

    });


    const nextNumber =
        String(highestNumber + 1).padStart(3, "0");


    return `DC-${year}-${nextNumber}`;

}


// =====================================================
// SEARCH
// =====================================================

function setupSearch() {

    const searchInput =
        document.getElementById("caseSearch");


    if (!searchInput) {
        return;
    }


    searchInput.addEventListener("input", () => {

        const query =
            searchInput.value.trim().toLowerCase();


        if (!query) {

            renderCases();

            return;

        }


        const filtered =
            cases.filter(caseItem => {

                return (

                    caseItem.id.toLowerCase().includes(query) ||

                    caseItem.caseNumber.toLowerCase().includes(query) ||

                    caseItem.title.toLowerCase().includes(query) ||

                    caseItem.status.toLowerCase().includes(query)

                );

            });


        renderCases(filtered);

    });

}


// =====================================================
// CURRENT DATE / TIME
// =====================================================

function getCurrentDateTime() {

    const now = new Date();

    const year =
        now.getFullYear();

    const month =
        String(now.getMonth() + 1).padStart(2, "0");

    const day =
        String(now.getDate()).padStart(2, "0");

    const hours =
        String(now.getHours()).padStart(2, "0");

    const minutes =
        String(now.getMinutes()).padStart(2, "0");


    return `${year}-${month}-${day} ${hours}:${minutes}`;

}


// =====================================================
// HTML ESCAPE
// =====================================================

function escapeHTML(value) {

    return String(value)

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");

}