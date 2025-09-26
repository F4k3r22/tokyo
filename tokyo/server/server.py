import httptools
import asyncio
import logging

logger = logging.getLogger(__name__)

class HTTPRequestHandler:
    """Handler para httptools"""
    def __init__(self, server, writer):
        self.server = server
        self.writer = writer
        self.reset()

    def reset(self):
        # Limipiamos todo
        self.method = None
        self.url = None
        self.headers = {}
        self.body = b''
        self.complete = False

    def on_message_begin(self):
        self.reset()

    def on_url(self, url: bytes):
        self.url = url.decode()

    def on_header(self, name: bytes, value: bytes):
        self.headers[name.decode().lower()] = value.decode()
    
    def on_headers_complete(self):
        pass
    
    def on_body(self, body: bytes):
        self.body += body
    
    def on_message_complete(self):
        self.complete = True
        # Programar procesamiento
        asyncio.create_task(self.server.process_request(self))

class TokyoASGIServer:
    """Servidor ASGI simple"""
    def __init__(self, app, host: str = "localhost", port: int = 8000):
        self.app = app
        self.host = host
        self.port = port

    async def start(self):
        server = await asyncio.start_server(
            self.handle_connection,
            self.host,
            self.port
        )

        logger.info(f"Server running on: http://{self.host}:{self.port}")

        async with server:
            await server.serve_forever()
    
    async def handle_connection(self, reader, writer):
        # Maneja conexión TCP
        try:
            # Leer datos
            data = await reader.read(8192)
            if not data:
                return
            
            # Crear handler httptools
            handler = HTTPRequestHandler(self, writer)
            parser = httptools.HttpRequestParser(handler)
            
            # Parsear con httptools
            parser.feed_data(data)
            
        except Exception as e:
            print(f"❌ Error en conexión: {e}")
        
        # La respuesta se maneja en process_request

    async def process_request(self, handler: HTTPRequestHandler):
        # Procesa petición parseada por httptools
        try:
            if not handler.complete:
                return
            
            # Crear ASGI scope
            scope = {
                'type': 'http',
                'method': 'GET',  # httptools no expone método directamente
                'path': handler.url.split('?')[0] if handler.url else '/',
                'query_string': (handler.url.split('?')[1] if '?' in (handler.url or '') else '').encode(),
                'headers': [[k.encode(), v.encode()] for k, v in handler.headers.items()],
            }
            
            # Inferir método de headers o URL (simplificado)
            if 'content-length' in handler.headers or handler.body:
                scope['method'] = 'POST'
            
            # Crear funciones ASGI
            receive_queue = asyncio.Queue()
            await receive_queue.put({
                'type': 'http.request',
                'body': handler.body,
                'more_body': False
            })
            
            response_parts = []
            
            async def receive():
                return await receive_queue.get()
            
            async def send(message):
                if message['type'] == 'http.response.start':
                    status = message['status']
                    headers = message.get('headers', [])
                    
                    response = f"HTTP/1.1 {status} OK\r\n"
                    for name, value in headers:
                        response += f"{name.decode()}: {value.decode()}\r\n"
                    response += "\r\n"
                    response_parts.append(response.encode())
                
                elif message['type'] == 'http.response.body':
                    body = message.get('body', b'')
                    response_parts.append(body)
            
            # Ejecutar app ASGI
            await self.app(scope, receive, send)
            
            # Enviar respuesta
            for part in response_parts:
                handler.writer.write(part)
            await handler.writer.drain()
            
        except Exception as e:
            logging.error(f"Error procesando: {e}")
        finally:
            handler.writer.close()
            await handler.writer.wait_closed()