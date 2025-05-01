from maprincess import *
from microbit import *
import utime

"""
   0   1   2

3             4
"""

SPEED = 20
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

def detectGrid(sensor: int, slp: int) -> bool :
    if 120 <= line_sensor_data(sensor) <= 236 :
        sleep(slp)
        return 1
    else :
        return 0
    
def countGrid(crossedGrid: list[int]) -> list[int] :
    order: list[int]
    if detectGrid(1) :
        sleep(20)
        if detectGrid(1) :
            pass
        
def setUpSpeed(totGrid: int):
    global SPEED
    gridCrossed: int = 0
    tick_zero: int = utime.ticks_ms()
    
    localCount: list[int] = [0,0,0,1]
    crossingMargin: int = utime.ticks_ms()
    
    while gridCrossed < totGrid :
        if utime.ticks_ms() - crossingMargin > 150 :
            crossingMargin = utime.ticks_ms()
            localCount = [0,0,0,1]
            print("reset")

        localCount[0] = detectGrid(0,0)
        localCount[1] = detectGrid(0,0)
        localCount[2] = detectGrid(0,0)
            
        if localCount == [1,1,1,1] :
            localCount[3] = 0
            gridCrossed += 1
            print("grid num:", gridCrossed)
            sleep(60)
            
        motor_run(Motor.ALL, SPEED)
    
    motor_stop()
    
    return totGrid / (utime.ticks_ms() - tick_zero)

        
'''
def getDir(head_zero: float) -> (int, float) :
    head: float = 0
    direction: int = 0
    #error: float
    
    for i in range(0,5) :
        head += mq_heading()
    head = head / 5
    print(head)

    if (head_zero - 45) % 359 < head < (head_zero + 45) % 359 :
        direction = 0
    elif (head_zero + 45) % 359 < head < (head_zero + 135) % 359 :
        direction = 1
    elif (head_zero + 135) % 359 < head < (head_zero + 225) % 359 :
        direction = 2
    elif (head_zero + 225) % 359 < head < (head_zero + 315) % 359 :
        direction = 3
    
    return direction
'''

        
def main() -> None :
    print("prog running...")
    
    
    led_rgb(Color.WHITE, brightness=255)
    realSpeed: float = setUpSpeed(5)
    
    if button_a.was_pressed() :
        
        grid: int = 0
        
        while True :
            Move()
            #grid += countGrid()
            #print(grid)
            #print("head0:",mq_heading())
            #print(getDir(head_zero))
            sleep(50)
        
        motor_stop()
    

if __name__ == "__main__" :
    main()
