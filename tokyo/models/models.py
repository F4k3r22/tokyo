from typing import Callable, List, Dict, Union
from dataclasses import dataclass
import re

@dataclass
class Routes:
    pattern: str # Ok esto agarra la ruta original like: "/user/{user_id}"
    handler: Callable # Esta seria la función que ejecuta la ruta like: def user(user_id: int):...
    methods: List[str] # Metodos permitido: GET, POST, PUT, etc.
    regex: re.Pattern # REGEX - Expresión regular compilada para matching like: (r"/user/(?P<user_id>\d+))
    param_names: List[str] # nombre de los parametros extraidos del regex
    param_types: Dict[str, str] # nombre del parametro y el tipo de dato que corresponde

class Request:
    """Request object simplificado"""
    def __init__(self, scope: dict, body: bytes = b''):
        pass

class Response:
    """Response object simplificado"""
    def __init__(self, content: Union[str, dict, list] = "", status_code: int = 200):
        pass