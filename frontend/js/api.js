const API_BASE = `${window.location.origin}/api/v1`;

class ApiClient {
    async startRun(rounds, seed, mode, options = {}) {
        const res = await fetch(`${API_BASE}/experiment/start`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rounds, seed, mode, ...options })
        });
        const body = await res.json();
        if (!res.ok) {
            throw new Error(body.detail || "Unable to start the run.");
        }
        return body;
    }

    async status() {
        const res = await fetch(`${API_BASE}/status`);
        return res.json();
    }

    async comparison() {
        const res = await fetch(`${API_BASE}/comparison`);
        if (!res.ok) return { available: false, summary: {} };
        return res.json();
    }
}

const api = new ApiClient();

class WebSocketManager {
    constructor(onMessageCallback) {
        this.onMessage = onMessageCallback;
        this.connect();
    }

    connect() {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        this.ws = new WebSocket(`${protocol}://${window.location.host}/ws/dashboard`);
        this.ws.onopen = () => {
            setConnection(true);
            if (window.dashboardLog) {
                window.dashboardLog("Dashboard stream connected.", "success");
            }
        };
        this.ws.onmessage = (event) => {
            this.onMessage(JSON.parse(event.data));
        };
        this.ws.onclose = () => {
            setConnection(false);
            setTimeout(() => this.connect(), 3000);
        };
    }
}

function setConnection(online) {
    const pill = document.getElementById("connection-pill");
    if (!pill) return;
    pill.textContent = online ? "Live" : "Offline";
    pill.className = online ? "pill live" : "pill offline";
}
