/* =========================================
   DIGI-CoC
   PERSONNEL FRONTEND
========================================= */


const personnelData = {

    systemAccess: [],

    evidenceHandlers: []

};


/* =========================================
   UPDATE COUNTS
========================================= */

function updatePersonnelCounts() {

    const systemCount =
        document.getElementById(
            "systemPersonnelCount"
        );

    const evidenceCount =
        document.getElementById(
            "evidencePersonnelCount"
        );


    if (systemCount) {

        systemCount.textContent =
            personnelData.systemAccess.length;

    }


    if (evidenceCount) {

        evidenceCount.textContent =
            personnelData.evidenceHandlers.length;

    }

}


/* =========================================
   RENDER SYSTEM PERSONNEL
========================================= */

function renderSystemPersonnel() {

    const table =
        document.getElementById(
            "systemPersonnelTable"
        );


    if (!table) {
        return;
    }


    if (personnelData.systemAccess.length === 0) {

        table.innerHTML = `
            <tr class="empty-row">
                <td colspan="6">
                    No system personnel registered yet.
                </td>
            </tr>
        `;

        return;
    }


    table.innerHTML =
        personnelData.systemAccess
            .map(person => {

                return `
                    <tr>

                        <td>
                            ${escapeHTML(person.id)}
                        </td>

                        <td>
                            ${escapeHTML(person.name)}
                        </td>

                        <td>
                            ${escapeHTML(person.role)}
                        </td>

                        <td>
                            ${escapeHTML(person.department)}
                        </td>

                        <td>
                            ${escapeHTML(person.status)}
                        </td>

                        <td>
                            Authorized
                        </td>

                    </tr>
                `;

            })
            .join("");

}


/* =========================================
   RENDER EVIDENCE HANDLERS
========================================= */

function renderEvidenceHandlers() {

    const table =
        document.getElementById(
            "evidencePersonnelTable"
        );


    if (!table) {
        return;
    }


    if (personnelData.evidenceHandlers.length === 0) {

        table.innerHTML = `
            <tr class="empty-row">
                <td colspan="6">
                    No evidence handlers registered yet.
                </td>
            </tr>
        `;

        return;
    }


    table.innerHTML =
        personnelData.evidenceHandlers
            .map(person => {

                return `
                    <tr>

                        <td>
                            ${escapeHTML(person.id)}
                        </td>

                        <td>
                            ${escapeHTML(person.name)}
                        </td>

                        <td>
                            ${escapeHTML(person.role)}
                        </td>

                        <td>
                            ${escapeHTML(person.department)}
                        </td>

                        <td>
                            ${escapeHTML(person.biometric)}
                        </td>

                        <td>
                            ${escapeHTML(person.status)}
                        </td>

                    </tr>
                `;

            })
            .join("");

}


/* =========================================
   HTML ESCAPING
========================================= */

function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }


    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


/* =========================================
   ADD PERSONNEL BUTTON
========================================= */

const addPersonnelButton =
    document.getElementById(
        "addPersonnelButton"
    );


if (addPersonnelButton) {

    addPersonnelButton.addEventListener(
        "click",
        () => {

            alert(
                "Personnel registration form will be connected here."
            );

        }
    );

}


/* =========================================
   INITIALIZE
========================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        updatePersonnelCounts();

        renderSystemPersonnel();

        renderEvidenceHandlers();

    }
);