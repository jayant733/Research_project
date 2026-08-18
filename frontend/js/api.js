const API_BASE = 'http://localhost:8081/api/v1';

class ApiClient {
    async registerClient(profile) {
        const id = `client-${Math.random().toString(36).substr(2, 6)}`;
        const res = await fetch(`${API_BASE}/clients/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ client_id: id, profile })
        });
        return res.json();
    }

    async startRound() {
        const res = await fetch(`${API_BASE}/round/start`, { method: 'POST' });
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
        this.ws = new WebSocket('ws://localhost:8081/ws/dashboard');
        
        this.ws.onopen = () => {
            console.log('Connected to WS');
            dashboardLog('System connected to backend streams.', 'success');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.onMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('WS disconnected, reconnecting...');
            setTimeout(() => this.connect(), 3000);
        };
    }
}
