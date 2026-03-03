from collections import deque

from core import config

MAX_TURNS = 4


class ShortTermMemory:
    def __init__(self):
        self.max_messages = MAX_TURNS * 2
        self.buffer = deque()
        self.summary = deque(maxlen=config.SHORT_MEMORY_SUMMARY_ITEMS)

    def _summarize_evicted(self, item):
        role = "User" if item["role"] == "user" else "AI"
        content = " ".join(str(item["content"]).split())

        if len(content) > config.SHORT_MEMORY_SUMMARY_CHARS:
            content = content[: config.SHORT_MEMORY_SUMMARY_CHARS - 3] + "..."

        self.summary.append(f"{role}: {content}")

    def _append(self, role: str, text: str):
        if len(self.buffer) >= self.max_messages:
            evicted = self.buffer.popleft()
            self._summarize_evicted(evicted)

        self.buffer.append({"role": role, "content": text})

    def add_user(self, text):
        self._append("user", text)

    def add_ai(self, text):
        self._append("ai", text)

    def get_context(self):
        sections = []

        if self.summary:
            sections.append("Earlier summary:\n" + "\n".join(self.summary))

        if self.buffer:
            recent_lines = []
            for item in self.buffer:
                if item["role"] == "user":
                    recent_lines.append(f"User: {item['content']}")
                else:
                    recent_lines.append(f"AI: {item['content']}")
            sections.append("Recent turns:\n" + "\n".join(recent_lines))

        return "\n\n".join(sections)


memory = ShortTermMemory()
