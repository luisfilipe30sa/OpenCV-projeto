

import RPi.GPIO as gpio
import time
gpio.setwarnings(False)
# Configurando como BOARD, Pinos Fisicos
gpio.setmode(gpio.BOARD)
# Configurando a direcao do Pino
gpio.setup(32, gpio.OUT)
gpio.setup(36, gpio.OUT)
gpio.setup(38, gpio.OUT)
# Usei 11 pois meu setmode é BOARD, se estive usando BCM seria 17
while True:
    gpio.output(32, gpio.HIGH)
    time.sleep(1)
    gpio.output(32, gpio.LOW)
    time.sleep(1)
    gpio.output(36, gpio.HIGH)
    time.sleep(1)
    gpio.output(36, gpio.LOW)
    time.sleep(1)
    gpio.output(38, gpio.HIGH)
    time.sleep(1)
    gpio.output(38, gpio.LOW)
    time.sleep(1)
 
# Desfazendo as modificações do GPIO
gpio.cleanup()
