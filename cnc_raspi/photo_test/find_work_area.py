import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from glob import glob
from time import time, sleep
from sympy import Line, Point

def perimeter(box):
    A = ((box[1][0] - box[0][0])**2 + (box[1][1] - box[0][1])**2)**0.5
    B = ((box[2][0] - box[1][0])**2 + (box[2][1] - box[1][1])**2)**0.5
    C = ((box[3][0] - box[2][0])**2 + (box[3][1] - box[2][1])**2)**0.5
    D = ((box[3][0] - box[0][0])**2 + (box[3][1] - box[0][1])**2)**0.5
    return A + B + C + D

def correcting_perspective(img):
    pt_A = [212,  284 ] 
    pt_B = [212,  2097] 
    pt_C = [3294, 2033]
    pt_D = [3208, 207 ]

    input_pts = np.float32([pt_A, pt_B, pt_C, pt_D])
    output_pts = np.float32([[210, 204],
                            [210, 2097], 
                            [3296, 2097], 
                            [3296, 204]])
    M = cv.getPerspectiveTransform(input_pts,output_pts)
    out = cv.warpPerspective(img,M,(img.shape[1],img.shape[0]),flags=cv.INTER_LINEAR)
    return out[204:2097, 210:3296]

def convert_cam_0_to_mm(coor):
    out = list()
    for i in range(len(coor)):
        l = list()
        l.append(300 - coor[i][0] / 10.287)
        l.append(coor[i][1] / 10.517)
        out.append(l)
        del l
    return out

def find_board_by_cam_two(img_path, req_perimeter):
    out_coor = list()
    hsv_min = np.array((0, 54, 5), np.uint8)
    hsv_max = np.array((187, 255, 253), np.uint8)

    img = cv.imread(img_path)

    hsv = cv.cvtColor( img, cv.COLOR_BGR2HSV ) 
    thresh = cv.inRange( hsv, hsv_min, hsv_max )
    contours0, hierarche = cv.findContours(thresh.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for cnt in contours0:
        rect = cv.minAreaRect(cnt)
        box = cv.boxPoints(rect)
        box = np.int0(box)
        perimeter_ = perimeter(box) / 10.286
        if ((perimeter_ < req_perimeter + 50) and (perimeter_ > req_perimeter - 50)):
            out_coor = box
            #cv.drawContours(img,[box],0,(255,0,0),2) # рисуем прямоугольник
            #plt.imshow(img),plt.show()
            #print(img_path)
            #print(box)
            #print(convert_cam_0_to_mm(box))
            #cv.imwrite('/home/duhanin/Изображения/cnc/cnc_test_1/test_ten/find_plate_'+str(img_path.split('/')[-1].split('.')[0]) + '_' + str(int(time())%1000) + '.jpg',img)
    return out_coor

def get_vertical_and_horizontal(lines):
    horizontal = []
    vertical = []
    for line in lines:
        x1,y1,x2,y2 = line[0]
        if x1 == x2 :
            vertical.append((x1, y1, x2, y2))
        elif y1 == y2 :
            horizontal.append((x1, y1, x2, y2))
        else:
            z = np.polyfit([x1, x2], [y1, y2], 1)
            if abs(z[0]) <= 1:
                horizontal.append((x1, y1, x2, y2))
            elif abs(z[0]) > 1 :
                vertical.append((x1, y1, x2, y2))
    return vertical, horizontal

def get_p_vertical(best_v, v, k):
    pass

def get_best_vertical(v):
    distance = list()
    for i in range(len(v)):
        if v[i][0] == v[i][2]:
            counter = 0
            for j in range(len(v)):
                if not (j == i) :
                    if abs(v[i][0] - v[j][0]) < 5:
                        counter += 1
                    if abs(v[i][2] - v[j][2]) < 5:
                        counter += 1
            distance.append([i, counter])
            del counter
        else:
            p = np.polyfit([v[i][0], v[i][2]], [v[i][1], v[i][3]], 1)
            counter = 0
            for j in range(len(v)):
                if not (j == i):
                    if abs(v[j][0] - ((p[1] - v[j][1])/ - p[0])) < 5:
                        counter += 1
                    if abs(v[j][0] - ((p[1] - v[j][1])/ - p[0])) < 5:
                        counter += 1
            distance.append([i, counter])
            del counter
    print(len(v))
    print(max(distance, key = lambda x: x[1]))
    p = get_p_vertical(v[max(distance, key = lambda x: x[1])[0]], v, max(distance, key = lambda x: x[1])[0])
    return v[max(distance, key = lambda x: x[1])[0]]

def get_best_horizontal(h):
    distance = list()
    for i in range(len(h)):
        if h[i][1] == h[i][3]:
            counter = 0
            for j in range(len(h)):
                if not (j == i) :
                    if abs(h[i][1] - h[j][1]) < 5:
                        counter += 1
                    if abs(h[i][3] - h[j][3]) < 5:
                        counter += 1
            distance.append([i, counter])
            del counter
        else:
            p = np.polyfit([h[i][0], h[i][2]], [h[i][1], h[i][3]], 1)
            counter = 0
            for j in range(len(h)):
                if not (j == i):
                    if abs(h[j][0] - ((p[1] - h[j][1])/ - p[0])) < 5:
                        counter += 1
                    if abs(h[j][0] - ((p[1] - h[j][1])/ - p[0])) < 5:
                        counter += 1
            distance.append([i, counter])
            del counter
    print(len(h))
    print(max(distance, key = lambda x: x[1]))
    return h[max(distance, key = lambda x: x[1])[0]]

def find_corner_by_cam_one(img_path):
    img = cv.imread(img_path)
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray,100,200,apertureSize = 3)
    lines = cv.HoughLinesP(edges,1,np.pi/180,2,minLineLength=30,maxLineGap=10)
    vertical, horizontal = get_vertical_and_horizontal(lines)
    
    print(vertical)
    cv.line(img,(605,276),(608,341),(255,0,0),2)
    cv.line(img,(120,270),(175,268),(255,255,0),2)
    cv.circle(img, (604,252), radius=2, color=(255, 0, 255), thickness=-1)
    cv.circle(img, (600,251), radius=2, color=(255, 255, 255), thickness=-1)
    #plt.imshow(img)
    #plt.show()
    best_vertical = get_best_vertical(vertical)
    print(best_vertical)
    best_horisontal = get_best_horizontal(horizontal)
    print(best_horisontal)
    line1 = Line(Point(best_vertical[0], best_vertical[1]), Point(best_vertical[2], best_vertical[3]))
    line2 = Line(Point(best_horisontal[0], best_horisontal[1]), Point(best_horisontal[2], best_horisontal[3]))
    intersect = line1.intersection(line2)
    x_intersection = int(str(intersect[0][0]).split('/')[0]) / int(str(intersect[0][0]).split('/')[1])
    y_intersection = int(str(intersect[0][1]).split('/')[0]) / int(str(intersect[0][1]).split('/')[1])
    print(x_intersection, y_intersection)

if __name__ == '__main__':
    #find_corner_by_cam_one('/tmp/out_2_834.jpeg')
    img_orig = cv.imread('/home/duhanin/Изображения/cnc/cnc_test_1/test_ten/out_0_912.jpeg')
    out = correcting_perspective(img_orig)
    cv.imwrite('/tmp/out_linear.jpg', out)
    out_pix_coor = find_board_by_cam_two('/tmp/out_linear.jpg', 666)
    coor_board_by_cam_two = convert_cam_0_to_mm(out_pix_coor)
    print(coor_board_by_cam_two)
