import requests as r

print("Try...")

base_url = "http://192.168.1.20:8000"

body = {"num1": 30,
        "num2": 60}

response = r.post(url=f"{base_url}/sum", json=body)

print(f"Response: {response.text}")