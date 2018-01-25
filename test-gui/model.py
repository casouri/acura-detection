import cv2

# functions have to take 1st argument as a list of four image boxes
# you might need to convert back and forth between RGB and GRAYSCALE
# and preform actions on them
# and return a log string
# see examples


def threshold(image_boxes, threshold=177, max_value=255):
    print('thresholding')
    image = cv2.cvtColor(image_boxes[1].image, cv2.COLOR_RGB2GRAY)
    ret, threshold_result = cv2.threshold(image, threshold, max_value,
                                          cv2.THRESH_BINARY)
    image_boxes[2].image = cv2.cvtColor(threshold_result, cv2.COLOR_GRAY2RGB)
    return 'threshold done'


def canny(image_boxes, min_num=200, max_num=250):
    print('cannying')
    image = cv2.cvtColor(image_boxes[1].image, cv2.COLOR_RGB2GRAY)
    edge = cv2.Canny(image, min_num, max_num)
    image_boxes[2].image = cv2.cvtColor(edge, cv2.COLOR_GRAY2RGB)
    return 'canny done'


def face_recognition(arg1=None, arg2=None):
    return 'face recognition done'


def human_detection(arg1=None, arg2=None):
    return 'human detection done'
