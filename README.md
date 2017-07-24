# iotMonitor
Occupancy detection based on WiFi signals and prediction using machine learning.

Usage: `sudo python monitor.py -h`

Store data to local Mongo DB: `sudo python monitor.py -d`

Store data to Dynamo DB: `sudo python monitor.py`

optional arguments:
  ```
  -h, --help                              Show this help message and exit
  -i INTERFACE, --interface INTERFACE     Interface to listen on - default wlan0
  -t TIME, --time TIME                    Scanning time in seconds (default 60)
  -d, --database                          Send payload to MongoDB
  -s SLEEP, --sleep SLEEP                 Set sleep time in seconds (default 600)
  ```
