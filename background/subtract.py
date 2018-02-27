import cv2
import matplotlib.pyplot as plt
import numpy as np
import copy

IMG_PATH = 'image1.png'
img = cv2.imread(IMG_PATH, 1)
bg = cv2.imread("bg.png", 1)

def sub1():
    threshold = 73
    maxValue = 225
    shape = (5, 5)

    kernel = np.ones(shape, np.uint8)

    # convert BGR to RGB
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)

    # convert BGR to LAB
    img = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    bg = cv2.cvtColor(bg, cv2.COLOR_RGB2LAB)

    # blur
    img = cv2.GaussianBlur(img, shape, 0)
    bg = cv2.GaussianBlur(bg, shape, 0)

    # subtract
    front = img - bg

    # combine channel
    r, g, b = cv2.split(front)
    combined = r + g + b

    # threshold
    ret, thresh_my = cv2.threshold(combined, threshold, maxValue,
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


def sub_lab(img, bg):
    original = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2LAB)


    # split color
    l, a, b = cv2.split(img)
    bl, ba, bb = cv2.split(bg)

    # subtract bg
    sl = l - bl
    sa = a - ba
    sb = b - bb

    # I found that noises from chairs and shadow
    # are strangly over 230, and background noises
    # are under 20

    # threshold
    # remove if under 20
    ret,thresh = cv2.threshold(sl,40,255,cv2.THRESH_TOZERO)
    # remove if over 230
    ret,thresh = cv2.threshold(thresh,230,255,cv2.THRESH_TOZERO_INV)

    # closing
    shape = (3, 3)
    kernel = np.ones(shape, np.uint8)
    # closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    dilation = cv2.dilate(thresh,kernel,iterations = 3)
    erosion = cv2.erode(dilation,kernel,iterations = 3)
    closing = erosion

    #opening
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)


    # mask
    mask = opening
    final = cv2.bitwise_or(original, original, mask=mask)


    subplot_num = (5,3)

    def show(order, img, title=""):
        plt.subplot(* subplot_num, order)
        plt.title(title)
        plt.axis("off")
        plt.imshow(img)

    show(1, l, "L")
    show(2, a, "A")
    show(3, b, "B")
    show(4, bl, "L")
    show(5, ba, "A")
    show(6, bb, "B")
    show(7, sl, "L")
    show(8, sa, "A")
    show(9, sb, "B")
    show(10, thresh, "L thresh")
    show(11, closing, "L closing")
    show(12, opening, "L opening")
    show(13, final, "Mask")
    plt.show()


def sub_rgb(img, bg):
    original = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)


    # split color
    r, g, b = cv2.split(img)
    br, bg, bb = cv2.split(bg)

    # subtract bg
    sr = r - br
    sg = g - bg
    sb = b - bb

    rgb_sum = np.add(sb, np.add(sr, sg))

    # threshold
    # remove if under 50
    ret,thresh = cv2.threshold(rgb_sum,50,255,cv2.THRESH_TOZERO)
    # remove if over 200
    ret,thresh = cv2.threshold(thresh,200,255,cv2.THRESH_TOZERO_INV)

    # closing
    shape = (3, 3)
    kernel = np.ones(shape, np.uint8)
    # closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    dilation = cv2.dilate(thresh,kernel,iterations = 3)
    erosion = cv2.erode(dilation,kernel,iterations = 3)
    closing = erosion

    #opening
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)


    # mask
    mask = opening
    final = cv2.bitwise_or(original, original, mask=mask)


    subplot_num = (4,4)

    def show(order, img, title=""):
        plt.subplot(* subplot_num, order)
        plt.title(title)
        plt.axis("off")
        plt.imshow(img)

    show(1, r, "R")
    show(2, g, "G")
    show(3, b, "B")
    # show(4, b, "B")

    show(5, br, "R")
    show(6, bg, "G")
    show(7, bb, "B")
    # show(8, bb, "B")

    show(9, sr, "R")
    show(10, sg, "G")
    show(11, sb, "B")
    show(12, rgb_sum, "SUM")

    show(13, thresh, "thresh")
    show(14, closing, "closing")
    show(15, opening, "opening")
    show(16, final, "Mask")
    plt.show()

if __name__ == "__main__":
    sub_rgb(img, bg)
