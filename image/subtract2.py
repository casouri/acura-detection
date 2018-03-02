import matplotlib.pyplot as plt
import numpy as np

import cv2

IMG_PATH = 'image2.png'
img = cv2.imread(IMG_PATH, 1)
bg = cv2.imread("bg.png", 1)

threshold = 73
maxValue = 225
shape = (5, 5)

kernel = np.ones(shape, np.uint8)

# convert BGR to RGB
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)

# blur
img = cv2.GaussianBlur(img, shape, 0)
bg = cv2.GaussianBlur(bg, shape, 0)

#separate channel
ir, ig, ib = cv2.split(img)
bgr, bgg, bgb = cv2.split(bg)

# subtract
fr, fg, fb = abs(ir - bgr), abs(ig - bgg), abs(ib - bgb)

# combine channel
combined = fr + fg + fb
front = cv2.merge([fr, fg, fb])
front_gray = cv2.cvtColor(front, cv2.COLOR_RGB2GRAY)

# threshold
ret, thresh_my = cv2.threshold(front_gray, threshold, maxValue,
                               cv2.THRESH_BINARY)

# close holes
dilation = cv2.dilate(thresh_my, kernel, iterations=2)
erosion = cv2.erode(dilation, kernel, iterations=2)

# remove shadow
erosion2 = cv2.erode(dilation, kernel, iterations=5)
dilation2 = cv2.dilate(erosion2, kernel, iterations=3)

# mask
final_img = cv2.bitwise_or(img, img, mask=dilation2)

plt.subplot(231)
plt.title("original")
plt.imshow(img)
plt.subplot(232)
plt.title("subtraction")
plt.imshow(front)
plt.subplot(233)
plt.title("threshold")
plt.imshow(thresh_my)
plt.subplot(234)
plt.title("remove hole")
plt.imshow(erosion)
plt.subplot(235)
plt.title("remove shadow")
plt.imshow(dilation2)
plt.subplot(236)
plt.title("mask")
plt.imshow(final_img)
plt.show()
