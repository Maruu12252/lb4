from typing import Any
from dataclasses import dataclass
import queue

@dataclass
class Message:
    payload: Any
    timestamp: int
    sender_id: int

class LamportClock:
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

class ProcessFixed:
    """Виправлений процес із ізольованою та безпечною чергою повідомлень."""
    
    def __init__(self, pid: int):
        self.clock = LamportClock(pid)
        # Виправлення 1 та 2: Ізольована (self) та потокобезпечна (Queue) черга
        self.inbox = queue.Queue()

    def local_event(self) -> int:
        return self.clock.tick()

    def send_to(self, other: "ProcessFixed", payload: Any = None) -> Message:
        # Інкремент локального годинника відбувається всередині self.clock.send()
        msg = self.clock.send(payload=payload)
        other.inbox.put(msg)
        return msg

    def recv_one(self) -> int:
        try:
            # Витягуємо повідомлення без блокування
            msg = self.inbox.get_nowait()
        except queue.Empty:
            raise IndexError("Inbox порожній")
            
        # Оновлення часу (max + 1) відбувається всередині self.clock.recv()
        return self.clock.recv(msg)