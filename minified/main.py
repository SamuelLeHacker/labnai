_C='C6'
_B=False
_A=True
from microbit import*
from maprincess import*
import utime,music,radio
SUPER_SPEED=90
SPEED=85
S_SPEED=79
SS_SPEED=70
TUNE_START=['C6:1','E','G']
TUNE_POSITIVE=['F5:1','G']
TUNE_NEGATIVE=['E4:1','C5','E3:1','C3:']
is_stucked=0
is_super_stucked=0
def Move():
	token=_A;stoped=_B;global is_stucked
	if line_sensor_data(0)<=60 and line_sensor_data(2)<=60 and token==_A:token=_B;stoped=_A;motor_stop();sleep(10)
	if is_stucked>6:is_stucked=0;print('STUUUUUUUCK');motor_run(Motor.RIGHT,-35);motor_run(Motor.LEFT,20);sleep(800)
	if line_sensor_data(0)>60 and line_sensor_data(2)<=60 and token==_A:motor_run(Motor.LEFT,SPEED);motor_run(Motor.RIGHT,0);sleep(10);token=_B
	if line_sensor_data(2)>60 and line_sensor_data(0)<=60 and token==_A:motor_run(Motor.LEFT,0);motor_run(Motor.RIGHT,SPEED);sleep(10);token=_B
	if line_sensor_data(3)>60 and line_sensor_data(4)<=60 and token==_A:motor_run(Motor.LEFT,SPEED);motor_run(Motor.RIGHT,S_SPEED);sleep(10);token=_B
	if line_sensor_data(3)<=60 and line_sensor_data(4)>60 and token==_A:motor_run(Motor.RIGHT,SPEED);motor_run(Motor.LEFT,S_SPEED);sleep(10);token=_B
	if line_sensor_data(0)>60 and line_sensor_data(2)>60 and token==_A:motor_run(Motor.ALL,S_SPEED);sleep(10);token=_B
def JustFollowRightWall():
	if line_sensor_data(2)<=220:motor_run(Motor.LEFT,-SPEED);motor_run(Motor.RIGHT,S_SPEED);sleep(1)
	elif line_sensor_data(1)<=220:motor_run(Motor.LEFT,-50);motor_run(Motor.RIGHT,SPEED);sleep(1)
	elif line_sensor_data(0)<=220:motor_run(Motor.LEFT,0);motor_run(Motor.RIGHT,SPEED);sleep(1)
	elif line_sensor_data(3)>220:motor_run(Motor.RIGHT,-SS_SPEED);motor_run(Motor.LEFT,SPEED);sleep(1)
	elif line_sensor_data(3)<=220:motor_run(Motor.RIGHT,SUPER_SPEED-35);motor_run(Motor.LEFT,SUPER_SPEED);sleep(1)
def detectGrid(sensor,slp):
	if 120<=line_sensor_data(sensor)<=236:sleep(slp);return 1
	else:return 0
def countGrid(crossedGrid):
	order:0
	if detectGrid(1):
		sleep(20)
		if detectGrid(1):0
def setUpSpeed(totGrid):
	global SPEED;gridSpeed:0;tick_final:0;gridCrossed=0;tick_zero=utime.ticks_ms();crossingMargin=utime.ticks_ms();localCount=[0,0,0,1]
	while gridCrossed<totGrid:
		if utime.ticks_ms()-crossingMargin>150:crossingMargin=utime.ticks_ms();localCount=[0,0,0,1];print('reset')
		localCount[0]=detectGrid(0,0);localCount[1]=detectGrid(0,0);localCount[2]=detectGrid(0,0)
		if localCount==[1,1,1,1]:localCount[3]=0;gridCrossed+=1;print('grid num:',gridCrossed);sleep(60)
		motor_run(Motor.ALL,SPEED)
	tick_final=utime.ticks_ms();motor_stop();gridSpeed=totGrid/(tick_final-tick_zero);return gridSpeed
def setUpDirections():
	A=None;i=0;last_id=0;recieved:0;head_zero=[0,0,0,0];compass.clear_calibration();compass.calibrate()
	while button_b.was_pressed()!=_A:0
	while i<10:
		received=radio.receive()
		if received!=A and received[0:5]!=str(last_id):print(received);head_zero[0]+=eval(received[6:]);last_id=received[0:5];i+=1
	i=0;head_zero[0]=head_zero[0]/10;led_rgb(Color.BLUE,brightness=255);music.play(_C);led_rgb(Color.RED,brightness=255)
	while button_b.was_pressed()!=_A:0
	while i<10:
		received=radio.receive()
		if received!=A and received[0:5]!=str(last_id):print(received);head_zero[1]+=eval(received[6:]);last_id=received[0:5];i+=1
	i=0;head_zero[1]=head_zero[1]/10;led_rgb(Color.BLUE,brightness=255);music.play(_C);led_rgb(Color.RED,brightness=255)
	while button_b.was_pressed()!=_A:0
	while i<10:
		received=radio.receive()
		if received!=A and received[0:5]!=str(last_id):print(received);head_zero[2]+=eval(received[6:]);last_id=received[0:5];i+=1
	i=0;head_zero[2]=head_zero[2]/10;led_rgb(Color.BLUE,brightness=255);music.play(_C);led_rgb(Color.RED,brightness=255)
	while button_b.was_pressed()!=_A:0
	while i<10:
		received=radio.receive()
		if received!=A and received[0:5]!=str(last_id):print(received);head_zero[3]+=eval(received[6:]);last_id=received[0:5];i+=1
	head_zero[3]=head_zero[3]/10;led_rgb(Color.BLUE,brightness=255);music.play(_C);return head_zero
def getDirection(head_zero):
	direction:0;intensity:0;head_now=0;head_dist=[0,0,0,0]
	for i in range(0,40):head_now+=mq_heading();sleep(2)
	head_now=head_now/40
	for i in range(0,4):head_dist[i]=abs(head_zero[i]-head_now)
	direction=head_dist.index(min(head_dist))
	if head_now<=head_zero[direction]:intensity=head_now/head_zero[direction]
	elif head_now>head_zero[direction]:intensity=head_now/head_zero[direction]-2
	return direction,intensity
def changeDirection(head_zero,head,head_new):
	head_diff=head_new-head[0]
	if abs(head_diff)>=3:head_diff=head_diff//abs(head_diff)*-1
	print(head_diff)
	if head_diff>=0:motor_run(Motor.LEFT,SPEED);motor_run(Motor.RIGHT,-SPEED);sleep(720*abs(head_diff));motor_stop()
	elif head_diff<0:motor_run(Motor.LEFT,-SPEED);motor_run(Motor.RIGHT,SPEED);sleep(720*abs(head_diff));motor_stop()
def adjustDirection(direction,slp):
	for i in range(1,3):
		for j in range(0,8):
			if direction[1]<0:motor_run(Motor.LEFT,SPEED);motor_run(Motor.RIGHT,-SPEED);print('turn LEFT');sleep(1/i*slp)
			elif direction[1]>0:motor_run(Motor.LEFT,-SPEED);motor_run(Motor.RIGHT,SPEED);print('turn RIGHT');sleep(1/i*slp)
			motor_stop()
		sleep(200)
def main():
	A='C';grid:0;realSpeed:0;head_zero:0;direction:0;option=0;start=_B;initialization=[_B,_B];forward=_B;print('prog running...');radio.on();motor_stop();led_rgb(Color.GREEN,brightness=255);music.play(TUNE_START);sleep(2000);led_rgb(Color.RED,brightness=255);music.play(TUNE_NEGATIVE)
	while initialization!=[_A,_A]:
		led_rgb(Color.RED,brightness=255)
		if button_a.was_pressed():realSpeed=setUpSpeed(5);grid=0;print('robot speed initialized');initialization[0]=_A;led_rgb(Color.GREEN,brightness=255);music.play(TUNE_POSITIVE)
		if button_b.was_pressed():head_zero=setUpDirections();print('robot is initially heading: ',head_zero);print('robot compass initialized.');initialization[1]=_A;led_rgb(Color.GREEN,brightness=255);music.play(TUNE_POSITIVE)
	print(head_zero);tick=utime.ticks_ms()
	while start!=_A:
		if utime.ticks_ms()-tick>6000:led_rgb(Color.RED,brightness=255);music.play(TUNE_NEGATIVE);led_rgb(Color.GREEN,brightness=255);tick=utime.ticks_ms()
		if button_a.was_pressed():option=1;break
		elif button_b.was_pressed():option=2;break
	led_rgb(Color.GREEN,brightness=255);music.play(TUNE_POSITIVE);music.play(TUNE_POSITIVE);sleep(600);led_rgb(Color.RED,brightness=255);music.play(A);sleep(400);led_rgb_off();sleep(100);led_rgb(Color.ORANGE,brightness=255);music.play(A);sleep(400);led_rgb_off();sleep(100);led_rgb(Color.GREEN,brightness=255);music.play(A);sleep(400);led_rgb_off();sleep(100);print('robot num 1 starts operating...');led_rgb(Color.WHITE,brightness=255);music.play(_C);sleep(1000)
	if option==1:
		while _A:
			if button_b.was_pressed():
				for i in range(0,10):direction=getDirection(head_zero);print(direction);adjustDirection(direction,80);sleep(100)
				sleep(200)
				for i in range(0,20):direction=getDirection(head_zero);print(direction);adjustDirection(direction,25);sleep(50)
			if button_a.was_pressed():sleep(500);direction=getDirection(head_zero);changeDirection(head_zero,direction,(direction[0]+2)%4)
			sleep(100)
	elif option==2:
		while _A:JustFollowRightLine();sleep(10)
	elif option==0:return-1
	motor_stop()
if __name__=='__main__':
	motor_stop();led_rgb(Color.WHITE,brightness=255)
	while _A:JustFollowRightWall()