from pyniryo import NiryoRobot
from time import sleep as delay

robot = NiryoRobot('172.21.182.53')

robot.set_led_color([255, 165, 0])

delay(1000)

robot.close_connection()
