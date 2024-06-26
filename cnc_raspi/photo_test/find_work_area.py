import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from glob import glob
from time import time, sleep
from sympy import Line, Point
import math
from statistics import mean, median

class FWA:
    def __init__(self):
        pass

    def get_diagonal(self, box):
        try:
            x0, y0 = mean([x for x, y in box]), mean([y for x, y in box])
            min_pt = [[x, y] for x, y in box if x <= x0 and y >= y0][0]
            max_pt = [[x, y] for x, y in box if x >= x0 and y <= y0][0]

            return math.dist(min_pt, max_pt)
        except:
            #print(box)
            #print([[x, y] for x, y in box if x <= x0 and y <= y0])
            return 0

    def det_min_max_side(self, box):
        A = ((box[1][0] - box[0][0])**2 + (box[1][1] - box[0][1])**2)**0.5
        B = ((box[2][0] - box[1][0])**2 + (box[2][1] - box[1][1])**2)**0.5
        C = ((box[3][0] - box[2][0])**2 + (box[3][1] - box[2][1])**2)**0.5
        D = ((box[3][0] - box[0][0])**2 + (box[3][1] - box[0][1])**2)**0.5
        sides = [A, B, C, D]
        return min(sides) / 10.286, max(sides) / 10.286

    def rotate(self, img_path, angle):
        img = cv.imread(img_path)
        rows,cols = img.shape[0], img.shape[1]
        M = cv.getRotationMatrix2D(((cols-1)/2.0,(rows-1)/2.0),angle,1)
        dst = cv.warpAffine(img,M,(cols,rows))
        #plt.imshow(dst), plt.show()
        #cv.imwrite('/tmp/out_2_4343_rotate.jpg', dst)
        return dst[20:940, 35:1261]

    def correcting_perspective(self, img):
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

    def convert_cam_0_to_mm(self, coor):
        out = list()
        for i in range(len(coor)):
            l = list()
            l.append(300 - coor[i][0] / 10.287)
            l.append(coor[i][1] / 10.517)
            out.append(l)
            del l
        return out

    def find_board_by_cam_two(self, img_path, req_diagonal, min_side, max_side):
        out_coor = list()
        hsv_min = np.array((0, 54, 5), np.uint8)
        hsv_max = np.array((187, 255, 253), np.uint8)

        img = cv.imread(img_path)

        hsv = cv.cvtColor( img, cv.COLOR_BGR2HSV ) 
        thresh = cv.inRange( hsv, hsv_min, hsv_max )
        contours0, hierarche = cv.findContours(thresh.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        img_t = img
        #cv.drawContours(img_t, contours0, -1, (0, 0, 255), 3)
        #plt.imshow(img_t)
        #plt.show()
        for cnt in contours0:
            rect = cv.minAreaRect(cnt)
            box = cv.boxPoints(rect)
            box = np.int0(box)
            diagonal_ = self.get_diagonal(box) / 10.286
            #cv.drawContours(img_t,[box],0,(255,0,0),2)
            min_side_, max_side_ = self.det_min_max_side(box)
            if ((diagonal_ < req_diagonal + 15) and (diagonal_ > req_diagonal - 15)) and ((min_side_ < min_side + 10) and (min_side_ > min_side - 10)) and ((max_side_ < max_side + 10) and (max_side_ > max_side - 10)):
                #print(diagonal_)
                out_coor = box
                cv.drawContours(img,[box],0,(0,0,255),40) # рисуем прямоугольник
                #plt.imshow(img),plt.show()
                #print(img_path)
                #print(box)
                #print(convert_cam_0_to_mm(box))
                cv.imwrite('/home/duhanin/Изображения/cnc/cnc_test_1/test_ten/find_plate_'+str(img_path.split('/')[-1].split('.')[0]) + '_' + str(int(time())%1000) + '.jpg',img)
        #plt.imshow(img_t)
        #plt.show()
        return out_coor

    def get_vertical_and_horizontal(self, lines, img):
        horizontal = []
        vertical = []
        for line in lines:
            x1,y1,x2,y2 = line[0]
            if x1 == x2 :
                cv.line(img,(x1,y1),(x2,y2),(128,0,128),12)
                vertical.append((x1, y1, x2, y2))
            elif y1 == y2 :
                cv.line(img,(x1,y1),(x2,y2),(255,0,0),12)
                horizontal.append((x1, y1, x2, y2))
            else:
                z = np.polyfit([x1, x2], [y1, y2], 1)
                if abs(z[0]) <= 1:
                    cv.line(img,(x1,y1),(x2,y2),(255,0,0),12)
                    horizontal.append((x1, y1, x2, y2))
                elif abs(z[0]) > 1 :
                    cv.line(img,(x1,y1),(x2,y2),(128,0,128),12)
                    vertical.append((x1, y1, x2, y2))
        return vertical, horizontal, img

    def get_p_vertical(self, best_v, v, k):
        pass

    def get_best_vertical(self, v):
        distance = list()
        for i in range(len(v)):
            if v[i][0] == v[i][2]:
                counter = 0
                for j in range(len(v)):
                    if not (j == i) :
                        if abs(v[i][0] - v[j][0]) < 2:
                            counter += 1
                        if abs(v[i][2] - v[j][2]) < 2:
                            counter += 1
                distance.append([i, counter])
                del counter
            else:
                p = np.polyfit([v[i][0], v[i][2]], [v[i][1], v[i][3]], 1)
                counter = 0
                for j in range(len(v)):
                    if not (j == i):
                        if abs(v[j][0] - ((p[1] - v[j][1])/ - p[0])) < 2:
                            counter += 1
                        if abs(v[j][0] - ((p[1] - v[j][1])/ - p[0])) < 2:
                            counter += 1
                distance.append([i, counter])
                del counter
        #print(distance)
        #print(max(distance, key = lambda x: x[1]))
        #p = self.get_p_vertical(v[max(distance, key = lambda x: x[1])[0]], v, max(distance, key = lambda x: x[1])[0])
        return v[max(distance, key = lambda x: x[1])[0]]

    def get_best_horizontal(self, h):
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
        #print(distance)
        #print(max(distance, key = lambda x: x[1]))
        return h[max(distance, key = lambda x: x[1])[0]]

    def find_corner_by_cam_one(self, img):
        img = img
        gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
        edges = cv.Canny(gray,100,200,apertureSize = 3)
        lines = cv.HoughLinesP(edges,1,np.pi/180,2,minLineLength=30,maxLineGap=10)
        vertical, horizontal, img = self.get_vertical_and_horizontal(lines, img)
    
        #print(vertical)

        best_vertical = self.get_best_vertical(vertical)
        #print(best_vertical)
        best_horisontal = self.get_best_horizontal(horizontal)
        #print(best_horisontal)

        cv.line(img,(best_vertical[0],best_vertical[1]),(best_vertical[2],best_vertical[3]),(0,0,255),12)
        cv.line(img,(best_horisontal[0],best_horisontal[1]),(best_horisontal[2],best_horisontal[3]),(255,255,0),12)

        line1 = Line(Point(best_vertical[0], best_vertical[1]), Point(best_vertical[2], best_vertical[3]))
        line2 = Line(Point(best_horisontal[0], best_horisontal[1]), Point(best_horisontal[2], best_horisontal[3]))
        intersect = line1.intersection(line2)
        if len(str(intersect[0][0]).split('/')) > 1:
            x_intersection = int(str(intersect[0][0]).split('/')[0]) / int(str(intersect[0][0]).split('/')[1])
        else:
            x_intersection = int(str(intersect[0][0]))
        if len(str(intersect[0][1]).split('/')) > 1:
            y_intersection = int(str(intersect[0][1]).split('/')[0]) / int(str(intersect[0][1]).split('/')[1])
        else:
            y_intersection = int(str(intersect[0][1]))
        #print(x_intersection, y_intersection)
        cv.circle(img, (int(x_intersection),int(y_intersection)), radius=12, color=(255, 0, 255), thickness=-1)
        cv.circle(img, (640,480), radius=12, color=(255, 255, 255), thickness=-1)
        #plt.imshow(img)
        #plt.show()
        return (640 - x_intersection)/34.5 , (480 - y_intersection)/35, img

if __name__ == '__main__':
    '''
    imgs_path = glob("/tmp/test_cnc/*")
    for img_path in imgs_path:
        img = rotate(img_path, angle = 1.8)
    #img = cv.imread('/tmp/out_2_76735_.jpeg')
        dx, dy, img = find_corner_by_cam_one(img)
        plt.imshow(img)
        plt.show()
        dx = int(round(dx, 2) * 100)
        dy = int(round(dy, 2) * 100)
        print(dx, dy)
    
    fwa = FWA()
    #img = fwa.rotate('/tmp/out_2_4343.jpeg', angle = 1.8)
    #dx, dy, img = find_corner_by_cam_one('/tmp/out_2_815.jpeg')
    #plt.imshow(img)
    #plt.show()
    #cv.imwrite(f'/tmp/test_cnc_out/out_corner_{img_path}', img)
    #print(dx, dy)
    '''
    #img_orig = cv.imread('/tmp/out_0_19039.jpeg')
    #out = correcting_perspective(img_orig)
    #cv.imwrite('/tmp/out_linear.jpg', out)
    fwa = FWA()
    
    '''
    a = 140
    b = 190
    out_pix_coor = fwa.find_board_by_cam_two('/tmp/out_linear.jpg', (a**2 + b**2)**0.5 ,140, 190)
    coor_board_by_cam_two = fwa.convert_cam_0_to_mm(out_pix_coor)
    print(coor_board_by_cam_two)
    '''
    