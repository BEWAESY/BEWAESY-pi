# BEWAESY-pi
## Setup
1. Copy this repo on your Raspberry Pi under the ``/home/pi/BEWAESY/`` directory
2. Install the required Python components for the DHT sensor:
    ```bash
    pip3 install adafruit-circuitpython-dht
    ```
    ```bash
    sudo apt-get install libgpiod2
    ```
3. Add a Cronjob to run the python script every minute:

    ```bash
    sudo nano /etc/crontab
    ```
    Copy this line into the file:
    ```bash
    *  *    * * *   pi      cd ~/BEWAESY/ && python3 water.py >> log.txt
    ```
