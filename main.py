from maprincess import *

"""
   0   1   2

3             4
"""

def Move() :
    while True :
        print("jeofij")
        

led_rgb(Color.WHITE, brightness=50)
        
while True :
    if line_sensor_data(0) > 60 and line_sensor_data(2) > 60 :
        motor_run(Motor.ALL, 40)
    elif line_sensor_data(0) <= 60 and line_sensor_data(2) <= 60 :
        motor_stop(Motor.ALL)
        