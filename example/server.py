from tokyo import Tokyo

app = Tokyo()

@app.get("/hello")
def hello():
    return {"status": "succes",
            "messages": "Hello world from Tokyo"}

if __name__ == "__main__":
    app.run("0.0.0.0", port=8000)