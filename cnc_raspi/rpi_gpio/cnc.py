"""
TODO:
1) sum time by onece
2) averenge END's for best init
"""
import rpi_gpio.config
from time import sleep, time
import cv2 as cv
import numpy as np
import sys
#sys.path.append('..')
#import photo_test.find_work_area
import RPi.GPIO as GPIO

config = rpi_gpio.config
FRW =  1
BCK = -1
coor_x     = 0
coor_y     = 1
coor_z     = 2
coor_freza = 3
coordinates = [0, 0, 0, 0]

def x_step(direction, speed_x):
    d = 1 if direction == FRW else 0
    GPIO.output(config.x_St, 0)
    GPIO.output(config.x_Dr, d)
    sleep((round(round((pow(speed_x * 800, -1) * pow(10, 5))) / 2)) * 10**-6)
    GPIO.output(config.x_St, 1)
    GPIO.output(config.x_Dr, d)
    sleep((round(round((pow(speed_x * 800, -1) * pow(10, 5))) / 2)) * 10**-6) 
    coordinates[coor_x] += direction * 125

def y_step(direction, speed_y):
    d = 1 if direction == FRW else 0
    GPIO.output(config.y_St, 0)
    GPIO.output(config.y_Dr, d)
    sleep((round(round((pow(speed_y * 800, -1) * pow(10, 5))) / 2)) * 10**-6)
    GPIO.output(config.y_St, 1)
    GPIO.output(config.y_Dr, d)
    sleep((round(round((pow(speed_y * 800, -1) * pow(10, 5))) / 2)) * 10**-6) 
    coordinates[coor_y] += direction * 125

def z_step(direction, speed_z):
    d = 1 if direction == FRW else 0
    GPIO.output(config.z_St, 0)
    GPIO.output(config.z_Dr, d)
    sleep((round(round((pow(speed_z * 800, -1) * pow(10, 5))) / 2)) * 10**-6)
    GPIO.output(config.z_St, 1)
    GPIO.output(config.z_Dr, d)
    sleep((round(round((pow(speed_z* 800, -1) * pow(10, 5))) / 2)) * 10**-6) 
    coordinates[coor_z] += direction * 125

def x_go(mm, speed_x = 1):
    steps = mm * config.X_STEPS_MM
    GPIO.output(config.x_En, 0)
    d = FRW if steps > 0 else BCK
    for i in range(abs(steps)):
        x_step(d, speed_x)
    GPIO.output(config.x_En, 1)
    
def y_go(mm, speed_y = 1):
    steps = mm * config.Y_STEPS_MM
    GPIO.output(config.y_En, 0)
    d = FRW if steps > 0 else BCK
    for i in range(abs(steps)):
        y_step(d, speed_y)
    GPIO.output(config.y_En, 1)
    
def z_go(mm, speed_z = 1):
    steps = mm * config.Z_STEPS_MM
    GPIO.output(config.z_En, 0)
    d = FRW if steps > 0 else BCK
    for i in range(abs(steps)):
        z_step(d, speed_z)
    GPIO.output(config.z_En, 1)

def init_axis_x():
    count = 0
    while((GPIO.input(config.X_END)) and (count < 270)):
        x_go(-100, 1)
        count += 1
    x_go(500, 1)
    count = 0
    while((GPIO.input(config.X_END)) and (count < 500)):
        x_go(-1, 0.05)
        count += 1
    while(not (GPIO.input(config.X_END))):
        x_go(1, 0.1)
    coordinates[coor_x] = 0

def init_axis_y():
    count = 0
    while((GPIO.input(config.Y_END)) and (count < 270)):
        y_go(-100, 1)
        count += 1
    y_go(500, 1)
    count = 0
    while((GPIO.input(config.Y_END)) and (count < 500)):
        y_go(-1, 0.05)
        count += 1
    while(not (GPIO.input(config.Y_END))):
        y_go(1, 0.1)
    coordinates[coor_y] = 0

def init_axis_z():
    count = 0
    while((GPIO.input(config.Z_END)) and (count < 270)):
        z_go(-100, 1)
        count += 1
    z_go(500, 1)
    count = 0
    while((GPIO.input(config.Z_END)) and (count < 500)):
        z_go(-1, 0.05)
        count += 1
    while(not (GPIO.input(config.Z_END))):
        z_go(1, 0.1)
    coordinates[coor_z] = 0

def cnc_init():
    init_axis_z()
    init_axis_x()
    init_axis_y()
    
def zero_freza():
    count = 0
    while((GPIO.input(config.Z_END)) and (count < 270)):
        z_go(-100, 1)
        count += 1
    z_go(500, 1)
    count = 0
    while((GPIO.input(config.Z_END)) and (count < 500)):
        z_go(-1, 0.05)
        count += 1
    while(not (GPIO.input(config.Z_END))):
        z_go(1, 0.1)
    coordinates[coor_z] = 0
    f = 100
    while((int(round(f / 100))) and (coordinates[coor_z] < 8000000)):
        z_go(1, 0.25)
        f = 0
        for i in range(100):
            f += GPIO.input(config.F_END) 
    coordinates[coor_freza] = coordinates[coor_z]
    
    count = 0
    while((GPIO.input(config.Z_END)) and (count < 270)):
        z_go(-100, 1)
        count += 1
    z_go(500, 1)
    count = 0
    while((GPIO.input(config.Z_END)) and (count < 500)):
        z_go(-1, 0.05)
        count += 1
    while(not (GPIO.input(config.Z_END))):
        z_go(1, 0.1)
    coordinates[coor_z] = 0

def get_frames(id):
    cam = cv.VideoCapture(id)
    assert cam.isOpened()
    cam.set(3, 1920)
    cam.set(4, 1080)
    out = np.zeros((int(cam.get(4)*2),int(cam.get(3)*2), 3))
    for i in range(10):
        out[::2 ,  ::2] = cam.read()[1]
        out[::2 , 1::2] = cam.read()[1]
        out[1::2,  ::2] = cam.read()[1]
        out[1::2, 1::2] = cam.read()[1]
    return out

def camera_screen(coordinates):
    ret, frame = cv.VideoCapture(0).read()
    screen_name = f'/tmp/cnc/{str(coordinates)}.jpeg'
    cv.imwrite(screen_name, frame)
    print("Screen saved in " + screen_name)

def go_to_coor(x, y):
    dx = x - int(coordinates[coor_x] / 1000)
    dy = y - int(coordinates[coor_y] / 1000)
    x_go(dx, 1)
    y_go(dy, 1)

def run_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(True)
    GPIO.setup([config.X_END, config.Y_END, config.Z_END, config.F_END], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.setup([config.x_St, config.x_Dr, config.x_En], GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(config.x_En, 1)
    
    GPIO.setup([config.y_St, config.y_Dr, config.y_En], GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(config.y_En, 1)
    
    GPIO.setup([config.z_St, config.z_Dr, config.z_En], GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(config.z_En, 1)

def stop_gpio():
    GPIO.cleanup()

if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(True)
    GPIO.setup([config.X_END, config.Y_END, config.Z_END, config.F_END], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.setup([config.x_St, config.x_Dr, config.x_En], GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(config.x_En, 1)
    
    GPIO.setup([config.y_St, config.y_Dr, config.y_En], GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(config.y_En, 1)
    
    GPIO.setup([config.z_St, config.z_Dr, config.z_En], GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(config.z_En, 1)
    
    #GPIO.setup(config.Freza, GPIO.OUT, initial=GPIO.LOW)
    #GPIO.output(config.Freza, 1)
    #sleep(5)
    #GPIO.output(config.Freza, 0)
    #cnc_init()
    '''
    x_go(1000, 3)
    y_go(1000, 3)
    DUTY_CYCLE = 42
    FREQUENCY = 100
    
    GPIO.setup(config.Freza, GPIO.OUT)
    freza = GPIO.PWM(config.Freza, FREQUENCY)
    freza.start(20)
    sleep(1)
    freza.stop()
    '''
    #zero cam one - 32.64 ; 0 ???31.93???
    cnc_init()
    
    x_go(1707)
    y_go(13012)
    z_go(1500)
    print(coordinates)
    #x_go(0, 1)
    #y_go(2672, 1)
    #z_go(1500, 1)
    '''
    x_go(1909, 1)#(0, 1)
    y_go(3661, 1)#(2672, 1)
    z_go(1500, 1)#(1500, 1)
    #go_to_coor(0, 2635, 1500)
    img = get_frames(2)
    t = str(int(time())%100000)
    cv.imwrite(f'/tmp/out_{2}_{t}.jpeg', img)
    print(f"[INFO:] img write in /tmp/out_{2}_{t}.jpeg")
    img = photo_test.find_work_area.rotate(f'/tmp/out_{2}_{t}.jpeg', angle = 1.8)
    #img = cv.imread('/tmp/out_2_76735_.jpeg')
    dx, dy, img = photo_test.find_work_area.find_corner_by_cam_one(img)
    #plt.imshow(img)
    #plt.show()
    dx = int(round(dx, 2) * 100)
    dy = int(round(dy, 2) * 100)
    print(dx, dy)
    count = 0
    while ((count > 150) or ((dx**2 + dy**2)**0.5 > 10)):
        x_go(-dx, 1)
        y_go(dy, 1)
        img = get_frames(2)
        t = str(int(time())%100000)
        cv.imwrite(f'/tmp/out_{2}_{t}.jpeg', img)
        print(f"[INFO:] img write in /tmp/out_{2}_{t}.jpeg")
        img = photo_test.find_work_area.rotate(f'/tmp/out_{2}_{t}.jpeg', angle = 1.8)
        #img = cv.imread('/tmp/out_2_76735_.jpeg')
        dx, dy, img = photo_test.find_work_area.find_corner_by_cam_one(img)
        #plt.imshow(img)
        #plt.show()
        dx = int(round(dx, 2) * 100)
        dy = int(round(dy, 2) * 100)
        print(dx, dy)
        count += 1
    print("READY")
    print(count)
    print(dx, dy)
    print(f"[INFO:] img write in /tmp/out_{2}_{t}.jpeg")
    print(coordinates)
   # x_go(20688, 1)
   # y_go(5072, 1)
    #z_go(1500, 1)
    
    for i in range(9):
        cnc_init()
        go_to_coor(0, 16000) #zero cam two
    #go_to_coor(0, 2635)#, 1500) #zero cam one 
        print(coordinates)
        img = get_frames(0)
        cv.imwrite(f'/tmp/out_{0}_{str(int(time())%1000)}.jpeg', img)
    '''
    GPIO.cleanup()


