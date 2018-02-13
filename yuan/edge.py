import cv2

IMG_PATH = ''
img = cv2.imread(IMG_PATH, 0)

# canny
# image, threshhold 1, threshhold 2
min_num = 200
max_num = 250
edges = cv2.Canny(img, min_num, max_num)
