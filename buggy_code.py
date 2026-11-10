from typing import Any
from dataclasses import dataclass

@dataclass
class Message:
    payload: Any
    timestamp: int
    sender_id: int

class LamportClock:
    """Базова реалізація логічного годинника Лемпорта."""
    def __init__(self, pid: int):
        self.pid = pid
        self.time = 0

    def tick(self) -> int:
        self.time += 1
        return self.time

    def send(self, payload: Any = None) -> Message:
        self.time += 1
        return Message(payload=payload, timestamp=self.time, sender_id=self.pid)

    def recv(self, msg: Message) -> int:
        self.time = max(self.time, msg.timestamp) + 1
        return self.time

class Process:
    """Приклад процесу з чергами надсилання/отримання. (Варіант 5)"""
    inbox = []  # Помилка 1: Атрибут класу (спільна черга)

    def __init__(self, pid: int):
        self.clock = LamportClock(pid)

    def local_event(self) -> int:
        return self.clock.tick()

    def send_to(self, other: "Process", payload: Any = None) -> Message:
        msg = self.clock.send(payload=payload)
        other.inbox.append(msg)
        return msg

    def recv_one(self) -> int:
        if not self.inbox:
            raise IndexError("Inbox порожній")
        msg = self.inbox.pop(0)  # Помилка 2: O(N) та непотокобезпечно
        return self.clock.recv(msg)