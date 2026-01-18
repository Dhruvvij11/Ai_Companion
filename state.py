class State:
    def __init__(self):
        self.running = True
        self.ui_state = "idle"
        self.current_emotion = "neutral"
        self.current_intent = "normal"
        self.idle_time = 0


state = State()
