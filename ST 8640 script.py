import RPi.GPIO as GPIO
import modules
import warnings
import xmlrpc.client
warnings.filterwarnings("ignore", category = DeprecationWarning)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setwarnings(False)


while True:
    inputValue = GPIO.input(18)
    if (inputValue == False):
        modules.red_led_off()
        modules.green_led_off()
        #print("Script started")
        serial_scrapped = modules.firmware_operations()
        odoo_serial = modules.veryfi_odoo_serial(serial_scrapped)
        #print(odoo_serial)
        modules.yellow_led_off()

