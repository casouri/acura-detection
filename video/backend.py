import copy

import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde


def minus_within(num1, num2, min_):
    result = num1 - num2
    if result >= min_:
        return result
    else:
        return min_


def plus_within(num1, num2, max_):
    result = num1 + num2
    if result <= max_:
        return result
    else:
        return max_


class Backend():
    def __init__(self, bg):
        """Return a background subtractor.
        
        Arguments:
        * bg (array): background image
        """
        self.bg = bg
        self.bg_model = bg
        self.fgbg = cv2.createBackgroundSubtractorMOG2()

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
        # format mask so every pixel is wither 0 or 255
        ret, thresh = cv2.threshold(thresh, 10, 255, cv2.THRESH_BINARY)

        # closing
        shape = (3, 3)
        kernel = np.ones(shape, np.uint8)

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

        # Super closing

        dilation_super = cv2.dilate(mask, kernel, iterations=6)
        erosion_super = cv2.erode(dilation_super, kernel, iterations=6)
        mask = erosion_super

        self.bg_mask = mask

        # final
        final = cv2.bitwise_or(original, original, mask=mask)
        self.after_bg_sub = final

        return final

    def scan_left_right(self, img, human_height_threshold):
        """Scan left to right to look for possible humans.

    * Arguments:
    * img (arraay): the image to scan through. Must be binary.
    * human_height_threshold (tuple<int, int>): (min, max) Anything above the min and
    under the max is considered human.

    * Return:
    * (list): [((xmin, ymin), (xmax, ymax))] a list of coordinates marking 
    top left and down right of each body.
    """

        #
        # 1: get each line's height
        #

        # vertical line
        # amount of non zero pixels in each vertical_line
        nonzero_height_in_line_list = np.count_nonzero(img, axis=0)

        #
        # 2: get positions of lines with enough height
        #

        list_of_left_side_of_body = []
        list_of_right_side_of_body = []

        min_height, max_height = human_height_threshold
        width = len(nonzero_height_in_line_list)
        for index in range(0, width):
            length = nonzero_height_in_line_list[index]

            length_before = nonzero_height_in_line_list[minus_within(
                index, 1, 0)]
            # length_5_before = nonzero_height_in_line_list[minus_within(
            #     index, 5, 0)]
            # length_5_after = nonzero_height_in_line_list[plus_within(index, 5, 0)]
            curve_around = [
                nonzero_height_in_line_list[idx]
                for idx in range(
                    minus_within(index, 10, 0), plus_within(index, 10, width))
            ]

            # fix the cure to a second degree polynomio
            poly = np.poly1d(
                np.polyfit(range(len(curve_around)), curve_around, 2))
            deriv = poly.deriv()
            # direction > 0 means height increasing, opposite means decreasing
            direction = deriv(len(curve_around) / 2)

            if length < max_height:
                if length_before <= min_height and length >= min_height and direction > 0:
                    # increasing height
                    list_of_left_side_of_body.append(index)
                elif length_before >= min_height and length <= min_height and direction < 0:
                    # decreasing height
                    list_of_right_side_of_body.append(index)

            # remove positions that are too close to each other
            # between two left postion or two right position,
            # there should be at least 50 pixels
            tmp_list = copy.copy(list_of_left_side_of_body)
            list_of_left_side_of_body = []
            for index in range(0, len(tmp_list)):
                if not (index >= 1 and
                        (tmp_list[index] - tmp_list[index - 1]) < 50):
                    list_of_left_side_of_body.append(tmp_list[index])

            tmp_list = copy.copy(list_of_right_side_of_body)
            list_of_right_side_of_body = []
            for index in range(0, len(tmp_list)):
                if not (index >= 1 and
                        (tmp_list[index] - tmp_list[index - 1]) < 50):
                    list_of_right_side_of_body.append(tmp_list[index])

        # make the range wider between left and right
        # so more body can be coverd
        # be aware that this block should be out side the for loop above!
        PADDING = 5
        list_of_left_side_of_body = np.subtract(list_of_left_side_of_body,
                                                PADDING)
        list_of_right_side_of_body = np.add(list_of_right_side_of_body,
                                            PADDING)

        # make sure padding does exceed frame width
        for index in range(0, len(list_of_left_side_of_body)):
            if list_of_left_side_of_body[index] < 0:
                list_of_left_side_of_body[index] = 0
        for index in range(0, len(list_of_right_side_of_body)):
            if list_of_right_side_of_body[index] > width - 1:
                list_of_right_side_of_body[index] = width - 1
        #
        # 3: pack each two lines into a tuple that represent a body
        #

        # body_sides is a list of tuples of left and right position of each body
        # print(list_of_left_side_of_body)
        # print(list_of_right_side_of_body)
        if len(list_of_left_side_of_body) < len(list_of_right_side_of_body):
            body_sides = zip([0, *list_of_left_side_of_body],
                             list_of_right_side_of_body)
        elif len(list_of_left_side_of_body) > len(list_of_right_side_of_body):
            body_sides = zip(list_of_left_side_of_body,
                             [*list_of_right_side_of_body, 319])
        else:
            body_sides = zip(list_of_left_side_of_body,
                             list_of_right_side_of_body)

        # so we can use it many times with out exhausting it (as iterator)
        body_sides = list(body_sides)

        #
        # 4: find upper left and down right of each body
        #

        body_coordinate_list = []

        # print(body_sides)
        for left, right in body_sides:
            # guard against situations like [8,8]
            if right - left < 3:
                break
            # for each body
            xlist = []
            ylist = []
            # find all the coordinates of non zero pixels
            for x in range(left, right):
                # only colomns between left and right boundries
                for y in range(0, img.shape[0]):
                    if img[y, x] > 0:
                        xlist.append(x)
                        ylist.append(y)

            xmin = min(xlist)
            xmax = max(xlist)
            ymin = min(ylist)
            ymax = max(ylist)

            body_coordinate_list.append(((xmin, ymin), (xmax, ymax)))

        return body_coordinate_list

    def get_color(self, component_list, img):
        """Get dominant color in each region.

* Argument:
  * component_list (list): [((xmin, ymin), (xmax, ymax))]
  * img (array): original image
        
* Return:
  * (list): [head_dominant_color, body_dominant_color([R, G, B]), leg_dominant_color]
"""
        # get dominant color

        color_list = []
        # head, body, leg
        for part in component_list:
            ((xmin, ymin), (xmax, ymax)) = part
            pixel = np.array(img[ymin:ymax, xmin:xmax])

            # channels are in RGB format
            # get color clusters
            flat_pixel = np.float32(pixel.reshape((-1, 3)))
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10,
                        1.0)
            ret, label, center = cv2.kmeans(flat_pixel, 3, None, criteria, 10,
                                            cv2.KMEANS_PP_CENTERS)
            center = np.uint8(center)

            # get most repeated color
            unique, count = np.unique(label, return_counts=True)
            dominant_color = center[list(count).index(max(count))]

            color_list.append(list(dominant_color))

        return color_list

    def detect_human(self):
        """Detect human in image and return a message and processed image.

* Return:
  (tuple): (message, img)
        
* Message format:
[
  {
   "component": [head((xmin, ymin),(xmax, ymax)), body((xmin, ymin),(xmax, ymax)), leg((xmin, ymin),(xmax, ymax))],
   "color": (R, G, B),
   "position": (X, Y)
  },

  {another person},

  ...
]
"""
        binary_mask = self.bg_mask

        # dim background
        foreground = cv2.bitwise_or(self.img, self.img, mask=self.bg_mask)
        dimmed_bg = copy.copy(self.img)
        # stick foreground onto dimmed background
        for y in range(dimmed_bg.shape[0]):
            for x in range(dimmed_bg.shape[1]):
                pixel = foreground[y, x]
                if pixel.all(0):
                    dimmed_bg[y, x] = pixel
                else:
                    dimmed_bg[y, x] = np.int_(np.divide(dimmed_bg[y, x], 2))

        # self.img with blured background
        image = dimmed_bg

        # detect human
        body_coordinate_list = self.scan_left_right(binary_mask, (100, 180))
        # draw boxes around image
        for pt1, pt2 in body_coordinate_list:
            cv2.rectangle(image, pt1, pt2, (0, 255, 0), 2)

        # separate head, body and leg
        all_component_list = []
        for ((xmin, ymin), (xmax, ymax)) in body_coordinate_list:
            head_xmin, head_ymin = xmin, ymin
            head_xmax, head_ymax = xmax, round((ymax - ymin) / 6) + ymin

            body_xmin, body_ymin = xmin, head_ymax
            body_xmax, body_ymax = xmax, round((ymax - ymin) / 2) + ymin

            leg_xmin, leg_ymin = xmin, body_ymax
            leg_xmax, leg_ymax = xmax, ymax

            component_list = [((head_xmin, head_ymin), (head_xmax, head_ymax)),
                              ((body_xmin, body_ymin), (body_xmax, body_ymax)),
                              ((leg_xmin, leg_ymin), (leg_xmax, leg_ymax))]

            # draw components
            for pt1, pt2 in component_list:
                cv2.rectangle(image, pt1, pt2, (255, 0, 0), 1)

            all_component_list.append(component_list)

        # get color
        all_color_list = []
        for component in all_component_list:
            color_list = self.get_color(component, self.img)
            all_color_list.append(color_list)

        # draw color
        x = 20
        count = 0
        for color in all_color_list:
            # -1 means fill
            body_color = color[1]
            body_color = list(map(int, body_color))
            cv2.rectangle(image, (x * count, 0), (x * (count + 1), x),
                          body_color, -1)
            count += 1

        # get position
        all_position_list = []
        for component_list in all_component_list:
            ((leg_xin, leg_ymin), (leg_xmax, leg_ymax)) = component_list[2]
            position_x = (leg_xin + leg_xmax) / 2
            position_y = leg_ymax
            all_position_list.append((position_x, position_y))

        return_list = []
        for person in zip(body_coordinate_list, all_component_list,
                          all_color_list, all_position_list):
            return_list.append({
                "coordinate": person[0],
                "component": person[1],
                "color": person[2],
                "position": person[3]
            })

        return (image, return_list)
