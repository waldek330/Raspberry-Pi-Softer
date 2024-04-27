import RPi.GPIO as GPIO
import time
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as actions
import warnings
import requests
import xmlrpc.client
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ssl import SSLCertVerificationError, SSLContext


login = "admin"
passw = "1234"
url = "http://192.168.1.1/ui/swc/login/index?mode=choose"
path = "/usr/share/applications/chromium-browser.desktop"
firmware_site_address = "http://192.168.1.1/ui/swc/router/firmware/index"
firmware_name = "plik tekstowy.txt"
api_key = "bf4fd965a1f8e2da56f62162d790d06cd5360620"

status_pass = 'PASS'
status_fail = 'FAIL'


def firmware_operations():
    yellow_led_on()
    options = Options()
    options.BinaryLocation = "/usr/bin/chromium-browser"
    driver_path = "/usr/bin/chromedriver"
    driver = webdriver.Chrome(options=options, service=Service(driver_path))
    driver.get(url)
    wait = WebDriverWait(driver, 90)
    login_button = wait.until(EC.presence_of_element_located((By.ID, "loginCtrl")))
    login_button.click()
    user_name_field = driver.find_element_by_xpath("""//*[@id="main_wrapper"]/div[1]/form/div/div/div[2]/table/tbody/tr[1]/td[2]/input""")
    user_name_field.send_keys(login)
    password_field = driver.find_element_by_xpath("""//*[@id="main_wrapper"]/div[1]/form/div/div/div[2]/table/tbody/tr[2]/td[2]/input""")
    password_field.send_keys(passw)
    second_login_button = driver.find_element_by_id("loginCtrl")
    second_login_button.click()
    time.sleep(2)
    serial_number = driver.find_element_by_xpath("""//*[@id="main_wrapper"]/div[1]/table/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/table/tbody/tr[3]/td[3]""").text
    print(serial_number)
    global serial_scrapped 
    serial_scrapped = serial_number
    driver.get(firmware_site_address)
    browse_button = driver.find_element_by_name("file_upload").send_keys("/home/pi/Desktop/"+firmware_name)
    update_firmware_button = driver.find_element_by_xpath("""//*[@id="main_wrapper"]/div[1]/div/div[3]/div[2]/div/form/table[2]/tbody/tr[2]/td[3]/table/tbody/tr/td[2]""").click()
    yellow_led_off()
    green_led_on
    return serial_scrapped

def yellow_led_on():
    YELLOW_LED_PIN = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)
    GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)

    
def yellow_led_off():
    YELLOW_LED_PIN = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)
    GPIO.output(YELLOW_LED_PIN, GPIO.LOW)
    

def green_led_on():
    GREEN_LED_PIN = 22
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
    GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
    
def green_led_off():
    GREEN_LED_PIN = 22
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)

def red_led_on():
    RED_LED_PIN = 20
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.output(RED_LED_PIN, GPIO.HIGH)

def red_led_off():
    RED_LED_PIN = 20
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.output(RED_LED_PIN, GPIO.LOW)

def fail_log_email(serial_scrapped):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "waldemar.lusiak@nksgroup.pl"  # Enter your address
    receiver_email = "waldemar.lusiak@nksgroup.pl"  # Enter receiver address , admin@onservice.pl, remigiusz.zerbst@nksgroup.pl
    password = ''
    subject = 'Error occured during software update on Raspberry Pi softer'
    message = """
     
    This is automatically generated message please do not answer to it.
    
    The problem occured in: {} or it is related to it.""".format(serial_scrapped) #w nawiasach zamieniamy na zmienną którą chcemy przekazać w emailu

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email.split(','), message, subject)

def veryfi_odoo_serial(serial_scrapped):
    try:
        url_stg = "https://sbx-nksgroup.odoo.com"
        db_stg = 'nksgroup-sbx-4964326'
        username = 'waldemar.lusiak@nksgroup.pl'
        password = ''
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_stg))
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url_stg))
        uid = common.authenticate(db_stg, username, password, {})
        #print("UID ", uid)
        list_record = models.execute_kw(db_stg, uid, password, 'stock.production.lot', 'search_read', [[['name', '=', serial_scrapped]]], {'fields': ['name']})
        if len(list_record) == 0:
            fail_log_email(serial_scrapped + ' is the Serial Number provided from router GUI and is not the same as the serial registered in Odoo')
            yellow_led_off()
            green_led_off()
            red_led_on()
        else:
            for objects in list_record:
                odoo_serial = list(objects.values())[1]
                # create insert to the LC- Logs collector for the reporting purposes
                red_led_off()
                green_led_on()
                return odoo_serial
                
    except Exception as e:
        red_led_on()
        raise(fail_log_email(e.__class__))
        




__version__ = '0.1'
