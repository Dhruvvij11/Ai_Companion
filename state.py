class AppState:
    def __init__(self):
        self.running = True
        self.idle_time = 0
        self.last_event = None
        self.current_emotion = "neutral" 
        self.current_intent = "normal"


state = AppState()
