from tokyo import Tokyo
from tokyo.models import Request, Response
import logging
from openai import OpenAI

client = OpenAI()

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

@app.post("/query")
async def query(request: Request):
    req = request.json()

    try:
        prompt = req.get("prompt", "")

        response = client.responses.create(
            model="gpt-5",
            input=prompt
        )
    
        return {"response": response.output_text}
    except Exception as e:
        return Response({"status": "error",
                        "content": f"Error: {e}"}, 500)

if __name__ == "__main__":
    app.run("0.0.0.0", port=8000)