#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import numpy as np
import cv2, random, math, time

Width = 640
Height = 480
Offset = 330


# ROI 설정
def region_of_interest(img, w_threshold, h_threshold):
    # img와 크기가 같은 값이 0인 zero_img 생성
    zero_img = np.zeros((Height, Width), dtype='uint8')
    # mask 영역 설정(가로 마스크 - 살릴 영역)
    w_mask = np.array([[(0, Offset - w_threshold), (0, Offset + w_threshold), (Width, Offset + w_threshold),
                        (Width, Offset - w_threshold)]])
    # mask 영역 설정(세로 마스크-중앙선 - 지울 영역)
    h_mask = np.array([[(Width / 2 - h_threshold, 0), (Width / 2 - h_threshold, Height),
                        (Width / 2 + h_threshold, Height), (Width / 2 + h_threshold, 0)]])
    # mask 영역으로 mask_img 생성
    mask_img = cv2.fillPoly(zero_img, w_mask, (255, 255, 255))
    mask_img = cv2.fillPoly(mask_img, h_mask, (0, 0, 0))
    # img와 mask_img의 and 연산으로 ROI 설정
    ROI_img = cv2.bitwise_and(img, mask_img)
    #    cv2.imshow('a', mask_img)
    return ROI_img


# draw rectangle
def draw_rectangle(img, lpos, rpos, offset=0):
    center = (lpos + rpos) / 2

    # 왼쪽 차선 표시 사각형
    cv2.rectangle(img, (lpos - 5, offset - 5),
                  (lpos + 5, offset + 5),
                  (0, 255, 0), 2)
    # 오른쪽 차선 표시 사각형
    cv2.rectangle(img, (rpos - 5, offset - 5),
                  (rpos + 5, offset + 5),
                  (0, 255, 0), 2)
    # 차선 가운데 지점 표시 사각형
    cv2.rectangle(img, (center - 5, offset - 5),
                  (center + 5, offset + 5),
                  (0, 255, 0), 2)
    # 화면 가운데 지점 표시 사각형
    cv2.rectangle(img, (Width / 2 - 5, offset - 5),
                  (Width / 2 + 5, offset + 5),
                  (0, 0, 255), 2)
    return img


# Gaussian Blur
def gaussain_blur(img, kernel_size, sigmaX=0):
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), sigmaX)


# White Detect
def white_detect(img, threshold):
    mark = np.copy(img)
    thresholds = (img[:, :] < threshold)
    mark[thresholds] = 0
    return mark


# Canny Edge
def canny(img, low_threshold, high_threshold):
    return cv2.Canny(img, low_threshold, high_threshold)


# Hough Transform
def hough_transform(img, rst_img, rho, theta, threshold, minLineLength, maxLineGap):
    lines = cv2.HoughLinesP(img, rho, theta, threshold, minLineLength, maxLineGap)
    for line in lines:
        cv2.line(rst_img, (line[0][0], line[0][1]), (line[0][2], line[0][3]), [255, 0, 0], 2)
    return lines, rst_img


# You are to find "left and light position" of road lanes
def process_image(frame):
    global Offset

    # 이진화
    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Gaussian Blur
    blur_img = gaussain_blur(gray_img, 5)
    # White Color Detection
    #    white = white_detect(blur_img, 200)
    # Canny Edge
    # 80, 160에서 중간에 Nonetype 에러 발생하지 않고 결승지점까지 완주
    canny_img = canny(blur_img, 80, 160)  # original: 80, 240
    #    canny_img1 = canny(blur_img, 60, 160)	# original: 80, 240
    #    canny_img2 = canny(blur_img, 70, 160)	# original: 80, 240
    #    canny_img3 = canny(blur_img, 90, 160)	# original: 80, 240
    #    canny_img4 = canny(blur_img, 100, 160)	# original: 80, 240
    #    canny_img5 = canny(blur_img, 80, 140)	# original: 80, 240
    #    canny_img6 = canny(blur_img, 80, 150)	# original: 80, 240
    #    canny_img7 = canny(blur_img, 80, 170)	# original: 80, 240
    canny_img8 = canny(blur_img, 80, 180)  # original: 80, 240
    canny_img9 = canny(blur_img, 60, 140)  # original: 80, 240
    canny_img10 = canny(blur_img, 70, 140)  # original: 80, 240
    canny_img11 = canny(blur_img, 60, 150)  # original: 80, 240
    # ROI 설정
    ROI_img = region_of_interest(canny_img, 35, 150)
    # Hough Transform
    hough_img = frame.copy()
    lines, hough_img = hough_transform(canny_img, frame, 1, np.pi / 180, 30, 0, np.pi / 2)

    # 기울기 구하기
    #    lines = np.squeeze(lines)
    #    print(lines)

    # lpos, rpos 계산하기
    lpos = 0
    rpos = 0
    for i in range(Width):
        if frame[Offset][i][0] == 255 and frame[Offset][i][1] == 0 and frame[Offset][i][2] == 0 and i < Width / 2 - 150:
            lpos = i
        if frame[Offset][i][0] == 255 and frame[Offset][i][1] == 0 and frame[Offset][i][2] == 0 and i > Width / 2 + 150:
            rpos = i
    #    print(lpos, rpos)

    #    cv2.imshow('white_img', white)
    #    cv2.imshow('canny_img', canny_img[Offset-35:Offset+35, ])
    #    cv2.imshow('canny1', canny_img1[Offset-35:Offset+35, ])
    #    cv2.imshow('canny2', canny_img2[Offset-35:Offset+35, ])
    #    cv2.imshow('canny3', canny_img3[Offset-35:Offset+35, ])
    #    cv2.imshow('canny4', canny_img4[Offset-35:Offset+35, ])
    #    cv2.imshow('canny5', canny_img5[Offset-35:Offset+35, ])
    #    cv2.imshow('canny6', canny_img6[Offset-35:Offset+35, ])
    #    cv2.imshow('canny7', canny_img7[Offset-35:Offset+35, ])
    cv2.imshow('canny8', canny_img8[Offset - 35:Offset + 35, ])
    cv2.imshow('canny9', canny_img9[Offset - 35:Offset + 35, ])
    cv2.imshow('canny10', canny_img10[Offset - 35:Offset + 35, ])
    cv2.imshow('canny11', canny_img11[Offset - 35:Offset + 35, ])
    #    cv2.imshow('hough_img', hough_img)

    frame = draw_rectangle(frame, lpos, rpos, offset=Offset)

    return (lpos, rpos), frame


def draw_steer(image, steer_angle):
    global Width, Height, arrow_pic

    arrow_pic = cv2.imread('steer_arrow.png', cv2.IMREAD_COLOR)

    origin_Height = arrow_pic.shape[0]
    origin_Width = arrow_pic.shape[1]
    steer_wheel_center = origin_Height * 0.74
    arrow_Height = Height / 2
    arrow_Width = (arrow_Height * 462) / 728

    matrix = cv2.getRotationMatrix2D((origin_Width / 2, steer_wheel_center), (steer_angle) * 1.5, 0.7)
    arrow_pic = cv2.warpAffine(arrow_pic, matrix, (origin_Width + 60, origin_Height))
    arrow_pic = cv2.resize(arrow_pic, dsize=(arrow_Width, arrow_Height), interpolation=cv2.INTER_AREA)

    gray_arrow = cv2.cvtColor(arrow_pic, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_arrow, 1, 255, cv2.THRESH_BINARY_INV)

    arrow_roi = image[arrow_Height: Height, (Width / 2 - arrow_Width / 2): (Width / 2 + arrow_Width / 2)]
    arrow_roi = cv2.add(arrow_pic, arrow_roi, mask=mask)
    res = cv2.add(arrow_roi, arrow_pic)
    image[(Height - arrow_Height): Height, (Width / 2 - arrow_Width / 2): (Width / 2 + arrow_Width / 2)] = res

    cv2.imshow('steer', image)


# You are to publish "steer_anlge" following load lanes
if __name__ == '__main__':
    cap = cv2.VideoCapture('kmu_track.mkv')
    time.sleep(3)

    while not rospy.is_shutdown():
        ret, image = cap.read()
        pos, frame = process_image(image)

        # center(두 차선의 중간 지점), angle(차선 중심과 화면 중앙 픽셀 차이), steer_angle 계산
        # 조향(steer_angle)범위는 좌우20도, 각도(angle)범위는 좌우50도, 조향범위 대 각도범위의 비 20:50의 비율 = 20/50 = 0.4
        center = (pos[0] + pos[1]) // 2
        angle = Width / 2 - center
        steer_angle = angle * 0.4  # 마이너스일 때 우회전, 플러스일 때 좌회전
        #	print("{} -> {}".format(angle, steer_angle))
        draw_steer(frame, steer_angle)

        if cv2.waitKey(3) & 0xFF == ord('q'):
            break
