import requests
import json
from datetime import datetime
import time
import RPi.GPIO as GPIO

api_url = "http://localhost:3000/"
with open("config.txt", "r") as f:
    payload = json.loads(f.read())


def checkData(data):
    for value in data[1]:
        # Check if value is for temperature or humidity
        if value["eventTrigger"] == "time" and value["triggerValue1"] == datetime.now().strftime("%H:%M"):
            activatePump(data, value)
        else:
            print("No active event")


def activatePump(data, value):
    lastExecution = datetime.strptime(data[0][0]["lastExecution"], "%Y-%m-%dT%H:%M:%S.%fZ")

    # Check if plant should be watered
    if (datetime.now() - lastExecution).total_seconds() >= data[0][0]["cooldown"]:
        print(f"Water Plant for {value['seconds']} seconds")

        # Send data to API that plant was watered
        apiData = {
            "seconds": value["seconds"],
            "timestamp": datetime.now()
        }
        responsePost = requests.post(api_url + "systems/watered-plant", params=payload, data=apiData)
        print(responsePost)

        # Activate pump
        # Start Relay for given time
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(14, GPIO.OUT)

        time.sleep(value["seconds"])

        GPIO.cleanup()
    else:
        print("Cooldown issue!")



response = requests.get(api_url + "systems/should-water", params=payload)

if response.status_code == 200:
    checkData(response.json())
elif response.status_code == 404:
    print("System not found")
elif response.status_code == 401:
    print("Wrong API-Key")
else:
    print("Something weird happened")
