import matplotlib.pyplot as plt

import cv2

IMG_PATH = 'small.png'
img = cv2.imread(IMG_PATH, 0)
bg = cv2.imread("bg.png", 0)

threshold = 73
maxValue = 225
shape = (5, 5)

# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

diff = cv2.absdiff(img, bg)
# mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
imask = diff > 0

blur = cv2.GaussianBlur(img, shape, 0)

ret, thresh1 = cv2.threshold(blur, threshold, maxValue, cv2.THRESH_BINARY_INV)

plt.subplot(221)
plt.imshow(blur)
plt.subplot(222)
plt.imshow(thresh1)
plt.subplot(223)
plt.hist(blur)
plt.subplot(224)
plt.imshow(imask)
plt.show()
