/* =========================================================
   DIGI-CoC
   DEVICE MANAGEMENT
   ========================================================= */


/* ---------------------------------------------------------
   TEMPORARY FRONTEND DATA
   --------------------------------------------------------- */

let devices = [

    {
        deviceId: "DEV-001",
        name: "Biometric Unit 01",
        type: "Biometric Unit",
        location: "Evidence Room",
        identifier: "ESP32-001",
        status: "Online",
        lastSeen: "26 Aug 2026, 10:45"
    },

    {
        deviceId: "DEV-002",
        name: "RFID Scanner 01",
        type: "RFID Scanner",
        location: "Evidence Room",
        identifier: "RFID-001",
        status: "Offline",
        lastSeen: "26 Aug 2026, 09:30"
    }

];


/* ---------------------------------------------------------
   ELEMENTS
   --------------------------------------------------------- */

const tableBody =
    document.getElementById("devicesTableBody");

const totalDevices =
    document.getElementById("totalDevices");

const onlineDevices =
    document.getElementById("onlineDevices");

const offlineDevices =
    document.getElementById("offlineDevices");

const deviceAlerts =
    document.getElementById("deviceAlerts");

const searchInput =
    document.getElementById("deviceSearch");

const modal =
    document.getElementById("deviceModal");

const addDeviceBtn =
    document.getElementById("addDeviceBtn");

const closeDeviceModal =
    document.getElementById("closeDeviceModal");

const cancelDeviceBtn =
    document.getElementById("cancelDeviceBtn");

const deviceForm =
    document.getElementById("deviceForm");


/* ---------------------------------------------------------
   RENDER DEVICES
   --------------------------------------------------------- */

function renderDevices(list = devices) {

    tableBody.innerHTML = "";


    if (list.length === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    No devices found.
                </td>
            </tr>
        `;

        return;

    }


    list.forEach(device => {

        const row =
            document.createElement("tr");


        const statusClass =
            device.status
                .toLowerCase()
                .replaceAll(" ", "-");


        row.innerHTML = `

            <td>
                <strong>
                    ${escapeHTML(device.deviceId)}
                </strong>
            </td>


            <td>
                ${escapeHTML(device.name)}
            </td>


            <td>
                ${escapeHTML(device.type)}
            </td>


            <td>
                ${escapeHTML(device.location)}
            </td>


            <td>

                <span class="status-badge ${statusClass}">
                    ${escapeHTML(device.status)}
                </span>

            </td>


            <td>
                ${escapeHTML(device.lastSeen)}
            </td>


            <td>

                <button
                    class="table-action"
                    onclick="viewDevice('${device.deviceId}')"
                >
                    View
                </button>

            </td>

        `;


        tableBody.appendChild(row);

    });

}


/* ---------------------------------------------------------
   UPDATE STATS
   --------------------------------------------------------- */

function updateStats() {

    totalDevices.textContent =
        devices.length;


    onlineDevices.textContent =
        devices.filter(
            device =>
                device.status === "Online"
        ).length;


    offlineDevices.textContent =
        devices.filter(
            device =>
                device.status === "Offline"
        ).length;


    deviceAlerts.textContent =
        devices.filter(
            device =>
                device.status === "Alert"
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

            renderDevices(devices);

            return;

        }


        const filtered =
            devices.filter(device =>

                device.deviceId
                    .toLowerCase()
                    .includes(query)

                ||

                device.name
                    .toLowerCase()
                    .includes(query)

                ||

                device.type
                    .toLowerCase()
                    .includes(query)

                ||

                device.location
                    .toLowerCase()
                    .includes(query)

                ||

                device.status
                    .toLowerCase()
                    .includes(query)

            );


        renderDevices(filtered);

    }
);


/* ---------------------------------------------------------
   MODAL
   --------------------------------------------------------- */

function openDeviceModal() {

    modal.classList.add("show");

}


function closeModal() {

    modal.classList.remove("show");

    deviceForm.reset();

}


addDeviceBtn.addEventListener(
    "click",
    openDeviceModal
);


closeDeviceModal.addEventListener(
    "click",
    closeModal
);


cancelDeviceBtn.addEventListener(
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
   REGISTER DEVICE
   --------------------------------------------------------- */

deviceForm.addEventListener(
    "submit",
    event => {

        event.preventDefault();


        const name =
            document
                .getElementById("deviceName")
                .value
                .trim();


        const type =
            document
                .getElementById("deviceType")
                .value;


        const location =
            document
                .getElementById("deviceLocation")
                .value
                .trim();


        const identifier =
            document
                .getElementById("deviceIdentifier")
                .value
                .trim();


        if (!name || !location) {

            return;

        }


        const nextNumber =
            devices.length + 1;


        const newDevice = {

            deviceId:
                `DEV-${String(nextNumber).padStart(3, "0")}`,

            name,

            type,

            location,

            identifier,

            status:
                "Online",

            lastSeen:
                new Date().toLocaleDateString(
                    "en-GB",
                    {
                        day: "2-digit",
                        month: "short",
                        year: "numeric"
                    }
                )

        };


        devices.unshift(newDevice);


        renderDevices();

        updateStats();

        closeModal();

    }
);


/* ---------------------------------------------------------
   VIEW DEVICE
   --------------------------------------------------------- */

function viewDevice(deviceId) {

    const device =
        devices.find(
            item =>
                item.deviceId === deviceId
        );


    if (!device) {

        return;

    }


    alert(

        `Device: ${device.deviceId}\n` +

        `Name: ${device.name}\n` +

        `Type: ${device.type}\n` +

        `Location: ${device.location}\n` +

        `Hardware ID: ${device.identifier}\n` +

        `Status: ${device.status}\n` +

        `Last Seen: ${device.lastSeen}`

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

renderDevices();

updateStats();