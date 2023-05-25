from rpi_gpio.cnc import CNC
from photo_test.find_work_area import FWA
import cv2 as cv
from time import time, sleep
import sys
import RPi.GPIO as GPIO
from statistics import mean, median
cccc = list()

if __name__ == '__main__':
    try:
        stanok = CNC(GPIO)
        fwa = FWA()
        stanok.__init_cnc__()
        #[[coor[0] + 807, coor[1] - 4750] for coor in k]
        coors = [[15693, 3076], [10278, 2762], [9880, 9228], [15304, 9541]]
        x0, y0 = mean([x for x, y in coors]), mean([y for x, y in coors])
        start_pt = [[x+1000, y-1000] for x, y in now_k if x > x0 and y > y0][0]
        stanok.go_to_coor(start_pt[0], start_pt[1])
        print(stanok.get_zero_freza)
        stanok.__init_axis_z__()
        '''
        stanok.go_to_coor(0, 16000)
        img = stanok.get_frames(0)
        t = int(time()) % 100000
        cv.imwrite(f'/tmp/out_{0}_{str(t)}.jpeg', img)
        print(stanok.coordinates)

        img_orig = cv.imread(f'/tmp/out_{0}_{str(t)}.jpeg')
        out = fwa.correcting_perspective(img_orig)
        cv.imwrite('/tmp/out_linear.jpg', out)
        a = 55
        b = 65
        out_pix_coor = fwa.find_board_by_cam_two('/tmp/out_linear.jpg', (a**2 + b**2)**0.5 ,55, 65)
        coor_board_by_cam_two = fwa.convert_cam_0_to_mm(out_pix_coor)
        coor_for_cam_one = [[int(round(x, 2)*100) - 3264, int(round(y, 2)*100) + 2672] for [x, y] in coor_board_by_cam_two]
        print(coor_for_cam_one)

        coor_of_plate = list()
        for corner in coor_for_cam_one:
            stanok.go_to_coor(corner[0], corner[1])
            stanok.z_go(1500, 1)
            t = str(int(time())%100000)
            img = stanok.get_frames(2)
            cv.imwrite(f'/tmp/out_{2}_{t}.jpeg', img)
            img = fwa.rotate(f'/tmp/out_{2}_{t}.jpeg', angle = 1.8)
            dx, dy, img = fwa.find_corner_by_cam_one(img)
            #stanok.init_axis_z()
            dx = int(round(dx, 2) * 100)
            dy = int(round(dy, 2) * 100)
            #print(dx, dy)
            count = 0
            while ((count > 150) or ((dx**2 + dy**2)**0.5 > 10)):
                stanok.x_go(-dx, 1)
                stanok.y_go(dy, 1)
                img = stanok.get_frames(2)
                t = str(int(time())%100000)
                cv.imwrite(f'/tmp/out_{2}_{t}.jpeg', img)
                #print(f"[INFO:] img write in /tmp/out_{2}_{t}.jpeg")
                img = fwa.rotate(f'/tmp/out_{2}_{t}.jpeg', angle = 1.8)
                #img = cv.imread('/tmp/out_2_76735_.jpeg')
                dx, dy, img = fwa.find_corner_by_cam_one(img)
                #plt.imshow(img)
                #plt.show()
                dx = int(round(dx, 2) * 100)
                dy = int(round(dy, 2) * 100)
                #print(dx, dy)
                count += 1
                cccc = stanok.coordinates
            if count < 150:
                print(stanok.coordinates)
                coor_of_plate.append(cccc)
            else:
                print(f"[ERROR:] error by corner in {corner}")
            stanok.__init_axis_z__()
        print(coor_of_plate)
        '''
        stanok.stop_gpio()
    except Exception as e:
        print(e)
        stanok.stop_gpio()
    except KeyboardInterrupt:
        stanok.stop_gpio()
    '''
    rpi_gpio.cnc.run_gpio()
    try:
        rpi_gpio.cnc.cnc_init()
        x = 10733
        y = 8395
        gcode = list()
        for i in range(35):
            for j in range(35):
                gcode.append([x, y])
    
                if not i % 2:
                    x += 100
                else:
                    x -= 100
            y -= 100
        for x, y in gcode:
            rpi_gpio.cnc.go_to_coor(x, y)
            print(f"[INFO] : point {x} -- {y} has been scanned!", file=sys.stderr)
            rpi_gpio.cnc.get_zero_freza()
        #print(len(gcode))
        #print(gcode[0])
        #print(gcode[-1])

        #rpi_gpio.cnc.go_to_coor(12759, 6151)
        #rpi_gpio.cnc.get_zero_freza()
        #print(rpi_gpio.cnc.coordinates)
        
        rpi_gpio.cnc.go_to_coor(0, 16000)
    
        img = rpi_gpio.cnc.get_frames(0)
        t = int(time()) % 100000
        cv.imwrite(f'/tmp/out_{0}_{str(t)}.jpeg', img)
        print(rpi_gpio.cnc.coordinates)

        img_orig = cv.imread(f'/tmp/out_{0}_{str(t)}.jpeg')
        out = photo_test.find_work_area.correcting_perspective(img_orig)
        cv.imwrite('/tmp/out_linear.jpg', out)
        a = 55
        b = 65
        out_pix_coor = photo_test.find_work_area.find_board_by_cam_two('/tmp/out_linear.jpg', (a**2 + b**2)**0.5 ,55, 65)
        coor_board_by_cam_two = photo_test.find_work_area.convert_cam_0_to_mm(out_pix_coor)
        coor_for_cam_one = [[int(round(x, 2)*100) - 3264, int(round(y, 2)*100) + 2672] for [x, y] in coor_board_by_cam_two]
        print(coor_for_cam_one)
        coor_of_plate = list()
        for corner in coor_for_cam_one:
            rpi_gpio.cnc.go_to_coor(corner[0], corner[1])
            rpi_gpio.cnc.z_go(1500, 1)
            t = str(int(time())%100000)
            img = rpi_gpio.cnc.get_frames(2)
            cv.imwrite(f'/tmp/out_{2}_{t}.jpeg', img)
            img = photo_test.find_work_area.rotate(f'/tmp/out_{2}_{t}.jpeg', angle = 1.8)
            dx, dy, img = photo_test.find_work_area.find_corner_by_cam_one(img)
            #rpi_gpio.cnc.init_axis_z()
            dx = int(round(dx, 2) * 100)
            dy = int(round(dy, 2) * 100)
            #print(dx, dy)
            count = 0
            while ((count > 150) or ((dx**2 + dy**2)**0.5 > 10)):
                rpi_gpio.cnc.x_go(-dx, 1)
                rpi_gpio.cnc.y_go(dy, 1)
                img = rpi_gpio.cnc.get_frames(2)
                t = str(int(time())%100000)
                cv.imwrite(f'/tmp/out_{2}_{t}.jpeg', img)
                #print(f"[INFO:] img write in /tmp/out_{2}_{t}.jpeg")
                img = photo_test.find_work_area.rotate(f'/tmp/out_{2}_{t}.jpeg', angle = 1.8)
                #img = cv.imread('/tmp/out_2_76735_.jpeg')
                dx, dy, img = photo_test.find_work_area.find_corner_by_cam_one(img)
                #plt.imshow(img)
                #plt.show()
                dx = int(round(dx, 2) * 100)
                dy = int(round(dy, 2) * 100)
                #print(dx, dy)
                count += 1
                cccc = rpi_gpio.cnc.coordinates
            if count < 150:
                print(rpi_gpio.cnc.coordinates)
                rpi_gpio.cnc.save_coor()
            else:
                print(f"[ERROR:] error by corner in {corner}")
            rpi_gpio.cnc.init_axis_z()
        print(rpi_gpio.cnc.find_coor)
        '''
    