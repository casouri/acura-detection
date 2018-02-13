import cv2

# TODO gaussian filtering
# TODO matplotlib histogram

IMG_PATH = ''
img = cv2.imread(IMG_PATH, 0)

#
# threshold
#

# img gray scale array
# doc: https://docs.opencv.org/3.0-beta/modules/imgproc/doc/miscellaneous_transformations.html?highlight=threshold#threshold
# tutorial: https://docs.opencv.org/3.0-beta/doc/tutorials/imgproc/threshold/threshold.html?highlight=threshold

img = cv2.imread(IMG_PATH, 0)
threshold = 177
maxValue = 225

ret, thresh1 = cv2.threshold(img, threshold, maxValue, cv2.THRESH_BINARY)
ret, thresh2 = cv2.threshold(img, threshold, maxValue, cv2.THRESH_BINARY_INV)
ret, thresh3 = cv2.threshold(img, threshold, maxValue, cv2.THRESH_TRUNC)
ret, thresh4 = cv2.threshold(img, threshold, maxValue, cv2.THRESH_TOZERO)
ret, thresh5 = cv2.threshold(img, threshold, maxValue, cv2.THRESH_TOZERO_INV)

#
# adaptive threshold
#

# doc: https://docs.opencv.org/3.0-beta/modules/imgproc/doc/miscellaneous_transformations.html?highlight=adaptivethreshold#cv2.adaptiveThreshold
'''
src – Source 8-bit single-channel image.
dst – Destination image of the same size and the same type as src .
maxValue – Non-zero value assigned to the pixels for which the condition is satisfied. See the details below.
adaptiveMethod – Adaptive thresholding algorithm to use, ADAPTIVE_THRESH_MEAN_C or ADAPTIVE_THRESH_GAUSSIAN_C . See the details below.
thresholdType – Thresholding type that must be either THRESH_BINARY or THRESH_BINARY_INV .
blockSize – Size of a pixel neighborhood that is used to calculate a threshold value for the pixel: 3, 5, 7, and so on.
bias – Constant subtracted from the mean or weighted mean (see the details below). Normally, it is positive but may be zero or negative as well.
'''

img = cv2.imread(IMG_PATH, 0)
threshold = 177
maxValue = 225
blockSize = 11
bias = 2

ret, th1 = cv2.threshold(img, threshold, maxValue, cv2.THRESH_BINARY)
th2 = cv2.adaptiveThreshold(img, maxValue, cv2.ADAPTIVE_THRESH_MEAN_C,
                            cv2.THRESH_BINARY, blockSize, bias)
th3 = cv2.adaptiveThreshold(img, maxValue, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                            cv2.THRESH_BINARY, blockSize, bias)
#
# Otsu’s Binarization
#

img = cv2.imread(IMG_PATH, 0)
maxValue = 225

ret2, th2 = cv2.threshold(img, 0, maxValue,
                          cv2.THRESH_BINARY + cv2.THRESH_OTSU)
