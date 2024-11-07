import time
import json
import paho.mqtt.client as mqtt
from w1thermsensor import W1ThermSensor
import ADC0832
import RPi.GPIO as GPIO

THINGSBOARD_HOST = 'demo.thingsboard.io'
ACCESS_TOKEN = 'DHT22_TOKEN_BUJOLDZACK'

INTERVAL = 2
sensor_data = {'temperature': 0, 'lux': 0}
MAX_VOLTAGE = 3.3
MAX_ADC_VALUE = 255
LED_PIN_LIGHT = 26

temp_sensor = W1ThermSensor()
ADC0832.setup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN_LIGHT, GPIO.OUT)

def get_lux(adc_value):
    voltage = MAX_VOLTAGE / MAX_ADC_VALUE * adc_value
    lux = voltage * 100
    return lux

client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()

next_reading = time.time()

try:
    while True:
        temp = temp_sensor.get_temperature()
        
        adc_value = ADC0832.getADC(0)
        lux = get_lux(adc_value)

        if lux < 10:
            GPIO.output(LED_PIN_LIGHT, GPIO.LOW)
        else:
            GPIO.output(LED_PIN_LIGHT, GPIO.HIGH)

        sensor_data['temperature'] = round(temp, 2)
        sensor_data['lux'] = round(lux, 2)
        print(f"Temperature: {sensor_data['temperature']}°C, Lux: {sensor_data['lux']}")

        client.publish('v1/devices/me/telemetry', json.dumps(sensor_data), 1)

        next_reading += INTERVAL
        sleep_time = next_reading - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

except KeyboardInterrupt:
    pass

finally:
    client.loop_stop()
    client.disconnect()
    ADC0832.destroy()
    GPIO.cleanup()
