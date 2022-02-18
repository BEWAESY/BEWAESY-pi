import requests
import json
from datetime import datetime
import time
import RPi.GPIO as GPIO
import board
import adafruit_dht

alreadyActivated = False  # Used so that system does not trigger multiple times at once

#
api_url = "https://bewaesy-api.azurewebsites.net/"  # URL to the API
# Get id and API-key from config file, current data in the file is dummy data
with open("config.txt", "r") as f:
    payload = json.loads(f.read())

# Initiate DHT sensor
dhtDevice = adafruit_dht.DHT11(board.D18)
def dhtValues():
  dhtError = -1

  while True:
    if dhtError >= 10:
      return("Error")

    dhtError += 1

    try:
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity

        if dhtError == 0: print("Keine Fehler beim Auslesen des DHT-Sensors")

        return(temperature_c, humidity)
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error


# Check if plant should be watered
def checkData(data):
    print("Check triggers:")

    for value in data[1]:
        # Continue if one trigger already triggered system
        if (alreadyActivated == True): continue

        # Check if value is for temperature or humidity
        if value["eventTrigger"] == "time" and value["triggerValue1"] == datetime.now().strftime("%H:%M"):
            activatePump(data, value)
        elif value["eventTrigger"] == "temperature":
            # Check if value is in temperature range where plant should be watered
            if value["triggerRange"] == "smaller" and dhtResult[0] <= int(value["triggerValue1"]):
                activatePump(data, value)
            elif value["triggerRange"] == "bigger" and dhtResult[0] >= int(value["triggerValue1"]):
                activatePump(data, value)
            else:
                print("- Temperature not in right range")
        elif value["eventTrigger"] == "humidity":
            # Check if value is in humidity range where plant should be watered
            if value["triggerRange"] == "smaller" and dhtResult[1] <= int(value["triggerValue1"]):
                activatePump(data, value)
            elif value["triggerRange"] == "bigger" and dhtResult[1] >= int(value["triggerValue1"]):
                activatePump(data, value)
            else:
                print("- Humidity not in right range")
        else:
            print("- No active event")


# When plant should be watered, check if cooldown is active, and if not water plant
def activatePump(data, value):
    lastExecution = datetime.strptime(data[0][0]["lastExecution"], "%Y-%m-%dT%H:%M:%S.%fZ")

    print("Trigger with ID", value["id"], "fits. Checking cooldown and maxSeconds.")

    # Check if cooldown
    if (datetime.utcnow() - lastExecution).total_seconds() >= data[0][0]["cooldown"]:
        if (data[3] + value["seconds"] <= data[2]):
            print(f"Water Plant for {value['seconds']} seconds")
            global alreadyActivated
            alreadyActivated = True

            # Send data to API that plant was watered
            apiData = {
                "seconds": value["seconds"],
                "timestamp": datetime.utcnow()
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
            print("maxSeconds reached!")
    else:
        print("Cooldown active!")


# Start check
print("---------")
print("Check started at", datetime.utcnow())
print("DHT sensor:")
dhtResult = dhtValues()
print("Current temperature:", dhtResult[0], "°C")
print("Current humidity:", dhtResult[1], "%")
print("---")

weatherData = {
    "temperature": dhtResult[0],
    "humidity":    dhtResult[1]
}

response = requests.get(api_url + "systems/should-water", params=payload, data=weatherData)  # Get data from API

if response.status_code == 200:
    checkData(response.json())
elif response.status_code == 404:
    print("System not found")
elif response.status_code == 401:
    print("Wrong API-Key")
else:
    print("Something weird happened")
