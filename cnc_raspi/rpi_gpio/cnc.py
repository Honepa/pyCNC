"""
TODO:
1) sum time by onece
2) averenge END's for best init
"""
import RPi.GPIO as GPIO
import config
from time import sleep
import cv2 as cv

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

def x_go(mm, speed_x):
    steps = mm * config.X_STEPS_MM
    GPIO.output(config.x_En, 0)
    d = FRW if steps > 0 else BCK
    for i in range(abs(steps)):
        x_step(d, speed_x)
    GPIO.output(config.x_En, 1)
    
def y_go(mm, speed_y):
    steps = mm * config.Y_STEPS_MM
    GPIO.output(config.y_En, 0)
    d = FRW if steps > 0 else BCK
    for i in range(abs(steps)):
        y_step(d, speed_y)
    GPIO.output(config.y_En, 1)
    
def z_go(mm, speed_z):
    steps = mm * config.Z_STEPS_MM
    GPIO.output(config.z_En, 0)
    d = FRW if steps > 0 else BCK
    for i in range(abs(steps)):
        z_step(d, speed_z)
    GPIO.output(config.z_En, 1)

def cnc_init():
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
    cnc_init()
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
#    cnc_init()
   # x_go(20688, 1)
   # y_go(5072, 1)
    #z_go(1500, 1)
    go_to_coor(0, 16000) #zero cam two
    #go_to_coor(0, 2635)#, 1500) #zero cam one 
    print(coordinates)
    img = get_frames(0)
    cv.imwrite(f'/tmp/out_{0}_{str(int(time())%1000)}.jpeg', img)
    GPIO.cleanup()


