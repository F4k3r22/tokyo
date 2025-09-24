from typing import Callable, List
from tokyo.models import Routes, Response, Request

class Tokyo:
    """
        Framework minimalista para experimentar y aprender
    """
    def __init__(self):
        self.routes: List[Routes] = []
        self.middlewares: List[Callable] = []