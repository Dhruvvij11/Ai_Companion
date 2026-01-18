import tkinter as tk
from state import state

STATE_COLORS = {
    "idle": "#9aa0a6",       # gray
    "listening": "#1a73e8",  # blue
    "thinking": "#fbbc04",   # yellow
    "speaking": "#34a853",   # green
}

STATE_TEXT = {
    "idle": "Idle",
    "listening": "Listening",
    "thinking": "Thinking",
    "speaking": "Speaking",
}


class CompanionUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Companion")
        self.root.geometry("120x120")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.overrideredirect(True)  # no window chrome

        self.frame = tk.Frame(self.root, bg=STATE_COLORS["idle"])
        self.frame.pack(fill="both", expand=True)

        self.label = tk.Label(
            self.frame,
            text=STATE_TEXT["idle"],
            fg="white",
            bg=STATE_COLORS["idle"],
            font=("Segoe UI", 12, "bold")
        )
        self.label.pack(expand=True)

        # Drag support
        self.frame.bind("<Button-1>", self.start_move)
        self.frame.bind("<B1-Motion>", self.do_move)

        self.update_loop()

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = event.x_root - self._x
        y = event.y_root - self._y
        self.root.geometry(f"+{x}+{y}")

    def update_loop(self):
        ui_state = getattr(state, "ui_state", "idle")
        color = STATE_COLORS.get(ui_state, STATE_COLORS["idle"])
        text = STATE_TEXT.get(ui_state, "Idle")

        self.frame.config(bg=color)
        self.label.config(text=text, bg=color)

        self.root.after(100, self.update_loop)  # refresh 10x/sec

    def run(self):
        self.root.mainloop()


def start_ui():
    ui = CompanionUI()
    ui.run()
