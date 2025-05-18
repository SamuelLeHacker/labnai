from microbit import *
from maprincess import *
import utime
import music
import radio


'''
### Infrared Sensor Layout ###

           2  1  0
           

    4                    3
   

'''


SPEED: int = 40
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
        print("STUUUUUUUCK")
        motor_run(Motor.RIGHT, -35)
        motor_run(Motor.LEFT, 20)
        sleep(800)
    
    if line_sensor_data(0) > 60 and line_sensor_data(2) <= 60  and  token == True :
        motor_run(Motor.LEFT, SPEED)
        motor_run(Motor.RIGHT, 0)
        sleep(10)
        token = False
        
    if line_sensor_data(2) > 60 and line_sensor_data(0) <= 60 and token == True :
        motor_run(Motor.LEFT, 0)
        motor_run(Motor.RIGHT, SPEED)
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
        motor_run(Motor.ALL, S_SPEED)
        sleep(10)
        token = False
        

def JustFollowRightWall() -> None :
    '''
    In : None
    
    Out : None
    
    Fonction : La fonction JustFollowRightWall ajuste la position du robot pour que le capteur 3 soit
    toujours sur un mur, et les trois autres en dehors de celle-ci.
    '''
        
    if line_sensor_data(2) <= 60 :
        print("1")
        motor_run(Motor.RIGHT, SPEED)
        motor_run(Motor.LEFT, 0)
        sleep(100)
        
    elif line_sensor_data(1) <= 60 :
        print("2")
        motor_run(Motor.RIGHT, SPEED)
        motor_run(Motor.LEFT, 0)
        sleep(100)
    
    elif line_sensor_data(0) <= 60 :
        print("3")
        motor_run(Motor.RIGHT, SPEED)
        motor_run(Motor.LEFT, S_SPEED)
        sleep(100)
        
    elif line_sensor_data(3) > 60  :
        print("out")
        motor_run(Motor.RIGHT, 0)
        motor_run(Motor.LEFT, SPEED)
        sleep(100)
        
    elif line_sensor_data(3) <= 60 :
        print("forward")
        motor_run(Motor.ALL, SPEED)
        sleep(100)
    

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
    '''
    In : - totGrid: int -> Nombre total de grilles sur lequel se fait la calibration du robot. (plus ce nombre
                           est grand, plus la mesure de la vitesse est precise, et le risque que le robot devie
                           aussi.) (5 semble etre un bon entre-deux)
                           
    Out : - gridSpeed: float -> Vitesse mesuree en grilles traversees par millisecondes, et sur laquelle on
                                calibre le deuxieme robot, afin de calquer sa vitesse sur celle du premier.
                                On s'assure ainsi que la vitesse ne depende ni du niveau de charge des piles
                                ni de la puissance(peu precise) des moteurs.
                                
    Principe : Le robot avance tant qu'il n'a pas detecter x (x=totGrid) grilles traversee. On prend une premiere
    mesure du temps au debut de la fonction, puis une seconde a la fin. On calcule ensutie gridSpeed en divisant
    le nombre total de grilles traversees par la difference des deux mesures initiale et finale du temps.
    Pour s'assurer que l'on ne compte que les lignes perpendiculaire au mouvement du robot, la liste localCount
    comprend 3 variables booléennes (= 1 si detectGrid == True). Pour compter une grille, il faut que les trois
    variables associees aux capteur valent 1 dans un lapse de temps de 150ms.
    '''
    
    global SPEED
    gridSpeed: float
    tick_final: int
    
    gridCrossed: int = 0
    tick_zero: int = utime.ticks_ms()
    crossingMargin: int = utime.ticks_ms()
    localCount: list[int] = [0,0,0,1] #[capt1, capt2, capt3, 
    
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
    
    tick_final = utime.ticks_ms()
    motor_stop()
    
    gridSpeed = totGrid / (tick_final - tick_zero)
    
    return gridSpeed


def setUpDirections() -> list[float] :
    '''
    In : None
    
    Out : - head_zero: list -> Liste des 4 points cardinaux du labyrinthe (haut, bas, gauche, droite) mesures.
    
    Fonction : On commence par calibrer la bousole avec la fonction microbit "calibrate()", puis on calcul
    l'angle de head_zero[i] en faisant la moyenne de dix mesure compass.heading(). La mesure du heading est
    envoyee depuis un microbit externe fixe au dessus du premier.
    '''
    i: int = 0
    last_id: int = 0
    recieved: str
    
    head_zero: list[float] = [0, 0, 0, 0]
    
    compass.clear_calibration()
    compass.calibrate()
    
    '''---------- head 0 ----------'''
    
    while button_b.was_pressed() != True :
        pass
    while i < 10 :
        received = radio.receive()
        if received != None and received[0:5] != str(last_id) :
            print(received)
            head_zero[0] += eval(received[6:])
            last_id = received[0:5]
            i += 1
    i = 0
    head_zero[0] = head_zero[0] / 10

    led_rgb(Color.BLUE, brightness=255)
    music.play("C6")
    led_rgb(Color.RED, brightness=255)
    
    '''---------- head 1 ----------'''
    
    while button_b.was_pressed() != True :
        pass
    while i < 10 :
        received = radio.receive()
        if received != None and received[0:5] != str(last_id) :
            print(received)
            head_zero[1] += eval(received[6:])
            last_id = received[0:5]
            i += 1
    i = 0
    head_zero[1] = head_zero[1] / 10
    
    led_rgb(Color.BLUE, brightness=255)
    music.play("C6")
    led_rgb(Color.RED, brightness=255)
    
    '''---------- head 2 ----------'''
    
    while button_b.was_pressed() != True :
        pass
    while i < 10 :
        received = radio.receive()
        if received != None and received[0:5] != str(last_id) :
            print(received)
            head_zero[2] += eval(received[6:])
            last_id = received[0:5]
            i += 1
    i = 0
    head_zero[2] = head_zero[2] / 10
    
    led_rgb(Color.BLUE, brightness=255)
    music.play("C6")
    led_rgb(Color.RED, brightness=255)
    
    '''---------- head 4 ----------'''
    
    while button_b.was_pressed() != True :
        pass
    while i < 10 :
        received = radio.receive()
        if received != None and received[0:5] != str(last_id) :
            print(received)
            head_zero[3] += eval(received[6:])
            last_id = received[0:5]
            i += 1
            
    head_zero[3] = head_zero[3] / 10
    
    led_rgb(Color.BLUE, brightness=255)
    music.play("C6")
    
    return head_zero


def getDirection(head_zero: float) -> (int, float) :
    direction: int
    intensity: float
    
    head_now: float = 0#= mq_heading()
    head_dist: list[float] = [0, 0, 0, 0]
    
    for i in range(0,40) :
        head_now += mq_heading()
        sleep(2)
    head_now = head_now / 40
    
    for i in range(0,4) :
        head_dist[i] = abs(head_zero[i] - head_now)

    direction = head_dist.index(min(head_dist))
    
    if head_now <= head_zero[direction] :
        intensity = head_now / head_zero[direction]
    elif head_now > head_zero[direction] :
        intensity = (head_now / head_zero[direction]) -2
    
    return direction, intensity


def changeDirection(head_zero: list[int], head: list[int,float], head_new: int) -> None :
    head_diff: int = head_new - head[0]
    if abs(head_diff) >= 3 :
        head_diff = (head_diff//abs(head_diff)) * -1
    
    print(head_diff)
    
    if head_diff >= 0 :
        motor_run(Motor.LEFT, SPEED)
        motor_run(Motor.RIGHT, -SPEED)
        sleep(720 * abs(head_diff))
        motor_stop()
        
    elif head_diff < 0 :
        motor_run(Motor.LEFT, -SPEED)
        motor_run(Motor.RIGHT, SPEED)
        sleep(720 * abs(head_diff))
        motor_stop()

            
def adjustDirection(direction: list[int, float], slp: int) -> None :
    '''
    In : - direction: list -> liste des 4 direction actuelle du robot et leurs positions relative
                              (en %) par rapport a la position head_zero (initiale) la plus proche.
                        
         - slp: int -> longueur du temps de pause durant lequel le robot tourne. Varie entre slp et
                       2*slp entre le premier et le deuxieme ajustement.
         
    Out : None
    
    Fonction : Ajuste la direction afin de l'alligner a la position head_zero (mesuree durant la
    calibration du robot) la plus proche, pour s'assurer qu'il soit parallele a la grille afin de
    faciliter le comptage des cases. L'ajustement s'effectue en deux tours: 1er ajustement en gros
    et le second en precision.
    '''
    for i in range(1,3) :
        for j in range(0,8) : 
            if direction[1] < 0 :
                motor_run(Motor.LEFT, SPEED)
                motor_run(Motor.RIGHT, -SPEED)
                print("turn LEFT")
                sleep((1/i)*slp)
            
            elif direction[1] > 0 :
                motor_run(Motor.LEFT, -SPEED)
                motor_run(Motor.RIGHT, SPEED)
                print("turn RIGHT")
                sleep((1/i)*slp)
            
            motor_stop()
        
        sleep(200)

        
def main() -> None :
    grid: int
    realSpeed: float
    head_zero: list[float] #front, right, back, left
    direction: list[int,float] #heading, intensity
    
    option: int = 0 #case1: resolve maze, case:2 follow wall
    start: bool = False
    initialization: list[bool] = [False, False]
    forward: bool = False
    
    print("prog running...")
    
    '''============= Initialization ============='''
    
    radio.on()
        
    motor_stop()
    led_rgb(Color.GREEN, brightness=255)
    music.play(TUNE_START)
    sleep(2000)
    led_rgb(Color.RED, brightness=255)
    music.play(TUNE_NEGATIVE)    
    
    while initialization != [True, True]:
        led_rgb(Color.RED, brightness=255)
    
        if button_a.was_pressed() :
            '''----- setting up the speed -----'''
            realSpeed = setUpSpeed(5)
            grid = 0
            
            print("robot speed initialized")
            
            initialization[0] = True
            led_rgb(Color.GREEN, brightness=255)
            music.play(TUNE_POSITIVE)
            
            
        if button_b.was_pressed() :
            '''----- setting up the compass -----'''
            head_zero = setUpDirections()
            
            print("robot is initially heading: ", head_zero)
            print("robot compass initialized.")
            
            initialization[1] = True
            led_rgb(Color.GREEN, brightness=255)
            music.play(TUNE_POSITIVE)
    
    print(head_zero)
    
    '''============= Choose Option ============='''
    
    tick = utime.ticks_ms()
    
    while start != True :
        if utime.ticks_ms() - tick > 6000 :
            led_rgb(Color.RED, brightness=255)
            music.play(TUNE_NEGATIVE)
            led_rgb(Color.GREEN, brightness=255)
            tick = utime.ticks_ms()
            
        if button_a.was_pressed() :
            option = 1
            break
        
        elif button_b.was_pressed() :
            option = 2
            break
        
    led_rgb(Color.GREEN, brightness=255)
    music.play(TUNE_POSITIVE)
    music.play(TUNE_POSITIVE)
    sleep(600)
    
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
    
    
    '''============= Main Loops ============='''
    
    print("robot num 1 starts operating...")
    
    led_rgb(Color.WHITE, brightness=255)
    music.play("C6")
    sleep(1000)
    
    if option == 1 :
        while True : #for testing
            if button_b.was_pressed() :#might need to put it directly inside the function.
                
                for i in range(0,10) :
                    direction = getDirection(head_zero)
                    print(direction)
                    adjustDirection(direction, 80)
                    sleep(100)
                sleep(200)
                for i in range(0,20) :
                    direction = getDirection(head_zero)
                    print(direction)
                    adjustDirection(direction, 25)
                    sleep(50)
                    
            if button_a.was_pressed() :
                sleep(500)
                direction = getDirection(head_zero)
                changeDirection(head_zero, direction, (direction[0] + 2)%4)
                
            sleep(100)
    
    elif option == 2 :
        while True :
            JustFollowRightLine()
            sleep(10)
            
    elif option == 0 :
        return -1
            
            
    motor_stop()
    

if __name__ == "__main__" :
    #main()
    
    motor_stop()
    led_rgb(Color.WHITE, brightness=255)
    while True :
        JustFollowRightWall()
        print(line_sensor_data(3))
        sleep(5)
        
        
    
