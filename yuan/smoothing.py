import cv2
import numpy as np

IMG_PATH = ''
img = cv2.imread(IMG_PATH, 0)

#
# 2D Convolution
#

# doc: https://docs.opencv.org/3.0-beta/modules/imgproc/doc/filtering.html?highlight=filter2d#filter2d
# what is ddepth?

img = cv2.imread(IMG_PATH, 0)
shape = (5, 5)
dataType = np.float32
kernel = np.ones(shape, dataType) / 25
dst = cv2.filter2D(img, -1, kernel)

#
# blur
#

img = cv2.imread(IMG_PATH, 0)
shape = (5, 5)

blur = cv2.blur(img, shape)

#
# Gaussian Filtering
#

# doc: https://docs.opencv.org/3.0-beta/modules/imgproc/doc/filtering.html?highlight=gaussianblur#void%20GaussianBlur(InputArray%20src,%20OutputArray%20dst,%20Size%20ksize,%20double%20sigmaX,%20double%20sigmaY,%20int%20borderType)

# what is that 0?

img = cv2.imread(IMG_PATH, 0)
shape = (5, 5)

blur = cv2.GaussianBlur(img, shape, 0)

#
# Median Filtering: salt and pepper noise
#

# doc: https://docs.opencv.org/3.0-beta/modules/imgproc/doc/filtering.html?highlight=gaussianblur#void%20medianBlur(InputArray%20src,%20OutputArray%20dst,%20int%20ksize)

median = cv2.medianBlur(img, 5)

#
# Bilateral Filtering: remove texture but keeps edge
#

# https://docs.opencv.org/3.0-beta/modules/imgproc/doc/filtering.html?highlight=gaussianblur#cv2.bilateralFilter

diameter = 9
sigmaColor = 75
sigmaSpace = 75

blur = cv2.bilateralFilter(img, diameter, sigmaColor, sigmaSpace)
