import cv2
import numpy as np
import time
import copy
import serial           
import sys
import math
from threading import Timer


fourcc = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')                 # MPEG-4格式
anglefile = open('test11angleC.txt', 'r')

cap = cv2.VideoCapture('test11C.mp4')                               # set red threshold
lower_red = np.array([0, 230, 100])
upper_red = np.array([3, 255, 200])
lower_reda = np.array([175, 230, 100])
upper_reda = np.array([180, 255, 200])

# BHeight = 8   8米
# BWidth = 6    6米
# roi_x = 1466
# roi_y = 917
set_param2 = 10
FirstM = True  

# 创建一个空白轨迹图并绘制坐标轴
trace_img = np.zeros((1080, 1920, 3), np.uint8)
trace_img.fill(255)
cv2.line(trace_img, (1800, 100), (100, 100), (11, 134, 184), 2)
cv2.line(trace_img, (100, 100), (108, 92), (11, 134, 184), 2)
cv2.line(trace_img, (100, 100), (108, 108), (11, 134, 184), 2)
cv2.line(trace_img, (1800, 100), (1800, 1000), (11, 134, 184), 2)
cv2.line(trace_img, (1800, 1000), (1792, 992), (11, 134, 184), 2)
cv2.line(trace_img, (1800, 1000), (1808, 992), (11, 134, 184), 2)
p1 = p2 = p3 = p4 = [-1, -1]
count = 0


def return_coordinate(event, x, y):
    global p1, p2, p3, p4, count, frame
    if event == cv2.EVENT_LBUTTONDOWN and count == 0:
        p1 = [x, y]
        cv2.circle(frame, (x, y), 6, (0, 0, 255), 2)
        count += 1
    elif event == cv2.EVENT_LBUTTONDOWN and count == 1:
        p2 = [x, y]
        cv2.circle(frame, (x, y), 6, (240, 207, 137), 2)
        count += 1
    elif event == cv2.EVENT_LBUTTONDOWN and count == 2:
        p3 = [x, y]
        cv2.circle(frame, (x, y), 6, (240, 207, 137), 2)
        count += 1
    elif event == cv2.EVENT_LBUTTONDOWN and count == 3:
        p4 = [x, y]
        cv2.circle(frame, (x, y), 6, (240, 207, 137), 2)
        count += 1


def read_data():
    s = anglefile.readline()
    # s = s.decode()
    return s[13:]


def PerspectiveTransform_get(video_url):
    global p1, p2, p3, p4, count, frame
    cap = cv2.VideoCapture(video_url)
    # get a frame and show
    ret, frame = cap.read()
    if ret:
        frameinital = copy.deepcopy(frame)
        cv2.imshow('SET', frame)
        cv2.setMouseCallback('SET', return_coordinate)
        while cv2.waitKey(1) & 0xFF != 13:
            cv2.imshow('SET', frame)
            if cv2.waitKey(1) == 27:
                count = 0
                frame = copy.deepcopy(frameinital)
        count = 0
        SrcPointsA = np.array([p1, p2, p3, p4], np.float32)
    cap.release()
    cv2.destroyAllWindows()
    return SrcPointsA


def LocationDetection(PerspectiveMatrix, frame, BHeight, BWidth, Base):
    global roi_x, roi_y, set_param2, FirstM
    w, h = frame.shape[0:2]
    frame = cv2.warpPerspective(frame, PerspectiveMatrix, (h, w))
    # 画出坐标轴
    cv2.line(frame, (1800, 100), (100, 100), (11, 134, 184), 2)
    cv2.line(frame, (100, 100), (108, 92), (11, 134, 184), 2)
    cv2.line(frame, (100, 100), (108, 108), (11, 134, 184), 2)
    cv2.line(frame, (1800, 100), (1800, 1000), (11, 134, 184), 2)
    cv2.line(frame, (1800, 1000), (1792, 992), (11, 134, 184), 2)
    cv2.line(frame, (1800, 1000), (1808, 992), (11, 134, 184), 2)
    # cv2.imshow('Capture', frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_red, upper_red)
    maska = cv2.inRange(hsv, lower_reda, upper_reda)
    mask = cv2.bitwise_or(mask, maska)
    # cv2.imshow('CaptureMask', mask)
    # HoughCircles
    # print(FirstM)
    if not FirstM:
        mask = mask[roi_y-56:roi_y+56,roi_x-56:roi_x+56]
    # cv2.imshow('CaptureMaskk',mask)
        
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, 100, param1=100,param2=set_param2,minRadius=3,maxRadius=25)
    while type(circles) != np.ndarray and set_param2!=4:
        set_param2 -= 1
        circles= cv2.HoughCircles(mask,cv2.HOUGH_GRADIENT,1,100,param1=100,param2=set_param2,minRadius=3,maxRadius=25)

    if type(circles) == np.ndarray :           
        # drawing the circle
        circle = circles[0][0]
        if FirstM:
            x = int(circle[0])
            y = int(circle[1])
            r = int(circle[2])
            FirstM = False
        else:
            x = int(circle[0]) + roi_x - 56
            y = int(circle[1]) + roi_y - 56
            r = int(circle[2])
        # print(set_param2)
        # print(x,y)
        img = cv2.circle(frame, (x, y), 8, (255, 255, 255), -1)
        try:
            angle = read_data()
        except:
            angle = 0
        angle = float(angle)*math.pi/180
        img = cv2.line(img, (x, y), (int(x - 20 * math.cos(angle)), int(y - 20 * math.sin(angle))), (255, 255, 255), 3)

        roi_x = x
        roi_y = y
        img = cv2.rectangle(img, (x - 56, y + 56), (x + 56, y - 56), (255, 255, 0), 2)
        img = np.rot90(img, -1)
        img = img.copy()
        if Base == 'Height':
            img = cv2.putText(img, '(%d,%d),%.2f度' %((y-100)/(17/BHeight),(1800-x)/(17/BHeight),angle*180/math.pi),(1025-y,x-41),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1)
            X = (y - 100) / (17 / BHeight)
            Y = (1800 - x) / (17 / BHeight)
            ANGLE = angle * 180 / math.pi
        else:
            img = cv2.putText(img, '(%d, %d), %.2f度' %((y-100)/(9/BWidth),(1800-x)/(9/BWidth),angle*180/math.pi),(1025-y,x-41),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1)
            X = (y - 100) / (9 / BWidth)
            Y = (1800 - x) / (9 / BWidth)
            ANGLE = angle * 180 / math.pi
    else:
        img = frame
        img = np.rot90(img, -1)
        # print('1')
    # show the new image
    # cv2.imshow('Result',img)
    # print(roi_x, roi_y)
    return img, X, Y, ANGLE


def TrajectoryTracking():
    global trace_img, roi_x, roi_y
    trace_img = cv2.circle(trace_img, (roi_x, roi_y), 5, (0, 0, 0), -1)
    img = np.rot90(trace_img, -1)
    return img
