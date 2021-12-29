import requests
import json

api_url = "http://localhost:3000/systems/should-water"
payload = {"id": "1", "key": "12345"}

response = requests.get(api_url, params=payload)

if response.status_code == 200:
    print("Yes!")
elif response.status_code == 404:
    print("System not found")
elif response.status_code == 401:
    print("Wrong API-Key")
else:
    print("Something weird happened")
