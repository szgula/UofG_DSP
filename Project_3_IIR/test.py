import numpy as np
import cv2
import screeninfo
from time import sleep, time
import matplotlib.pyplot as plt
MIN_WAIT_TIME = 20

sc = screeninfo.get_monitors()[0]
height, width = sc.height, sc.width
red, green, blue = np.zeros((height,width,3), np.uint8), np.zeros((height,width,3), np.uint8), np.zeros((height,width,3), np.uint8)
blue[:, :] = (255,0,0)
red[:, :] = (0,0,255)
green[:, :] = (0,255,0)

cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cap = cv2.VideoCapture(0)

cv2.imshow('image', red)
for _ in range(10): cv2.waitKey(MIN_WAIT_TIME)

f_l = 1280
f_h = 720
mean_cam = np.zeros((3, 240, 428, 3))
r, g, b = [], [], []

for _ in range(3):
    for idx, img in enumerate((red, green, blue)):
        cv2.imshow('image', img)
        cv2.waitKey(MIN_WAIT_TIME)
        s_time = time()
        for i in range(60):
            #cv2.waitKey(1)
            ret, frame = cap.read()
            if ret:
                ret = False
                mean_cam[idx] += frame[f_h//3:f_h - f_h//3, f_l//3:f_l - f_l//3]
                r.append(frame[f_h//2, f_l//2, 0])
                g.append(frame[f_h // 2, f_l//2, 1])
                b.append(frame[f_h // 2, f_l//2, 2])
            #print(img[0,0])
            print(f's_time {time() - s_time}')

first_iter = mean_cam[0].mean(axis=0).mean(axis=0)
second_iter = mean_cam[1].mean(axis=0).mean(axis=0)
third_iter = mean_cam[2].mean(axis=0).mean(axis=0)
add = np.array([first_iter, second_iter, third_iter])

print(add)
plt.plot(r)
plt.plot(b)
plt.plot(g)
cap.release()
cv2.destroyAllWindows()
