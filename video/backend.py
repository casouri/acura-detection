import copy

import cv2
import matplotlib.pyplot as plt
import numpy as np


class Backend():
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

    def read(self, img):
        self.img = img

    def sub_lab(self):
        img = copy.copy(self.img)

        # original = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        original = copy.copy(img)
        bg = self.bg

        img = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        bg = cv2.cvtColor(bg, cv2.COLOR_RGB2LAB)

        # split color
        l, a, b = cv2.split(img)
        bl, ba, bb = cv2.split(bg)

        # subtract bg
        # sl = l - bl
        # sa = a - ba
        # sb = b - bb

        sl = cv2.absdiff(l, bl)
        sa = cv2.absdiff(a, ba)
        sb = cv2.absdiff(b, bb)

        # I found that noises from chairs and shadow
        # are strangly over 230, and background noises
        # are under 20

        # threshold
        # remove if under 20
        ret, thresh = cv2.threshold(sl, 40, 255, cv2.THRESH_TOZERO)
        # remove if over 230
        ret, thresh = cv2.threshold(thresh, 230, 255, cv2.THRESH_TOZERO_INV)

        # closing
        shape = (3, 3)
        kernel = np.ones(shape, np.uint8)
        # kernel = np.array([[0,1,0],
        #                   [1,1,1],
        #                   [1,1,1],
        #                   [0,1,0]], np.uint8)

        # closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        dilation = cv2.dilate(thresh, kernel, iterations=3)
        erosion = cv2.erode(dilation, kernel, iterations=3)
        # to kill pixel-small noises
        erosion2 = cv2.erode(erosion, kernel, iterations=1)
        dilation2 = cv2.dilate(erosion2, kernel, iterations=2)
        closing = dilation2

        #opening
        opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)

        # mask for further operations
        mask = opening

        #
        # Method 1: contour & convex hull
        #

        # contour
        # only return the most out side contours
        im2, contour, hierarchy = cv2.findContours(opening, cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_SIMPLE)
        original2 = copy.copy(original)
        h, w = mask.shape[:2]
        contour_mask = np.zeros((h, w), np.uint8)
        #                               all contour found
        #                                    v
        cv2.drawContours(contour_mask, contour, -1, (255), cv2.FILLED)
        #                                          ^         ^
        #                                        green   thickness

        #contour convex hull
        original4 = copy.copy(original)
        original5 = copy.copy(original)
        h, w = mask.shape[:2]
        hull_mask = np.zeros((h, w), np.uint8)
        for cnt in contour:
            hull = cv2.convexHull(cnt)
            cv2.drawContours(original4, [hull], -1, (0, 255, 0), 2)
            cv2.drawContours(hull_mask, [hull], -1, (255), cv2.FILLED)

        # contour mask
        contour_final = cv2.bitwise_or(original2, original2, mask=contour_mask)
        hull_final = cv2.bitwise_or(original5, original5, mask=hull_mask)

        #
        # Method2: Super closing
        #

        # kernel = np.array([[0,1,1,1,0],
        #                    [1,1,1,1,1],
        #                    [1,1,1,1,1],
        #                    [0,1,1,1,0]], np.uint8)
        # kernel = np.ones((10,10), np.uint8)

        dilation_super = cv2.dilate(mask, kernel, iterations=6)
        erosion_super = cv2.erode(dilation_super, kernel, iterations=6)
        mask = erosion_super

        self.mask = mask

        # final
        final = cv2.bitwise_or(original, original, mask=mask)
        self.after_bg_sub = final

        return final
        # return hull_final


    def find_human(self):
        img = self.after_bg_sub

        # contour
        # only return the most out side contours
        im2, contour, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_SIMPLE)
        # original2 = copy.copy(original)
        # h, w = mask.shape[:2]
        # contour_mask = np.zeros((h, w), np.uint8)
        # #                               all contour found
        # #                                    v
        # cv2.drawContours(contour_mask, contour, -1, (255), cv2.FILLED)
        # #                                          ^         ^
        # #                                        green   thickness

        # #contour convex hull
        # original4 = copy.copy(original)
        # original5 = copy.copy(original)
        # h, w = mask.shape[:2]
        # hull_mask = np.zeros((h, w), np.uint8)
        # for cnt in contour:
        #     hull = cv2.convexHull(cnt)
        #     cv2.drawContours(original4, [hull], -1, (0, 255, 0), 2)
        #     cv2.drawContours(hull_mask, [hull], -1, (255), cv2.FILLED)

