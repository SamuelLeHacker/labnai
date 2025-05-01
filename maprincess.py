'''
Version: 2.0.1
@see https://github.com/DFRobot/pxt-DFRobot_MaqueenPlus_v20/blob/master/maqueenPlusV2.ts
'''
from micropython import const
from microbit import i2c,display,Image,pin13,pin14,pin15,accelerometer,compass
from machine import time_pulse_us
from neopixel import NeoPixel
from time import sleep_ms
from math import sqrt,asin,cos,sin,atan2,pi
class Motor:
 LEFT=0
 RIGHT=1
 ALL=2
class Direction:
 FORWARD=0
 BACKWARD=1
class Led:
 LEFT=0
 RIGHT=1
 ALL=2
class LineSensor:
 L1=0
 M=1
 R1=2
 L2=3
 R2=4
class Color:
 RED=0xFF0000
 ORANGE=0xFFA500
 YELLOW=0xFFFF00
 GREEN=0x51FF00
 BLUE=0x0000FF
 INDIGO=0x4B0082
 VIOLET=0x8A2BE2
 PURPLE=0xFF00FF
 WHITE=0xFFFFFF
 BLACK=0x000000
class ColorLED:
 L1=0
 L2=1
 R2=2
 R1=3
 ALL=4
I2C_ADDR=const(0x10)
ADC0_REGISTER=const(0X1E)
ADC1_REGISTER=const(0X20)
ADC2_REGISTER=const(0X22)
ADC3_REGISTER=const(0X24)
ADC4_REGISTER=const(0X26)
LEFT_LED_REGISTER=const(0X0B)
RIGHT_LED_REGISTER=const(0X0C)
LEFT_MOTOR_REGISTER=const(0X00)
RIGHT_MOTOR_REGISTER=const(0X02)
LINE_STATE_REGISTER=const(0X1D)
VERSION_CNT_REGISTER=const(0X32)
VERSION_DATA_REGISTER=const(0X33)
_ULTRASONIC_PULSE_LENGTH_US=const(500*58)
_neo_pixel=NeoPixel(pin15,4)
_brightness=0xff
_heading_window_size=1
_heading_buffer=[0.0]
_heading_buffer_index=0
_motor_calibration=[[],[]]
def I2CInit():
 version_v=0
 i2c.write(I2C_ADDR,bytearray([VERSION_CNT_REGISTER]))
 version_v=i2c.read(I2C_ADDR,1)
 while not version_v:
  display.show(Image('90009:09090:00900:09090:90009'))
  sleep_ms(500)
  display.clear()
  i2c.write(I2C_ADDR,bytearray([VERSION_CNT_REGISTER]))
  version_v=i2c.read(I2C_ADDR,1)
 display.show(Image('00000:00009:00090:90900:09000'))
 sleep_ms(500)
 display.clear()
def motor_calibration(motor:int,speed_factors:list):
 if motor>1:
  print('No motor index',motor,'found. Calibration is ignored')
  return
 _motor_calibration[motor]=sorted(speed_factors,key=lambda x:x[0])
def motor_get_calibration(motor:int):
 return[s for s in _motor_calibration[motor]]
def _get_speed(motor:int,speed:int):
 num_calibs=len(_motor_calibration[motor])
 if motor>1 or num_calibs==0:
  return speed
 elif num_calibs==1:
  return int(_motor_calibration[motor][0][1]*speed)
 elif num_calibs==2:
  calibs=_motor_calibration[motor]
  x1=calibs[0][0]
  y1=calibs[0][1]
  x2=calibs[1][0]
  y2=calibs[1][1]
  m=(y2-y1)/(x2-x1)
  factor=y1+(speed-x1)*m
  return int(factor*speed)
 else:
  calibs=_motor_calibration[motor]
  bigger=[x for x in calibs if x[0]>speed]
  if len(bigger)>0:
   cal2=bigger[0]
  else:
   cal2=calibs[-1]
  idx_cal2=calibs.index(cal2)
  if idx_cal2>0:
   cal1=calibs[idx_cal2-1]
  else:
   cal1=cal2
   cal2=calibs[idx_cal2+1]
  x1=cal1[0]
  y1=cal1[1]
  x2=cal2[0]
  y2=cal2[1]
  m=(y2-y1)/(x2-x1)
  factor=y1+(speed-x1)*m
  return int(factor*speed)
def motor_run(motor:int,speed:int,dir:int=Direction.FORWARD):
 if speed<0:
  speed=-speed
  dir=Direction.FORWARD if dir==Direction.BACKWARD else Direction.BACKWARD
 if motor==Motor.LEFT:
  i2c.write(I2C_ADDR,bytearray([LEFT_MOTOR_REGISTER,dir,_get_speed(motor,speed)]))
 elif motor==Motor.RIGHT:
  i2c.write(I2C_ADDR,bytearray([RIGHT_MOTOR_REGISTER,dir,_get_speed(motor,speed)]))
 else:
  i2c.write(I2C_ADDR,bytearray([LEFT_MOTOR_REGISTER,dir,_get_speed(Motor.LEFT,speed),dir,_get_speed(Motor.RIGHT,speed)]))
def motor_stop(motor:int=Motor.ALL):
 motor_run(motor,0,0)
def led_red(on:bool,led:int=Led.ALL):
 if led==Led.LEFT:
  i2c.write(I2C_ADDR,bytearray([LEFT_LED_REGISTER,1 if on else 0]))
 elif led==Led.RIGHT:
  i2c.write(I2C_ADDR,bytearray([RIGHT_LED_REGISTER,1 if on else 0]))
 else:
  switch=1 if on else 0
  i2c.write(I2C_ADDR,bytearray([LEFT_LED_REGISTER,switch,switch]))
def line_sensor(sensor:int):
 i2c.write(I2C_ADDR,bytearray([LINE_STATE_REGISTER]))
 data=i2c.read(I2C_ADDR,1)
 if sensor==LineSensor.L2:
  return 1 if(data[0]&0x10)==0x10 else 0
 elif sensor==LineSensor.L1:
  return 1 if(data[0]&0x08)==0x08 else 0
 elif sensor==LineSensor.M:
  return 1 if(data[0]&0x04)==0x04 else 0
 elif sensor==LineSensor.R1:
  return 1 if(data[0]&0x02)==0x02 else 0
 elif sensor==LineSensor.R2:
  return 1 if(data[0]&0x01)==0x01 else 0
def line_sensor_all():
 i2c.write(I2C_ADDR,bytearray([LINE_STATE_REGISTER]))
 data=i2c.read(I2C_ADDR,1)
 return(1 if(data[0]&0x10)==0x10 else 0,1 if(data[0]&0x08)==0x08 else 0,1 if(data[0]&0x04)==0x04 else 0,1 if(data[0]&0x02)==0x02 else 0,1 if(data[0]&0x01)==0x01 else 0)
def line_sensor_data(sensor:int)->int:
 i2c.write(I2C_ADDR,bytearray([LINE_STATE_REGISTER]))
 if sensor==LineSensor.L2:
  i2c.write(I2C_ADDR,bytearray([ADC0_REGISTER]))
  buffer=i2c.read(I2C_ADDR,2)
  return buffer[1]<<8|buffer[0]
 if sensor==LineSensor.L1:
  i2c.write(I2C_ADDR,bytearray([ADC1_REGISTER]))
  buffer=i2c.read(I2C_ADDR,2)
  return buffer[1]<<8|buffer[0]
 elif sensor==LineSensor.M:
  i2c.write(I2C_ADDR,bytearray([ADC2_REGISTER]))
  buffer=i2c.read(I2C_ADDR,2)
  return buffer[1]<<8|buffer[0]
 elif sensor==LineSensor.R1:
  i2c.write(I2C_ADDR,bytearray([ADC3_REGISTER]))
  buffer=i2c.read(I2C_ADDR,2)
  return buffer[1]<<8|buffer[0]
 elif sensor==LineSensor.R2:
  i2c.write(I2C_ADDR,bytearray([ADC4_REGISTER]))
  buffer=i2c.read(I2C_ADDR,2)
  return buffer[1]<<8|buffer[0]
 return 0
def line_sensor_data_all():
 return(line_sensor_data(LineSensor.L2),line_sensor_data(LineSensor.L1),line_sensor_data(LineSensor.M),line_sensor_data(LineSensor.R1),line_sensor_data(LineSensor.R2))
def ultrasonic(trig=pin13,echo=pin14):
 trig.write_digital(1)
 sleep_ms(1)
 trig.write_digital(0)
 if echo.read_digital()==0:
  trig.write_digital(0)
  trig.write_digital(1)
  sleep_ms(20)
  trig.write_digital(0)
  data=time_pulse_us(echo,1,_ULTRASONIC_PULSE_LENGTH_US)
 else:
  trig.write_digital(1)
  trig.write_digital(0)
  sleep_ms(20)
  trig.write_digital(0)
  data=time_pulse_us(echo,1,_ULTRASONIC_PULSE_LENGTH_US)
 data=data/59
 if data<=0:
  return 0
 elif data>=500:
  return 500
 return round(data)
def version():
 i2c.write(I2C_ADDR,bytearray([VERSION_CNT_REGISTER]))
 bytes_to_read=int(i2c.read(I2C_ADDR,1)[0])
 i2c.write(I2C_ADDR,bytearray([VERSION_DATA_REGISTER]))
 version=i2c.read(I2C_ADDR,bytes_to_read)
 return version.decode('utf-8')
def rgb(r:int,g:int,b:int):
 return(r<<16)|(g<<8)|b
def hsl(h:int,s:int,l:int):
 _h=h/360.0
 _l=l/100.0
 _s=s/100.0
 if _s==0.0:
  return rgb(int(255*_l),int(255*_l),int(255*_l))
 if l<=0.5:
  m2=_l*(1+_s)
 else:
  m2=_l+_s-(_l*_s)
 m1=2.0*_l-m2
 return rgb(int(255*_v(m1,m2,_h+1/3)),int(255*_v(m1,m2,_h)),int(255*_v(m1,m2,_h-1/3)))
def _v(m1,m2,hue):
 hue=hue%1.0
 if hue<1/6:
  return m1+(m2-m1)*hue*6.0
 if hue<0.5:
  return m2
 if hue<2/3:
  return m1+(m2-m1)*(2/3-hue)*6.0
 return m1
def led_rgb(rgb:int,led:int=ColorLED.ALL,brightness:int=-1):
 if _brightness<2 and brightness<0:
  led_brightness(255)
 if brightness<0:
  brightness=_brightness
 r=(rgb>>16)*(brightness/255)
 g=((rgb>>8)&0xFF)*(brightness/255)
 b=((rgb)&0xFF)*(brightness/255)
 if led==ColorLED.ALL:
  for i in range(4):
   _neo_pixel[i]=(int(r),int(g),int(b))
 elif led>=0 and led<ColorLED.ALL:
  _neo_pixel[led]=(int(r),int(g),int(b))
 _neo_pixel.show()
def led_brightness(brightness:int):
 global _brightness
 if brightness<0:
  brightness=0
 elif brightness>255:
  brightness=255
 _brightness=brightness
def led_rgb_off(led:int=ColorLED.ALL):
 if led<0 or led>ColorLED.ALL:
  led=ColorLED.ALL
 led_rgb(0,led)
def mq_heading():
 acc_flat=accelerometer.get_values()
 acc_raw=(acc_flat[0],acc_flat[2],-acc_flat[1])
 mag_raw=(compass.get_x(),compass.get_z(),-compass.get_y())
 acc_norm=sqrt(acc_raw[0]*acc_raw[0]+acc_raw[1]*acc_raw[1]+acc_raw[2]*acc_raw[2])
 try:
  acc_x_norm=acc_raw[0]/acc_norm
  acc_y_norm=acc_raw[1]/acc_norm
  pitch=asin(acc_x_norm)
  roll=-asin(acc_y_norm/cos(pitch))
  mag_x_comp=mag_raw[0]*cos(pitch)+mag_raw[2]*sin(pitch)
  mag_y_comp=mag_raw[0]*sin(roll)*sin(pitch)+mag_raw[1]*cos(roll)-mag_raw[2]*sin(roll)*cos(pitch)
  heading=180*atan2(mag_y_comp,mag_x_comp)/pi
  if heading<0:
   heading+=360
  return heading
 except:
  return 0
def heading_set_window_size(n:int=1):
 global _heading_buffer_index
 if n<1:
  _heading_window_size=1
 else:
  _heading_window_size=n
 _heading_buffer.clear()
 for i in range(_heading_window_size):
  _heading_buffer.append(0)
 _heading_buffer_index=0
def _heading_append(heading:float):
 global _heading_buffer_index
 _heading_buffer[_heading_buffer_index]=heading
 _heading_buffer_index=(_heading_buffer_index+1)%_heading_window_size
def _heading_mean():
 if _heading_window_size==1:
  return _heading_buffer[0]
 return sum(_heading_buffer)/_heading_window_size
def heading_diff(heading0:float,apply_window:bool=True):
 heading=mq_heading()
 if apply_window:
  _heading_append(heading)
  current=_heading_mean()
 else:
  current=heading
 angle=180-abs(abs(heading0-current)-180)
 if(heading0+angle)%360==current:
  return-angle
 else:
  return angle
# Created by pyminifier (https://github.com/dzhuang/pyminifier3)
