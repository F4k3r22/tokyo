# tokyo: Creating an ASGI server and its minimalist web framework from scratch

This is all an experiment and a way to learn how ASGI servers and web frameworks work. I hope to soon write a blog post explaining step-by-step how to implement everything I've done with `Tokyo`

## Install:
```bash
git clone https://github.com/F4k3r22/tokyo.git

cd tokyo && pip install . && rm -rf build && rm -rf tokyo.egg-info && cd ..
```

## Basic use:
```python
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
```

> The only allowed methods are: `GET`, `POST`, `PUT` and `DELETE`