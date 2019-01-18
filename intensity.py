from boltiot import Bolt
import config
import json
import time

blt = Bolt(config.API_KEY, config.DEVICE_ID)

while True:
    resp = blt.analogRead('A0')
    data = json.loads(resp)
    print(data['value'])
    time.sleep(10)
