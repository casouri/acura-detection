import numpy as np

import cv2

IMG_PATH = ''
# image needs to be binary
img = cv2.imread(IMG_PATH, 0)

shape = (5, 5)
kernel = np.ones(shape, np.uint8)
erosion = cv2.erode(img, kernel, iterations=1)
dilation = cv2.dilate(img, kernel, iterations=1)
# erosion + dilation
opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
# dilation + erosion
closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
# difference between dilation and erosion
gradient = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
