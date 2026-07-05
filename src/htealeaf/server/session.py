from dataclasses import dataclass
from time import time
from typing import OrderedDict
from uuid import uuid4


class SessionData(dict):
    """
    A session object that behaves like a dictionary but allows attribute-style access.
    """

    def has(self, attr):
        """Checks if a session attribute exists."""
        return self.get(attr) is not None

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(f"'Session' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        self[attr] = value


@dataclass
class Session:
    exp: float
    data: SessionData

    def __init__(self, exp: float) -> None:
        self.exp = exp
        self.data = SessionData()

    def ttl(self):
        return max(0, self.exp - time())


class SessionManager:
    def __init__(self, max_ttl=10_000) -> None:
        self.sessions: OrderedDict[str, Session] = OrderedDict()
        self.max_ttl = max_ttl
        self.next_eviction = time() + self.max_ttl

    def create(self, session_id=None):
        """Generates a unique session ID."""
        session_id = session_id or str(uuid4())
        exp = time() + self.max_ttl

        self.sessions[session_id] = Session(exp)
        self.sessions.move_to_end(session_id)
        return session_id

    def exist(self, session_id):
        session = self.sessions.get(session_id)
        if session is None or session.ttl() == 0:
            return False
        return True

    def _check_evict(self):
        while self.sessions:
            session_id, session = next(iter(self.sessions.items()))

            if session.ttl() > 0:
                self.next_eviction = session.exp
                break

            self.sessions.popitem(last=False)

    def get(self, session_id):
        session = self.sessions.get(session_id)
        if session is None:
            return None
        if session.ttl() == 0:
            del self.sessions[session_id]
            return None

        session.exp = time() + self.max_ttl
        self.sessions.move_to_end(session_id)
        if time() > self.next_eviction:
            self._check_evict()
        return session
