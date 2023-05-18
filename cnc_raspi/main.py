import rpi_gpio.cnc
import photo_test.find_work_area
import cv2 as cv
from time import time

if __name__ == '__main__':
	rpi_gpio.cnc.run_gpio()
	
	rpi_gpio.cnc.cnc_init()
	rpi_gpio.cnc.go_to_coor(0, 16000)
	
	img = rpi_gpio.cnc.get_frames(0)
	t = int(time()) % 100000
	cv.imwrite(f'/tmp/out_{0}_{str(t)}.jpeg', img)
	print(rpi_gpio.cnc.coordinates)
	out_pix_coor = photo_test.find_work_area.find_board_by_cam_two(f'/tmp/out_{0}_{str(t)}.jpeg', 666)
    coor_board_by_cam_two = photo_test.find_work_area.convert_cam_0_to_mm(out_pix_coor)
    print(coor_board_by_cam_two)

	rpi_gpio.cnc.stop_gpio()