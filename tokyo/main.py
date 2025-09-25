from typing import Callable, List, Optional
from tokyo.models import Routes, Response, Request
import re
import logging
import inspect

logger = logging.getLogger(__name__)


class Tokyo:
    """
        Framework minimalista para experimentar y aprender
    """
    def __init__(self, name: str | None = "Tokyo"):
        self.routes: List[Routes] = []
        # Los Middlewares los vamos a majenar como funciones

        self.middlewares: List[Callable] = []
        self.name = name

        logging.info(f"Launching App: {self.name}")


    def route(self, path: str, methods: List[str]):
        if methods is None:
            methods = ['GET']

        def decorator(handler: Callable):
            # Ok aqui extraemos todo lo necesario para registrarlo como ruta
            regex_pattern, param_names, param_types = self._compile_pattern(path)
            # aplicamos el regex
            compiled_regex = re.compile(f"^{regex_pattern}$")

            # Aqui registramos la ruta
            route = Routes(
                pattern=path,
                handler=handler,
                methods=[m.upper() for m in methods],
                regex=compiled_regex,
                param_names=param_names,
                param_types=param_types
            )


            # manejamos globalmente las rutas con una lista
            # puede ser ineficiente o tener el mismo problema de FastAPI
            # SI. Pero es un ejemplo simple
            self.routes.append(route)
            return handler

        return decorator

    def _compile_pattern(self, pattern: str) -> tuple:
        param_names = []
        param_types = {}

        def replace_param(match):
            param_def = match.group(1)
            if ':' in param_def:
                name, param_type = param_def.split(':', 1)
            else:
                name, param_type = param_def, 'str'
            
            param_names.append(name)
            param_types[name] = param_type
            
            type_patterns = {
                'str': r'[^/]+',
                'int': r'\d+',
                'float': r'\d+\.?\d*',
                'path': r'.+'
            }
            
            regex = type_patterns.get(param_type, r'[^/]+')
            return f"(?P<{name}>{regex})"

        regex_pattern = re.sub(r'\{([^}]+)\}', replace_param, pattern)
        return regex_pattern, param_names, param_types

    def get(self, path):
        # Metodos para hacer que la sintaxis se parezca a la de FastAPI
        # Me es más facil manejar la sintaxis asi
        return self.route(path, ['GET'])

    def post(self, path):
        return self.route(path, ['POST'])

    def put(self, path: str):
        return self.route(path, ['PUT'])
    
    def delete(self, path: str):
        return self.route(path, ['DELETE'])

    def middleware(self, func: Callable):
        self.middlewares.append(func)
        return func

    def _find_route(self, path: str, method: str) -> Optional[tuple]:
        # OJO ESTO ES PARA PODER MANEJAR EL PROCESO COMPLETO DE
        # REQUEST (Dirijir la petición a la ruta correcta) Y RESPONSE DENTRO DEL MINI FRAMEWORK


        # Buscamos la rutas en la lista global
        for route in self.routes:
            # Si hay una coincidencia validamos que sea con el metodo requerido
            if method.upper() not in route.methods:
                continue
                
            match = route.regex.match(path)
            if match:
                # Extraer y convertir parámetros
                path_params = {}
                for name, value in match.groupdict().items():
                    param_type = route.param_types.get(name, 'str')
                    if param_type == 'int':
                        try:
                            path_params[name] = int(value)
                        except:
                            path_params[name] = value
                    elif param_type == 'float':
                        try:
                            path_params[name] = float(value)
                        except:
                            path_params[name] = value
                    else:
                        path_params[name] = value
                
                return route, path_params
        

        # Como retornamos None y un diccionario vacio, en 
        # el caso que la ruta o el metodo no coincidan
        # Esto va a ser tomado como 404
        return None, {}

    async def _execute_middlewares(self, request: Request) -> Optional[Response]:
        # Solo ejecuta los middlewares
        for middleware in self.middlewares:
            try:
                result = middleware(request)
                # si es asincrono (Recomendable) lo ejecutamos como tal
                if inspect.iscoroutine(result):
                    result = await result
                
                # Si middleware retorna Response, parar la cadena
                if isinstance(result, Response):
                    return result
            except Exception as e:
                logging.error(f"{self.name}: ❌ Error in middleware {middleware.__name__}: {e}")
                return Response({"error": "Middleware error"}, 500)
        return None

    async def _handle_request(self, request: Request): #-> Response: # Despues lo implemento, ya es tarde (Tambien deberia terminar de implementar el Response y Request)
        # Maneja una petición completa
        pass

    def run(self, host: str = "localhost", port: int = 8000, use_uvloop: bool = True):
        # Ejecuta el servidor con uvloop + httptools
        pass