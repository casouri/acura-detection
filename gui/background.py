import cv2
import matplotlib.pyplot as plt
import numpy as np
import copy


class BG_subtractor():
    def __init__(self, bg, bg_alpha=0.0001):
        """Return a background subtractor.
        
        Arguments:
        * bg (array): background image
        * bg_alpha: The background learning factor, its value should
        be between 0 and 1. The higher the value, the more quickly
        your program learns the changes in the background. Therefore, 
        for a static background use a lower value, like 0.001. But if 
        your background has moving trees and stuff, use a higher value,
        maybe start with 0.01. Default 0.001
        """
        self.alpha = bg_alpha
        self.bg = bg
        self.bg_model = bg
        self.fgbg = cv2.createBackgroundSubtractorMOG2()

    # def subtract2(self, img):
    #     self.bg_model = img * self.alpha + self.bg_model * (1 - self.alpha)

    #     threshold = 73
    #     max_value = 255
    #     shape = (5, 5)
    #     kernel = np.ones(shape, np.uint8)

    #     diff = cv2.absdiff(self.bg_model.astype(np.uint8), img)

    #     r, g, b = cv2.split(diff)

    #     combined = r + g + b

    #     ret, thresh_my = cv2.threshold(combined, threshold, max_value,
    #                                    cv2.THRESH_BINARY)

    #     dilation = cv2.dilate(thresh_my, kernel, iterations=2)
    #     erosion = cv2.erode(dilation, kernel, iterations=2)

    #     mask = erosion

    #     final_img = cv2.bitwise_or(img, img, mask=mask)

    #     return final_img

    # def subtract3(self, img):
    #     fgmask = self.fgbg.apply(img)

    #     final_img = cv2.bitwise_or(img, img, mask=fgmask)

    #     return final_img

    def subtract(self, img):
        """Subtract foreground from image by background.
        The one used currently.

        Arguments:
        * img (array): the image
        * bg (array_: the background)

        Return:
        array: the processed image
        """

        threshold = 225
        max_value = 225
        shape = (5, 5)

        kernel = np.array([[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [1, 1, 1, 1, 1],
                           [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0],
                           [0, 0, 1, 0, 0]], np.uint8)

        bg = self.bg

        # convert BGR to RGB
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)

        # convert RGB to LAB
        img = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        bg = cv2.cvtColor(bg, cv2.COLOR_RGB2LAB)

        sharp_img = img.copy()

        # blur
        img = cv2.GaussianBlur(img, shape, 0)
        bg = cv2.GaussianBlur(bg, shape, 0)

        # subtract
        front = cv2.absdiff(bg.astype(np.uint8), img)

        # combine channel
        r, g, b = cv2.split(front)
        combined = r + g + b

        # threshold
        ret, thresh_my = cv2.threshold(combined, threshold, max_value,
                                       cv2.THRESH_BINARY)

        # close holes
        dilation = cv2.dilate(thresh_my, kernel, iterations=2)

        # remove shadow
        erosion = cv2.erode(dilation, kernel, iterations=3)
        dilation2 = cv2.dilate(erosion, kernel, iterations=2)

        # mask
        mask = dilation2
        final_img = cv2.bitwise_or(sharp_img, sharp_img, mask=mask)

        return final_img

    def sub_lab(self, img):
        # original = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        original = copy.copy(img)
        bg = self.bg

        img = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        bg = cv2.cvtColor(bg, cv2.COLOR_RGB2LAB)


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
        # kernel = np.array([[0,1,0],
        #                   [1,1,1],
        #                   [1,1,1],
        #                   [0,1,0]], np.uint8)
        # closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        dilation = cv2.dilate(thresh,kernel,iterations = 3)
        erosion = cv2.erode(dilation,kernel,iterations = 3)
        # to kill pixel-small noises
        erosion2 = cv2.erode(erosion,kernel,iterations = 1)
        dilation2 = cv2.dilate(erosion2,kernel,iterations = 2)
        closing = dilation2

        #opening
        opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)

        # mask
        mask = opening
        final = cv2.bitwise_or(original, original, mask=mask)

        return final

