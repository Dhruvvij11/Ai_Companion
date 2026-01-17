from collections import deque

MAX_TURNS = 4   # you can change this later

class ShortTermMemory:
    def __init__(self):
        self.buffer = deque(maxlen=MAX_TURNS * 2)
        # *2 because user + AI = one turn

    def add_user(self, text):
        self.buffer.append({"role": "user", "content": text})

    def add_ai(self, text):
        self.buffer.append({"role": "ai", "content": text})

    def get_context(self):
        if not self.buffer:
            return ""
        
        lines = []
        for item in self.buffer:
            if item["role"] == "user":
                lines.append(f"User: {item['content']}")
            else:
                lines.append(f"AI: {item['content']}")
        return "\n".join(lines)

memory = ShortTermMemory()
