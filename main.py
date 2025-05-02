from microbit import *
from maprincess import *
import utime
import music

"""
   0   1   2

3             4
"""

SPEED: int = 20
S_SPEED: int = 13
SS_SPEED: int = 8

TUNE_START = ["C6:1", "E", "G"]
TUNE_POSITIVE = ["F5:1", "G"]
TUNE_NEGATIVE = ["E4:1","C5","E3:1","C3:"]

is_stucked: int = 0
is_super_stucked: int = 0


def Move() -> None :
    token: bool = True
    stoped: bool = False
    global is_stucked #when this variable reach X (8), the robot is concidered stucked
    
    if line_sensor_data(0) <= 60 and line_sensor_data(2) <= 60 and token == True :
        token = False
        stoped = True
        motor_stop()
        sleep(10)
        
    if stoped == True :
        is_stucked += 1
        motor_run(Motor.ALL, -SPEED)
        print("back:", is_stucked)
        sleep(100)
        
    if is_stucked > 6 :
        is_stucked = 0
        #is_super_stucked += 1
        print("STUUUUUUUCKED")
        motor_run(Motor.RIGHT, -35)
        motor_run(Motor.LEFT, 20)
        sleep(800)
    
    if line_sensor_data(0) > 60 and line_sensor_data(2) <= 60  and  token == True :
        motor_run(Motor.LEFT, SPEED)
        motor_run(Motor.RIGHT, 0)
        sleep(10)
        token = False
        
    if line_sensor_data(2) > 60 and line_sensor_data(0) <= 60 and token == True :
        motor_run(Motor.RIGHT, SPEED)
        motor_run(Motor.LEFT, 0)
        sleep(10)
        token = False
        
    if line_sensor_data(3) > 60 and line_sensor_data(4) <= 60  and token == True :
        motor_run(Motor.LEFT, SPEED)
        motor_run(Motor.RIGHT, S_SPEED)
        sleep(10)
        token = False
        
    if line_sensor_data(3) <= 60 and line_sensor_data(4) > 60 and token == True :
        motor_run(Motor.RIGHT, SPEED)
        motor_run(Motor.LEFT, S_SPEED)
        sleep(10)
        token = False
        
    if line_sensor_data(0) > 60 and line_sensor_data(2) > 60 and token == True :
        motor_run(Motor.ALL, SPEED)
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


        
def main() -> None :
    
    print("prog running...")
    led_rgb(Color.GREEN, brightness=255)
    music.play(TUNE_START)
    
    sleep(2000)
    
    led_rgb(Color.RED, brightness=255)
    music.play(TUNE_NEGATIVE)
    
    #heading_set_window_size(20)
    
    head_zero: float = [4] #front, back, left, right
    
    start: bool = False
    initialization: list[bool] = [True, False]
    
    while initialization != [True, True]:
        led_rgb(Color.RED, brightness=255)
    
        if button_a.was_pressed() :
            ''' setting up the speed '''
            realSpeed: float = setUpSpeed(5)
            grid: int = 0
            
            print("robot speed initialized")
            initialization[0] = True
            led_rgb(Color.GREEN, brightness=255)
            music.play(TUNE_POSITIVE)
            
            
        if button_b.was_pressed() :
            ''' setting up the compass '''
            compass.clear_calibration()
            compass.calibrate()
            
            while button_b.was_pressed() != True :
                pass
            head_zero[0] = mq_heading()
            
            while button_b.was_pressed() != True :
                pass
            head_zero[1] = mq_heading()
            
            while button_b.was_pressed() != True :
                pass
            head_zero[2] = mq_heading()
            
            while button_b.was_pressed() != True :
                pass
            head_zero[3] = mq_heading()
            
            print("robot is initially heading: ", head_zero)
            
            print("robot compass initialized.")
            initialization[1] = True
            led_rgb(Color.GREEN, brightness=255)
            music.play(TUNE_POSITIVE)
    
    tick = utime.ticks_ms()
    
    while start != True :
        if utime.ticks_ms() - tick > 10000 :
            led_rgb(Color.RED, brightness=255)
            music.play(TUNE_NEGATIVE)
            led_rgb(Color.GREEN, brightness=255)
            tick = utime.ticks_ms()
        if button_a.was_pressed() or button_b.was_pressed() :
            led_rgb(Color.GREEN, brightness=255)
            music.play(TUNE_POSITIVE)
            music.play(TUNE_POSITIVE)
            sleep(500)
            break
    
    
    led_rgb(Color.RED, brightness=255)
    music.play("C")
    sleep(400)
    
    led_rgb_off()
    sleep(100)
    
    led_rgb(Color.ORANGE, brightness=255)
    music.play("C")
    sleep(400)
    
    led_rgb_off()
    sleep(100)
    
    led_rgb(Color.GREEN, brightness=255)
    music.play("C")
    sleep(400)
    
    led_rgb_off()
    sleep(100)
    
    print("robot num 1 starts operating...")
    
    led_rgb(Color.WHITE, brightness=255)
    music.play("C6")
    sleep(1000)
    
    i = 0
    head = 0
    
    while True :
        head
    
    motor_stop()
    

if __name__ == "__main__" :
    main()
