from tokyo import Tokyo
from tokyo.models import Request, Response
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

app = Tokyo()

logger = logging.getLogger("Tokyo App")

@app.middleware
def logging_md(request: Request):
    logger.info(f"{request.method} {request.path}")

@app.get("/hello")
async def hello():
    return {"status": "succes",
            "messages": "Hello world from Tokyo"}

@app.post("/sum")
async def sum_fun(request: Request):
    req = request.json()
    try:
        num1 = int(req.get("num1"))
        num2 = int(req.get("num2"))
        res = num1 + num2

        return {"sum": res}
    except:
        return Response({"status": "error",
                        "content": "Unknown error"}, 500)

if __name__ == "__main__":
    app.run("0.0.0.0", port=8000)