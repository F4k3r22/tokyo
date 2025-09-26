from typing import Callable, List, Dict, Union
from dataclasses import dataclass
import re
import json

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
        self.method = scope['method'] # Utilizamos scope para obtener el metodo, ruta, y los headers, al parecer siempre van a ser diccionarios
        self.path = scope['path']
        self.headers = dict(scope.get('headers', []))
        self.query_params = self._parse_query(scope.get('query_string', b''))
        self.body = body # Cuerpo de la Request
        self.path_params = {}  # Se llena durante routing
        self._json_cache = None

    def _parse_query(self, query_string: bytes) -> dict:
        if not query_string:
            return {}
        # Parsing básico: key=value&key2=value2
        params = {}
        for part in query_string.decode().split('&'): # Siempre va a tocar decodificar del formato ASCII para obtener todo lo necesario
            if '=' in part:
                key, value = part.split('=', 1)
                params[key] = value
        return params

    def json(self) -> dict:
        # Parsea body como JSON
        if self._json_cache is None and self.body:
            try:
                self._json_cache = json.loads(self.body.decode())
            except:
                self._json_cache = {}
        return self._json_cache or {}

class Response:
    """Response object simplificado"""
    def __init__(self, content: Union[str, dict, list] = "", status_code: int = 200):
        self.status_code = status_code

        if isinstance(content, (dict, list)):
            self.content = json.dumps(content, ensure_ascii=False)
            self.content_type = "application/json"
        else:
            self.content = str(content)
            self.content_type = "text/plain"

    def to_asgi_response(self):
        # Enviamos la respuesta en el formato correcto
        body = self.content.encode('utf-8')
        return {
            'status': self.status_code,
            'headers': [
                [b'content-type', self.content_type.encode()],
                [b'content-length', str(len(body)).encode()]
            ],
            'body': body
        }