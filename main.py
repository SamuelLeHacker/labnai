from microbit import *
from maprincess import *
import utime
import music


'''
### Infrared Sensor Layout ###

           0  1  2
           

    3                    4
   

'''


SPEED: int = 30
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


def setUpDirections() -> list[float] :
    
    head_zero: list[float] = [0, 0, 0, 0]
    
    compass.clear_calibration()
    compass.calibrate()
    
    while button_b.was_pressed() != True :
        pass
    head_zero[0] = mq_heading()
    led_rgb(Color.BLUE, brightness=255)
    music.play("C6")
    led_rgb(Color.RED, brightness=255)
    
    while button_b.was_pressed() != True :
        pass
    head_zero[1] = mq_heading()
    led_rgb(Color.BLUE, brightness=255)
    music.play("C6")
    led_rgb(Color.RED, brightness=255)
    
    while button_b.was_pressed() != True :
        pass
    head_zero[2] = mq_heading()
    led_rgb(Color.BLUE, brightness=255)
    music.play("C6")
    led_rgb(Color.RED, brightness=255)
    
    while button_b.was_pressed() != True :
        pass
    head_zero[3] = mq_heading()
    led_rgb(Color.BLUE, brightness=255)
    music.play("C6")
    
    return head_zero


def getDirection(head_zero: float) -> (int, float) :
    direction: int
    intensity: float
    
    head_now: float = 0#= mq_heading()
    head_dist: list[float] = [0, 0, 0, 0]
    
    for i in range(0,20) :
        head_now += mq_heading()
        sleep(2)
    head_now = head_now / 20
    
    for i in range(0,4) :
        head_dist[i] = abs(head_zero[i] - head_now)

    direction = head_dist.index(min(head_dist))
    
    if head_now <= head_zero[direction] :
        intensity = head_now / head_zero[direction]
    elif head_now > head_zero[direction] :
        intensity = (head_now / head_zero[direction]) -2
    
    return direction, intensity


#def changeDirection(head_zero:list[int], dir: list[int,float], new_dir: int) -> None :

def adjustDirection(direction: list[int, float], slp: int) -> None :
    if direction[1] < 0 :
        motor_run(Motor.LEFT, SPEED)
        motor_run(Motor.RIGHT, -SPEED)
        print("turn LEFT")
        sleep(slp)
    
    elif direction[1] > 0 :
        motor_run(Motor.LEFT, -SPEED)
        motor_run(Motor.RIGHT, SPEED)
        print("turn RIGHT")
        sleep(slp)
    
    motor_stop()

        
def main() -> None :
    grid: int
    realSpeed: float
    head_zero: list[float] #front, right, back, left
    direction: list[int,float] #heading, intensity
    
    '''states variables'''
    initialization: list[bool] = [True, False]
    start: bool = False
    forward: bool = False
    
    print("prog running...")
        
    motor_stop()
    led_rgb(Color.GREEN, brightness=255)
    music.play(TUNE_START)
    sleep(2000)
    led_rgb(Color.RED, brightness=255)
    music.play(TUNE_NEGATIVE)    
    
    while initialization != [True, True]:
        led_rgb(Color.RED, brightness=255)
    
        if button_a.was_pressed() :
            ''' setting up the speed '''
            realSpeed = setUpSpeed(5)
            grid = 0
            
            print("robot speed initialized")
            
            initialization[0] = True
            led_rgb(Color.GREEN, brightness=255)
            music.play(TUNE_POSITIVE)
            
            
        if button_b.was_pressed() :
            ''' setting up the compass '''
            head_zero = setUpDirections()
            
            print("robot is initially heading: ", head_zero)
            print("robot compass initialized.")
            
            initialization[1] = True
            led_rgb(Color.GREEN, brightness=255)
            music.play(TUNE_POSITIVE)
    
    tick = utime.ticks_ms()
    
    while start != True :
        if utime.ticks_ms() - tick > 6000 :
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
    
    while True :
        if button_b.was_pressed() :
            
            for i in range(0,10) :
                direction = getDirection(head_zero)
                print(direction)
                adjustDirection(direction, 70)
                sleep(100)
            sleep(200)
            for i in range(0,10) :
                direction = getDirection(head_zero)
                print(direction)
                adjustDirection(direction, 25)
                sleep(100)
                
        sleep(700)
            
    
    motor_stop()
    

if __name__ == "__main__" :
    main()
