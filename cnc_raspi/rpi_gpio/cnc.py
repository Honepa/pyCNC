"""
TODO:
1) sum time by onece
2) averenge END's for best init
#sys.path.append('..')
#import photo_test.find_work_area
"""
import config
from time import sleep, time
import cv2 as cv
import numpy as np
import sys
import RPi.GPIO as GPIO
from statistics import mean, median

#config = rpi_gpio.config
#FRW =  1
#BCK = -1
#coor_x     = 0
#coor_y     = 1
#coor_z     = 2#
#coor_freza = 3
#coordinates = [0, 0, 0, 0]

class CNC:
    def __init__(self, GPIO):
        self.gpio = GPIO
        self.config = config
        self.__set_initial_values()
        self.__init_gpio__()
        self.cams = []
        self.cams.append(cv.VideoCapture(0))
        self.cams.append(cv.VideoCapture(2))
        #self.__init_cnc__()

    def __set_initial_values(self):
        self.FRW =  1
        self.BCK = -1
        self.coordinates = [0, 0, 0]
        self.coor_x      = 0
        self.coor_y      = 1
        self.coor_z      = 2
        self.config = config

    def __init_gpio__(self):
        self.gpio.setmode(self.gpio.BOARD)
        self.gpio.setwarnings(True)
        self.gpio.setup([self.config.X_END, self.config.Y_END, self.config.Z_END, self.config.F_END], self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
    
        self.gpio.setup([self.config.x_St, self.config.x_Dr, self.config.x_En], self.gpio.OUT, initial=self.gpio.LOW)
        self.gpio.output(self.config.x_En, 1)
    
        self.gpio.setup([self.config.y_St, self.config.y_Dr, self.config.y_En], self.gpio.OUT, initial=self.gpio.LOW)
        self.gpio.output(self.config.y_En, 1)
    
        self.gpio.setup([self.config.z_St, self.config.z_Dr, self.config.z_En], self.gpio.OUT, initial=self.gpio.LOW)
        self.gpio.output(self.config.z_En, 1)

        FREQUENCY = 100
    
        self.gpio.setup(self.config.Freza, self.gpio.OUT)
        self.freza = self.gpio.PWM(self.config.Freza, FREQUENCY)

    def __init_cnc__(self):
        print("[INFO:] INIT CNC")
        self.__init_axis_z__()
        self.__init_axis_x__()
        self.__init_axis_y__()
        print("[INFO:] CNC is init")

    def __init_axis_x__(self):
        count = 0
        while((self.gpio.input(self.config.X_END)) and (count < 270)):
            self.x_go(-100, 1)
            count += 1
        self.x_go(500, 1)
        count = 0
        while((self.gpio.input(self.config.X_END)) and (count < 500)):
            self.x_go(-1, 0.05)
            count += 1
        while(not (self.gpio.input(self.config.X_END))):
            self.x_go(1, 0.1)
        self.coordinates[self.coor_x] = 0

    def x_go(self, mm, speed_x = 6):
        steps = mm * self.config.X_STEPS_MM
        self.gpio.output(self.config.x_En, 0)
        d = self.FRW if steps > 0 else self.BCK
        for i in range(abs(steps)):
            self.x_step(d, speed_x)
        self.gpio.output(self.config.x_En, 1)

    def x_step(self, direction, speed_x):
        d = 1 if direction == self.FRW else 0
        self.gpio.output(self.config.x_St, 0)
        self.gpio.output(self.config.x_Dr, d)
        sleep((round(round((pow(speed_x * 800, -1) * pow(10, 5))) / 2)) * 10**-6)
        self.gpio.output(self.config.x_St, 1)
        self.gpio.output(self.config.x_Dr, d)
        sleep((round(round((pow(speed_x * 800, -1) * pow(10, 5))) / 2)) * 10**-6) 
        self.coordinates[self.coor_x] += direction * 125

    def __init_axis_y__(self):
        count = 0
        while((self.gpio.input(self.config.Y_END)) and (count < 270)):
            self.y_go(-100, 1)
            count += 1
        self.y_go(500, 1)
        count = 0
        while((self.gpio.input(self.config.Y_END)) and (count < 500)):
            self.y_go(-1, 0.05)
            count += 1
        while(not (self.gpio.input(self.config.Y_END))):
            self.y_go(1, 0.1)
        self.coordinates[self.coor_y] = 0

    def y_go(self, mm, speed_y = 6):
        steps = mm * self.config.Y_STEPS_MM
        self.gpio.output(self.config.y_En, 0)
        d = self.FRW if steps > 0 else self.BCK
        for i in range(abs(steps)):
            self.y_step(d, speed_y)
        self.gpio.output(self.config.y_En, 1)

    def y_step(self, direction, speed_y):
        d = 1 if direction == self.FRW else 0
        self.gpio.output(self.config.y_St, 0)
        self.gpio.output(self.config.y_Dr, d)
        sleep((round(round((pow(speed_y * 800, -1) * pow(10, 5))) / 2)) * 10**-6)
        self.gpio.output(self.config.y_St, 1)
        self.gpio.output(self.config.y_Dr, d)
        sleep((round(round((pow(speed_y * 800, -1) * pow(10, 5))) / 2)) * 10**-6) 
        self.coordinates[self.coor_y] += direction * 125

    def __init_axis_z__(self):
        count = 0
        while((self.gpio.input(self.config.Z_END)) and (count < 270)):
            self.z_go(-100, 1)
            count += 1
        self.z_go(500, 1)
        count = 0
        while((self.gpio.input(self.config.Z_END)) and (count < 500)):
            self.z_go(-1, 0.05)
            count += 1
        while(not (self.gpio.input(self.config.Z_END))):
            self.z_go(1, 0.1)
        self.coordinates[self.coor_z] = 0

    def z_go(self, mm, speed_z = 6):
        steps = mm * self.config.Z_STEPS_MM
        self.gpio.output(self.config.z_En, 0)
        d = self.FRW if steps > 0 else self.BCK
        for i in range(abs(steps)):
            self.z_step(d, speed_z)
        self.gpio.output(self.config.z_En, 1)

    def z_step(self, direction, speed_z):
        d = 1 if direction == self.FRW else 0
        self.gpio.output(self.config.z_St, 0)
        self.gpio.output(self.config.z_Dr, d)
        sleep((round(round((pow(speed_z * 800, -1) * pow(10, 5))) / 2)) * 10**-6)
        self.gpio.output(self.config.z_St, 1)
        self.gpio.output(self.config.z_Dr, d)
        sleep((round(round((pow(speed_z* 800, -1) * pow(10, 5))) / 2)) * 10**-6) 
        self.coordinates[self.coor_z] += direction * 125

    def get_zero_freza(self):
        #init_axis_z()
        f = 0
        test_coor_z_list = list()
        for i in range(5):
            f = 0
            while( f < 90 and self.coordinates[self.coor_z] < 6000000):
                self.z_go(1, 0.25)
                f = 0
                for i in range(100):
                    f += self.gpio.input(self.config.F_END)
            #print(f)
            test_coor_z_list.append(self.coordinates[self.coor_z])
            self.z_go(-400, 4)
        #print(test_coor_z_list)
        #print(mean(test_coor_z_list))
        #init_axis_z()
        return mean(test_coor_z_list)
    

    def get_frames(self, id):
        cam  = self.cams[id]
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

    def camera_screen(self, coordinates):
        ret, frame = cv.VideoCapture(0).read()
        screen_name = f'/tmp/cnc/{str(self.coordinates)}.jpeg'
        cv.imwrite(screen_name, frame)
        print("Screen saved in " + screen_name)

    def go_to_coor(self, x, y):
        dx = x - int(self.coordinates[self.coor_x] / 1000)
        dy = y - int(self.coordinates[self.coor_y] / 1000)
        self.x_go(dx)
        self.y_go(dy)

    def stop_gpio(self):
        self.gpio.cleanup()

if __name__ == "__main__":

    
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
    cnc = CNC(GPIO)
    cnc.__init_cnc__()
    
    cnc.go_to_coor(0, 26350)
    print(cnc.coordinates)
    img = cnc.get_frames(0)
    t = str(int(time())%100000)
    cv.imwrite(f'/tmp/out_{2}_{t}.jpeg', img)
    #cnc.camera_screen(cnc.coordinates)
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
    cnc.stop_gpio()
    #GPIO.cleanup()


