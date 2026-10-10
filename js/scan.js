// ============================================
// Digi-CoC — Scan Evidence Tag
// ============================================

// Temporary frontend evidence registry.
// Later this will come from the backend database.
const evidenceRegistry = [
    {
        evidenceId: "EV-2026-001",
        caseId: "DC-2026-001",
        evidenceType: "Clothing",
        description: "Black jacket",
        collectionLocation: "Crime Scene A",
        collectionDate: "26 Aug 2026",
        collectedBy: "P-001",
        status: "In Custody",
        tagType: "RFID",
        tagId: "RFID-0001"
    },
    {
        evidenceId: "EV-2026-002",
        caseId: "DC-2026-001",
        evidenceType: "Document",
        description: "Handwritten document",
        collectionLocation: "Crime Scene A",
        collectionDate: "26 Aug 2026",
        collectedBy: "P-002",
        status: "In Custody",
        tagType: "RFID",
        tagId: "RFID-0002"
    },
    {
        evidenceId: "EV-2026-003",
        caseId: "DC-2026-002",
        evidenceType: "Mobile Device",
        description: "Mobile phone",
        collectionLocation: "Police Station",
        collectionDate: "25 Aug 2026",
        collectedBy: "P-001",
        status: "Flagged",
        tagType: "RFID",
        tagId: "RFID-0003"
    }
];


// ============================================
// DOM ELEMENTS
// ============================================

const scanForm = document.getElementById("scanForm");
const tagIdInput = document.getElementById("tagId");

const scanResult = document.getElementById("scanResult");
const resultIcon = document.getElementById("resultIcon");
const resultTitle = document.getElementById("resultTitle");
const resultMessage = document.getElementById("resultMessage");

const evidenceDetails = document.getElementById("evidenceDetails");

const evidenceIdValue = document.getElementById("evidenceIdValue");
const caseIdValue = document.getElementById("caseIdValue");
const evidenceTypeValue = document.getElementById("evidenceTypeValue");
const evidenceDescriptionValue = document.getElementById("evidenceDescriptionValue");
const collectionLocationValue = document.getElementById("collectionLocationValue");
const collectionDateValue = document.getElementById("collectionDateValue");
const collectedByValue = document.getElementById("collectedByValue");
const evidenceStatusValue = document.getElementById("evidenceStatusValue");
const tagTypeValue = document.getElementById("tagTypeValue");
const tagIdValue = document.getElementById("tagIdValue");

const continueBtn = document.getElementById("continueBtn");
const resetScanBtn = document.getElementById("resetScanBtn");


// ============================================
// HELPERS
// ============================================

function escapeHTML(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function findEvidenceByTag(tagId) {
    const normalizedTag = tagId.trim().toLowerCase();

    return evidenceRegistry.find(
        evidence =>
            evidence.tagId &&
            evidence.tagId.toLowerCase() === normalizedTag
    );
}


// ============================================
// SHOW SCAN RESULT
// ============================================

function showValidResult(evidence) {

    scanResult.className = "scan-result success";

    if (resultIcon) {
        resultIcon.textContent = "✓";
    }

    if (resultTitle) {
        resultTitle.textContent = "Evidence Tag Recognized";
    }

    if (resultMessage) {
        resultMessage.textContent =
            "The scanned tag is registered to the following evidence item.";
    }

    if (evidenceDetails) {
        evidenceDetails.style.display = "block";
    }

    if (evidenceIdValue) {
        evidenceIdValue.textContent = evidence.evidenceId;
    }

    if (caseIdValue) {
        caseIdValue.textContent = evidence.caseId;
    }

    if (evidenceTypeValue) {
        evidenceTypeValue.textContent = evidence.evidenceType;
    }

    if (evidenceDescriptionValue) {
        evidenceDescriptionValue.textContent = evidence.description;
    }

    if (collectionLocationValue) {
        collectionLocationValue.textContent = evidence.collectionLocation;
    }

    if (collectionDateValue) {
        collectionDateValue.textContent = evidence.collectionDate;
    }

    if (collectedByValue) {
        collectedByValue.textContent = evidence.collectedBy;
    }

    if (evidenceStatusValue) {
        evidenceStatusValue.textContent = evidence.status;
    }

    if (tagTypeValue) {
        tagTypeValue.textContent = evidence.tagType;
    }

    if (tagIdValue) {
        tagIdValue.textContent = evidence.tagId;
    }

    if (continueBtn) {
        continueBtn.style.display = "inline-flex";

        // Store the currently scanned evidence ID
        continueBtn.dataset.evidenceId = evidence.evidenceId;
        continueBtn.dataset.tagId = evidence.tagId;
    }
}


// ============================================
// UNKNOWN TAG RESULT
// ============================================

function showUnknownResult(tagId) {

    scanResult.className = "scan-result danger";

    if (resultIcon) {
        resultIcon.textContent = "!";
    }

    if (resultTitle) {
        resultTitle.textContent = "Unknown Evidence Tag";
    }

    if (resultMessage) {
        resultMessage.textContent =
            `Tag "${tagId}" is not registered in the Digi-CoC evidence registry. The scan should be treated as a security event.`;
    }

    if (evidenceDetails) {
        evidenceDetails.style.display = "none";
    }

    if (continueBtn) {
        continueBtn.style.display = "none";
        continueBtn.dataset.evidenceId = "";
        continueBtn.dataset.tagId = "";
    }

    // Prototype security alert
    console.warn("SECURITY EVENT: Unknown evidence tag scanned:", tagId);
}


// ============================================
// SCAN TAG
// ============================================

function scanEvidenceTag(tagId) {

    if (!tagId || !tagId.trim()) {

        scanResult.className = "scan-result warning";

        if (resultIcon) {
            resultIcon.textContent = "!";
        }

        if (resultTitle) {
            resultTitle.textContent = "Tag ID Required";
        }

        if (resultMessage) {
            resultMessage.textContent =
                "Enter or scan an Evidence Tag ID before continuing.";
        }

        if (evidenceDetails) {
            evidenceDetails.style.display = "none";
        }

        if (continueBtn) {
            continueBtn.style.display = "none";
        }

        return;
    }

    const evidence = findEvidenceByTag(tagId);

    if (evidence) {
        showValidResult(evidence);
    } else {
        showUnknownResult(tagId.trim());
    }
}


// ============================================
// FORM SUBMIT
// ============================================

if (scanForm) {

    scanForm.addEventListener("submit", function (event) {

        event.preventDefault();

        const tagId = tagIdInput
            ? tagIdInput.value.trim()
            : "";

        scanEvidenceTag(tagId);
    });
}


// ============================================
// CONTINUE TO PERSONNEL VERIFICATION
// ============================================

if (continueBtn) {

    continueBtn.addEventListener("click", function () {

        const evidenceId = this.dataset.evidenceId;
        const tagId = this.dataset.tagId;

        if (!evidenceId || !tagId) {
            return;
        }

        /*
         * The final workflow will be:
         *
         * Scan Evidence Tag
         *        ↓
         * Evidence identified
         *        ↓
         * Personnel identification
         *        ↓
         * Fingerprint verification
         *        ↓
         * Authorization
         *        ↓
         * Custody event
         */

        window.location.href =
            `custody.html?evidence_id=${encodeURIComponent(evidenceId)}&tag_id=${encodeURIComponent(tagId)}`;
    });
}


// ============================================
// RESET SCAN
// ============================================

if (resetScanBtn) {

    resetScanBtn.addEventListener("click", function () {

        if (tagIdInput) {
            tagIdInput.value = "";
            tagIdInput.focus();
        }

        if (scanResult) {
            scanResult.className = "scan-result";
        }

        if (resultIcon) {
            resultIcon.textContent = "";
        }

        if (resultTitle) {
            resultTitle.textContent = "Ready to Scan";
        }

        if (resultMessage) {
            resultMessage.textContent =
                "Enter an Evidence Tag ID to begin.";
        }

        if (evidenceDetails) {
            evidenceDetails.style.display = "none";
        }

        if (continueBtn) {
            continueBtn.style.display = "none";
            continueBtn.dataset.evidenceId = "";
            continueBtn.dataset.tagId = "";
        }
    });
}


// ============================================
// INITIAL STATE
// ============================================

document.addEventListener("DOMContentLoaded", function () {

    if (evidenceDetails) {
        evidenceDetails.style.display = "none";
    }

    if (continueBtn) {
        continueBtn.style.display = "none";
    }

    if (tagIdInput) {
        tagIdInput.focus();
    }

});