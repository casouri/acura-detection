import numpy as np

import cv2

img1 = cv2.imread("./resource/delta0.JPG")
img2 = cv2.imread("./resource/delta3.JPG")
diff = cv2.absdiff(img1, img2)
mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
imask = mask > 0

canvas = np.zeros_like(img2, np.uint8)
canvas[imask] = img2[imask]
cv2.imwrite("./resource/result.png", canvas)
