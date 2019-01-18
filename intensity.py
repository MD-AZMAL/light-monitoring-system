from boltiot import Bolt, Email, Sms
import config
import json
import time
import math
import statistics


def compute_bounds(history_data, frame_size, factor):
    if len(history_data) < frame_size:
        return None

    if len(history_data) > frame_size:
        del history_data[0:len(history_data) - frame_size]
    Mn = statistics.mean(history_data)
    Variance = 0
    for data in history_data:
        Variance += math.pow((data - Mn), 2)
    Zn = factor * math.sqrt(Variance / frame_size)
    High_bound = history_data[frame_size - 1] + Zn
    Low_Bound = history_data[frame_size - 1] - Zn
    return [High_bound, Low_Bound]


min_li = 10
max_li = 80


blt = Bolt(config.API_KEY, config.DEVICE_ID)

mailer = Email(config.MAILGUN_API_KEY, config.SANDBOX_URL,
               config.SENDER_EMAIL, config.RECIPIENT_EMAIL)

sms = Sms(config.SSID, config.AUTH_TOKEN,
          config.TO_NUMBER, config.FROM_NUMBER)

history_data = []

while True:
    resp = blt.analogRead('A0')
    data = json.loads(resp)

    if data['success'] != '1':
        print("There was an error while retriving the data.")
        print("This is the error:" + data['value'])
        time.sleep(10)
        continue

    print('The light intensity is {}'.format(data['value']))
    try:
        val = int(data['value'])
        if val < min_li or val > max_li:
            resp = mailer.send_email(
                "Caution", "The Current Intensity is beyond range, its value is " + str(val))
            print('Value out of range : {}, mail sent'.format(val))
    except Exception as e:
        print("Error : ", e)

    bound = compute_bounds(history_data, config.FRAME_SIZE, config.MUL_FACTOR)

    if not bound:
        required_data_count = config.FRAME_SIZE - len(history_data)
        print("Not enough data to compute Z-score. Need ",
              required_data_count, " more data points")
        history_data.append(int(data['value']))
        time.sleep(10)
        continue

    try:
        if val > bound[0] or val < bound[1]:
            response = sms.send_sms("Someone turned on the lights")
            print("This is the response ", response)
        history_data.append(val)
    except Exception as e:
        print("Error", e)
    time.sleep(10)
