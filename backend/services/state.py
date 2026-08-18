class AppState:
    def __init__(self):
        self.clients = {}  # id -> {profile, tier, telemetry}
        self.current_round = 0
        self.total_rounds = 50
        self.metrics_history = []
        
state = AppState()
