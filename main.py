from maprincess import *
from microbit import *

"""
   0   1   2

3             4
"""
SPEED = 19
S_SPEED = 18
SS_SPEED = 13
def Move() -> None :
    token: bool = True
    
    if line_sensor_data(0) > 60 and line_sensor_data(1) <= 60  and  token == True:
        motor_run(Motor.LEFT, SPEED)
        motor_run(Motor.RIGHT, S_SPEED)
        sleep(10)
        token = False
        
    if line_sensor_data(2) > 60 and line_sensor_data(1) <= 60 and token == True:
        motor_run(Motor.RIGHT, SPEED)
        motor_run(Motor.LEFT, S_SPEED)
        sleep(10)
        token = False
        
    if line_sensor_data(3) > 60 and line_sensor_data(4) <= 60  and token == True:
        motor_run(Motor.LEFT, SPEED)
        motor_run(Motor.RIGHT, SS_SPEED)
        sleep(10)
        token = False
        
    if line_sensor_data(3) <= 60 and line_sensor_data(4) > 60 and token == True:
        motor_run(Motor.RIGHT, SPEED)
        motor_run(Motor.LEFT, SS_SPEED)
        sleep(10)
        token = False
        
    if line_sensor_data(0) > 60 and line_sensor_data(2) > 60 and token == True :
        motor_run(Motor.ALL, SPEED)
        sleep(10)
        token = False
        
    if line_sensor_data(0) <= 60 and line_sensor_data(2) <= 60 and token == True:
        motor_stop()
        sleep(10)
        token = False

def countGrid() -> int :
    if 110 <= line_sensor_data(1) <= 231 :
        sleep(10)
        return 1
    else:
        return 0
        
def main() -> None :
    print("prog running...")
    led_rgb(Color.WHITE, brightness=255)
    grid = 0
    
    while True:
        Move()
        grid += countGrid()
        print(grid)

if __name__ == "__main__" :
    main()
    """
    while True :
        print(line_sensor_data(0))
        sleep(50)
    
    """
        
