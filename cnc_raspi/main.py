import rpi_gpio.cnc
import photo_test.find_work_area

if __name__ == '__main__':
	rpi_gpio.cnc.run_gpio()
	rpi_gpio.cnc.cnc_init()
	print(rpi_gpio.cnc.coordinates)
	rpi_gpio.cnc.stop_gpio()