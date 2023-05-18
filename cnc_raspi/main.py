import rpi_gpio.cnc
import photo_test.find_work_area
import cv2 as cv
from time import time

if __name__ == '__main__':
    rpi_gpio.cnc.run_gpio()
    try:
        rpi_gpio.cnc.cnc_init()
        rpi_gpio.cnc.go_to_coor(0, 16000)
    
        img = rpi_gpio.cnc.get_frames(0)
        t = int(time()) % 100000
        cv.imwrite(f'/tmp/out_{0}_{str(t)}.jpeg', img)
        print(rpi_gpio.cnc.coordinates)

        img_orig = cv.imread(f'/tmp/out_{0}_{str(t)}.jpeg')
        out = photo_test.find_work_area.correcting_perspective(img_orig)
        cv.imwrite('/tmp/out_linear.jpg', out)
        out_pix_coor = photo_test.find_work_area.find_board_by_cam_two('/tmp/out_linear.jpg', 240)
        coor_board_by_cam_two = photo_test.find_work_area.convert_cam_0_to_mm(out_pix_coor)
        coor_for_cam_one = [[int(round(x, 2)*100) - 3264, int(round(y, 2)*100) + 2672] for [x, y] in coor_board_by_cam_two]
        print(coor_for_cam_one)
        for corner in coor_for_cam_one:
            rpi_gpio.cnc.go_to_coor(corner[0], corner[1])
            rpi_gpio.cnc.z_go(1500, 1)
            t = str(int(time())%100000)
            img = rpi_gpio.cnc.get_frames(2)
            cv.imwrite(f'/tmp/out_{2}_{rpi_gpio.cnc.coordinates}_{t}.jpeg', img)
            rpi_gpio.cnc.init_axis_z()
            print(f"[INFO:] {corner} -- photographed!")
        rpi_gpio.cnc.stop_gpio()
    except Exception as e:
        print(e)
        rpi_gpio.cnc.stop_gpio()