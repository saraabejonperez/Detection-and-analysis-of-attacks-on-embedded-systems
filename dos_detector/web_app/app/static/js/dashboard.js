// ===============================
// API CALLS
// ===============================

async function getStatus() {
    const res = await fetch("/status");
    return await res.json();
}

async function getAlarms() {
    const res = await fetch("/alarms");
    return await res.json();
}

// ===============================
// UPDATE DASHBOARD
// ===============================

async function updateDashboard() {

    try {
        const status = await getStatus();

        // -------- MODEL STATUS --------
        const modelEl = document.getElementById("model_status");

        if (status.model_loaded) {
            modelEl.innerText = "Loaded";
            modelEl.className = "status-ok";
        } else {
            modelEl.innerText = "Not loaded";
            modelEl.className = "status-bad";
        }

        // -------- DETECTION STATUS --------
        const detectionEl = document.getElementById("detection_status");

        if (status.detecting) {
            detectionEl.innerText = "Running";
            detectionEl.className = "status-ok";
        } else {
            detectionEl.innerText = "Stopped";
            detectionEl.className = "status-bad";
        }

        // -------- FLOWS --------
        document.getElementById("flows").innerText =
            status.flows_processed ?? 0;

        // -------- ATTACKS --------
        document.getElementById("attacks").innerText =
            status.attacks_detected ?? 0;

        // ===============================
        // ALARMS
        // ===============================

        const alarmsData = await getAlarms();
        const list = document.getElementById("alarms_list");

        list.innerHTML = "";

        if (!alarmsData.alarms || alarmsData.alarms.length === 0) {
            const item = document.createElement("li");
            item.innerText = "No alarms detected";
            list.appendChild(item);
            return;
        }

        alarmsData.alarms.forEach(a => {

            const item = document.createElement("li");

            item.innerHTML = `
                <span class="alert">
                    ${a.attack_type} (${(a.confidence * 100).toFixed(1)}%)
                </span>
                <br>
                ${a.source_ip} → ${a.destination_ip}
                <br>
                <small>${new Date(a.timestamp * 1000).toLocaleString()}</small>
            `;

            list.appendChild(item);
        });

    } catch (error) {
        console.error("Error updating dashboard:", error);
    }
}

// ===============================
// CONTROLS
// ===============================

async function startDetection() {

    try {
        await fetch("/start_detection", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                interface: "eth0",
                confidence_threshold: 0.8
            })
        });

        updateDashboard();

    } catch (error) {
        console.error("Error starting detection:", error);
    }
}

async function stopDetection() {

    try {
        await fetch("/stop_detection", {
            method: "POST"
        });

        updateDashboard();

    } catch (error) {
        console.error("Error stopping detection:", error);
    }
}

// ===============================
// AUTO REFRESH
// ===============================

// cada 3 segundos
setInterval(updateDashboard, 3000);

// carga inicial
updateDashboard();
/*async function getStatus() {
    const res = await fetch("/status");
    return await res.json();
}

async function getAlarms() {
    const res = await fetch("/alarms");
    return await res.json();
}

async function updateDashboard() {

    try {
        const status = await getStatus();

        document.getElementById("model_status").innerText =
            status.model_loaded ? "Loaded" : "Not loaded";

        document.getElementById("detection_status").innerText =
            status.detecting ? "Running" : "Stopped";

        document.getElementById("flows").innerText =
            status.flows_processed;

        document.getElementById("attacks").innerText =
            status.attacks_detected;

        const alarmsData = await getAlarms();
        const list = document.getElementById("alarms_list");

        list.innerHTML = "";

        alarmsData.alarms.forEach(a => {
            const item = document.createElement("li");

            item.innerHTML = `
                <span class="alert">
                    ${a.attack_type} (${a.confidence})
                </span>
                - ${a.source_ip} → ${a.destination_ip}
            `;

            list.appendChild(item);
        });

    } catch (error) {
        console.error("Error updating dashboard:", error);
    }
}

async function startDetection() {

    await fetch("/start_detection", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            interface: "eth0",
            confidence_threshold: 0.8
        })
    });

    updateDashboard();
}

async function stopDetection() {

    await fetch("/stop_detection", {
        method: "POST"
    });

    updateDashboard();
}

// refresco automático cada 3 segundos
setInterval(updateDashboard, 3000);

// cargar al inicio
updateDashboard();*/