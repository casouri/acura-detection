import cv2
import matplotlib.pyplot as plt
import numpy as np

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
# img = cv2.GaussianBlur(img, shape, 0)
# bg = cv2.GaussianBlur(bg, shape, 0)

# create MOG2 object
fgbg = cv2.createBackgroundSubtractorMOG2()

# subtract
fgmask = fgbg.apply(img)

# mask
final_img = cv2.bitwise_or(img, img, mask=fgmask)

plt.subplot(221)
plt.title("original")
plt.imshow(img)
plt.subplot(222)
plt.title("subtraction")
plt.subplot(223)
plt.imshow(fgmask)
plt.title("mask")
plt.imshow(final_img)
plt.show()
