import RPi.GPIO as GPIO
import time
WHITE = 26
RED = 19
BLUE = 13
YELLOW = 6


class PiControls:

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(2, GPIO.OUT)
        GPIO.setup(3, GPIO.OUT)
        GPIO.setup(27, GPIO.OUT)
        GPIO.setup(17, GPIO.OUT)
        GPIO.setup(WHITE, GPIO.OUT)
        GPIO.setup(RED, GPIO.OUT)
        GPIO.setup(BLUE, GPIO.OUT)
        GPIO.setup(YELLOW, GPIO.OUT)
        self.chan_list = [2, 3, 27, 17]  # also works with tuples
        self.led_chanel_list = [RED, BLUE, YELLOW]

    def no_led_flash(self):
        GPIO.output(self.led_chanel_list, (GPIO.LOW, GPIO.LOW, GPIO.LOW))

    def flash_red(self):
        GPIO.output(self.led_chanel_list, (GPIO.HIGH, GPIO.LOW, GPIO.LOW))

    def flash_blue(self):
        GPIO.output(self.led_chanel_list, (GPIO.LOW, GPIO.HIGH, GPIO.LOW))

    def flash_yellow(self):
        GPIO.output(self.led_chanel_list, (GPIO.LOW, GPIO.LOW, GPIO.HIGH))

    def flash_white(self):
        GPIO.output([WHITE], GPIO.HIGH)

    def no_flash_white(self):
        GPIO.output([WHITE], GPIO.LOW)

    def move_forward(self):
        GPIO.output(self.chan_list, (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH))
        time.sleep(3)
        GPIO.output(self.chan_list, (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW))

    def move_backward(self):
        GPIO.output(self.chan_list, (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH))
        time.sleep(3)
        GPIO.output(self.chan_list, (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW))

    def move_left(self):
        GPIO.output(self.chan_list, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.HIGH))
        time.sleep(3)
        GPIO.output(self.chan_list, (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW))

    def move_right(self):
        GPIO.output(self.chan_list, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
        time.sleep(3)
        GPIO.output(self.chan_list, (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW))


