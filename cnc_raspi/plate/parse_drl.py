import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    
    f = open('/home/duhanin/Документы/CNC станок (ВКР)/test_plate.drl', 'r')
    file = list()
    for line in f:
        file.append(line)
    f.close()

    drills = file[file.index('METRIC\n') + 1 : file.index('%\n', file.index('METRIC\n'))]

    dril_name_mm = list()
    for dril in drills:
        dril_name_mm.append([dril.split('C')[0], dril.split('C')[1].split('\n')[0]])
    print(dril_name_mm)
    
    drill = list()

    for i in range(len(dril_name_mm)):
        if not (i == len(dril_name_mm) - 1):
            coors = file[file.index(f'{dril_name_mm[i][0]}\n') + 1:file.index(f'{dril_name_mm[i + 1][0]}\n')]
            for coor in coors:
                drill.append([float(dril_name_mm[i][1]), int(coor.split('Y-')[0].split('X')[-1]) ,int(coor.split('Y-')[-1])])
        else:
            coors = file[file.index(f'{dril_name_mm[i][0]}\n') + 1:file.index('M30\n')]
            for coor in coors:
                drill.append([float(dril_name_mm[i][1]), int(coor.split('Y-')[0].split('X')[-1]) ,int(coor.split('Y-')[-1])])
    print(drill)
    for_draw = [[int(point[0] * 40), int((point[1] * 47.25)/100),int((point[2]*47.25)/100)] for point in drill]
    print(for_draw)
    src = cv.imread("/home/duhanin/Документы/CNC станок (ВКР)/test_plate.bmp")

    for point in for_draw:
        print(point)
        cv.circle(src, (point[1], point[2]), int(point[0]/200), (0, 255, 0), point[0]*2)
    #plt.imshow(src)
    #plt.show()

    imgray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(imgray, 0, 255, 0)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(src, contours, -1, (0, 255, 0), 10)
    contours_ = contours
    
    imgray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(imgray, 0, 255, 0)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    
    #cv.drawContours(src, contours_, -1, (0, 255, 0), 3)
    cv.drawContours(src, contours, -1, (0, 0, 255), 5)
    #out = np.zeros((len(src[0]), len(src), 3))
    #cv.drawContours(out, contours, 0, (0, 0, 255), 3)
    print(len(contours[0]))
    plt.imshow(src)
    plt.show()
