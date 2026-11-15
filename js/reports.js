/* =========================================================
   DIGI-CoC
   REPORTS
   ========================================================= */


/* ---------------------------------------------------------
   REPORT DATA
   Populated after backend integration.
   --------------------------------------------------------- */

let reports = []


/* ---------------------------------------------------------
   ELEMENTS
   --------------------------------------------------------- */

const reportForm =
    document.getElementById("reportForm");

const reportsTableBody =
    document.getElementById("reportsTableBody");

const reportModal =
    document.getElementById("reportModal");

const reportPreview =
    document.getElementById("reportPreview");

const previewReportBtn =
    document.getElementById("previewReportBtn");

const closeReportModal =
    document.getElementById("closeReportModal");

const closePreviewBtn =
    document.getElementById("closePreviewBtn");

const printReportBtn =
    document.getElementById("printReportBtn");


/* ---------------------------------------------------------
   RENDER RECENT REPORTS
   --------------------------------------------------------- */

function renderReports() {

    reportsTableBody.innerHTML = "";

    if (reports.length === 0) {
        reportsTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    No reports available yet.
                </td>
            </tr>
        `;
        return;
    }

    reports.forEach(report => {

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>
                <strong>
                    ${escapeHTML(report.reportId)}
                </strong>
            </td>

            <td>
                ${escapeHTML(report.caseId)}
            </td>

            <td>
                ${escapeHTML(report.type)}
            </td>

            <td>
                ${escapeHTML(report.generated)}
            </td>

            <td>
                ${escapeHTML(report.generatedBy)}
            </td>

            <td>

                <button
                    class="table-action"
                    onclick="viewReport('${report.reportId}')"
                >
                    View
                </button>

            </td>

        `;


        reportsTableBody.appendChild(row);

    });

}


/* ---------------------------------------------------------
   GENERATE REPORT PREVIEW
   --------------------------------------------------------- */

function generatePreview() {

    const caseId =
        document
            .getElementById("reportCase")
            .value;


    const reportType =
        document
            .getElementById("reportType")
            .value;


    if (!caseId) {

        alert("Please select a case first.");

        return false;

    }


    const includeEvidence =
        document
            .getElementById("includeEvidence")
            .checked;


    const includeCustody =
        document
            .getElementById("includeCustody")
            .checked;


    const includeVerification =
        document
            .getElementById("includeVerification")
            .checked;


    const includeAudit =
        document
            .getElementById("includeAudit")
            .checked;


    const now =
        new Date();


    const generatedDate =
        now.toLocaleDateString(
            "en-GB",
            {
                day: "2-digit",
                month: "short",
                year: "numeric"
            }
        );


    let html = `

        <div class="report-document">

            <div class="report-title">

                <h2>
                    Digi-CoC
                </h2>

                <p>
                    Digital Forensic Chain of Custody Report
                </p>

            </div>


            <div class="report-section">

                <h3>
                    Report Information
                </h3>


                <div class="report-info-grid">

                    <div class="report-info-item">

                        <span>
                            Case ID
                        </span>

                        <strong>
                            ${escapeHTML(caseId)}
                        </strong>

                    </div>


                    <div class="report-info-item">

                        <span>
                            Report Type
                        </span>

                        <strong>
                            ${escapeHTML(
                                document
                                    .getElementById("reportType")
                                    .selectedOptions[0]
                                    .text
                            )}
                        </strong>

                    </div>


                    <div class="report-info-item">

                        <span>
                            Generated
                        </span>

                        <strong>
                            ${generatedDate}
                        </strong>

                    </div>


                    <div class="report-info-item">

                        <span>
                            System
                        </span>

                        <strong>
                            Digi-CoC
                        </strong>

                    </div>

                </div>

            </div>

    `;


    if (includeEvidence) {
        html += `
            <div class="report-section">
                <h3>Evidence Information</h3>
                <p>Evidence details will be populated from the connected backend.</p>
            </div>
        `;
    }

    if (includeCustody) {
        html += `
            <div class="report-section">
                <h3>Chain of Custody</h3>
                <p>Custody events will be populated from the connected backend.</p>
            </div>
        `;
    }

    if (includeVerification) {
        html += `
            <div class="report-section">
                <h3>Biometric Verification</h3>
                <p>Verification records will be populated from the connected backend.</p>
            </div>
        `;
    }


    if (includeAudit) {

        html += `

            <div class="report-section">

                <h3>
                    Audit Information
                </h3>

                <p>
                    All recorded events are intended to be
                    maintained as an auditable history of the
                    evidence custody process.
                </p>

            </div>

        `;

    }


    html += `

            <div class="report-footer">

                Digi-CoC Digital Chain of Custody System

                <br>

                Generated electronically from recorded
                system information.

            </div>

        </div>

    `;


    reportPreview.innerHTML =
        html;


    reportModal.classList.add("show");


    return true;

}


/* ---------------------------------------------------------
   PREVIEW
   --------------------------------------------------------- */

previewReportBtn.addEventListener(
    "click",
    generatePreview
);


/* ---------------------------------------------------------
   GENERATE
   --------------------------------------------------------- */

reportForm.addEventListener(
    "submit",
    event => {

        event.preventDefault();


        if (!generatePreview()) {

            return;

        }


        const now =
            new Date();


        const nextNumber =
            reports.length + 1;


        reports.unshift({

            reportId:
                `REP-${now.getFullYear()}-${String(nextNumber).padStart(3, "0")}`,

            caseId:
                document
                    .getElementById("reportCase")
                    .value,

            type:
                document
                    .getElementById("reportType")
                    .selectedOptions[0]
                    .text,

            generated:
                now.toLocaleDateString(
                    "en-GB",
                    {
                        day: "2-digit",
                        month: "short",
                        year: "numeric"
                    }
                ),

            generatedBy:
                "Current User"

        });


        renderReports();

    }
);


/* ---------------------------------------------------------
   CLOSE MODAL
   --------------------------------------------------------- */

function closeModal() {

    reportModal.classList.remove("show");

}


closeReportModal.addEventListener(
    "click",
    closeModal
);


closePreviewBtn.addEventListener(
    "click",
    closeModal
);


reportModal.addEventListener(
    "click",
    event => {

        if (event.target === reportModal) {

            closeModal();

        }

    }
);


/* ---------------------------------------------------------
   PRINT
   --------------------------------------------------------- */

printReportBtn.addEventListener(
    "click",
    () => {

        window.print();

    }
);


/* ---------------------------------------------------------
   VIEW EXISTING REPORT
   --------------------------------------------------------- */

function viewReport(reportId) {

    const report =
        reports.find(
            item =>
                item.reportId === reportId
        );


    if (!report) {

        return;

    }


    document.getElementById("reportCase").value =
        report.caseId;


    document.getElementById("reportType").value =
        report.type === "Evidence Summary"
            ? "evidence"
            : "full";


    generatePreview();

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

renderReports();