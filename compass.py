from microbit import *
import radio

radio.on()
id: int = 10000
heading: int

while True :
    heading = compass.heading()
    tram = str(id) + "." + str(heading)
    radio.send(tram)
    print(tram)
    id += 1
    sleep(30)
    
    print(tram[0:5])
    print(tram[6:])