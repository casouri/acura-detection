import copy

import cv2
import matplotlib.pyplot as plt
import numpy as np


class Plotter:
    def __init__(self, row, colomn):
        self.shape = (row, colomn)

    def show_img(self, order, img, title=""):
        plt.subplot(*self.shape, order)
        plt.title(title)
        plt.axis("off")
        plt.imshow(img)

    def show_plot(self, order, plot, title=""):
        plt.subplot(*self.shape, order)
        plt.title(title)
        plt.plot(plot)

    def show_multi_plot(self, order, plot, title=""):
        plt.subplot(*self.shape, order)
        plt.title(title)
        plt.plot(*plot)


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


def last_nonzero(lis):
    return first_nonzero(lis.reversed())


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


def sub_lab(img, bg, export_path=""):
    original = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2LAB)

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
    # closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    dilation = cv2.dilate(thresh, kernel, iterations=3)
    erosion = cv2.erode(dilation, kernel, iterations=3)
    closing = erosion

    #opening
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)

    # for further operations
    mask = opening

    # canny
    canny = cv2.Canny(mask, 200, 250)

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

    # floodfill
    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    h, w = mask.shape[:2]
    mask_copy = copy.copy(mask)
    floodfill_mask = np.zeros((h + 2, w + 2), np.uint8)
    floodfill = cv2.floodFill(mask_copy, floodfill_mask, (0, 0), 255)

    # crop mask to normal size
    floodfill_mask = floodfill_mask * 255
    floodfill_mask = floodfill_mask[0:h, 0:w]
    floodfill_mask_inv = cv2.bitwise_not(floodfill_mask)

    # floodfill mask
    original3 = copy.copy(original)
    floodfill_final = cv2.bitwise_or(
        original3, original3, mask=floodfill_mask_inv)

    # super closing
    dilation = cv2.dilate(closing, kernel, iterations=6)
    erosion = cv2.erode(dilation, kernel, iterations=6)
    super_closing = erosion

    # mask
    # final = cv2.bitwise_or(original, original, mask=mask)
    final = cv2.bitwise_or(original, original, mask=super_closing)

    subplot_num = (6, 4)

    def show(order, img, title=""):
        plt.subplot(*subplot_num, order)
        plt.title(title)
        plt.axis("off")
        plt.imshow(img)

    def show_result():
        show(1, l, "L")
        show(2, a, "A")
        show(3, b, "B")
        # show(4, b, "B")

        show(5, bl, "L")
        show(6, ba, "A")
        show(7, bb, "B")

        show(9, sl, "L")
        show(10, sa, "A")
        show(11, sb, "B")
        show(12, canny, "Canny")

        show(13, thresh, "L thresh")
        show(14, closing, "L closing")
        show(15, opening, "L opening")
        show(16, final, "Mask")

        show(17, contour_mask, "Contour")
        show(18, contour_final, "Contour mask")
        show(19, floodfill_mask, "Floodfill")
        show(20, floodfill_final, "Floodfill mask")

        show(21, original4, "Convex hull")
        show(22, hull_final, "Convex hull mask")

        plt.show()

    # show_result()

    if export_path:
        cv2.imwrite(export_path, final)

    return final


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
    ret, thresh = cv2.threshold(rgb_sum, 50, 255, cv2.THRESH_TOZERO)
    # remove if over 200
    ret, thresh = cv2.threshold(thresh, 200, 255, cv2.THRESH_TOZERO_INV)

    # closing
    shape = (3, 3)
    kernel = np.ones(shape, np.uint8)
    # closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    dilation = cv2.dilate(thresh, kernel, iterations=3)
    erosion = cv2.erode(dilation, kernel, iterations=3)
    closing = erosion

    #opening
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)

    # mask
    mask = opening
    final = cv2.bitwise_or(original, original, mask=mask)

    subplot_num = (4, 4)

    def show(order, img, title=""):
        plt.subplot(*subplot_num, order)
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


def scan_left_right(img, human_height_threshold):
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

        length_before = nonzero_height_in_line_list[minus_within(index, 1, 0)]
        # length_5_before = nonzero_height_in_line_list[minus_within(
        #     index, 5, 0)]
        # length_5_after = nonzero_height_in_line_list[plus_within(index, 5, 0)]
        curve_around = [
            nonzero_height_in_line_list[idx]
            for idx in range(
                minus_within(index, 10, 0), plus_within(index, 10, width))
        ]

        # fix the cure to a second degree polynomio
        poly = np.poly1d(np.polyfit(range(len(curve_around)), curve_around, 2))
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
    list_of_left_side_of_body = np.subtract(list_of_left_side_of_body, PADDING)
    list_of_right_side_of_body = np.add(list_of_right_side_of_body, PADDING)

    #
    # 3: pack each two lines into a tuple that represent a body
    #

    # body_sides is a list of tuples of left and right position of each body
    if len(list_of_left_side_of_body) < len(list_of_right_side_of_body):
        body_sides = zip([0] + list_of_left_side_of_body,
                         list_of_right_side_of_body)
    elif len(list_of_left_side_of_body) > len(list_of_right_side_of_body):
        body_sides = zip(list_of_left_side_of_body,
                         list_of_right_side_of_body + [width])
    else:
        body_sides = zip(list_of_left_side_of_body, list_of_right_side_of_body)

    # so we can use it many times with out exhausting it (as iterator)
    body_sides = list(body_sides)

    #
    # 4: find upper left and down right of each body
    #

    body_coordinate_list = []

    for left, right in body_sides:
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


def scan_up_down(img, human_height_threshold):
    """Scan up to down to look for possible humans.

* Arguments:
* img (arraay): the image to scan through. Must be binary.
* human_height_threshold (tuple<int, int>): (min, max) Anything above the min and
under the max is considered human.
"""
    # horizontal line
    nonzero_length_in_line_list = np.count_nonzero(img, axis=1)


def detect_human(after_sub):
    mask = cv2.threshold(after_sub, 1, 255, cv2.THRESH_BINARY)[1]
    binary_mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)

    # draw boxes around image
    body_coordinate_list = scan_left_right(binary_mask, (100, 180))
    copy_img = copy.copy(after_sub)
    for pt1, pt2 in body_coordinate_list:
        cv2.rectangle(copy_img, pt1, pt2, (0, 255, 0), 2)

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
            cv2.rectangle(copy_img, pt1, pt2, (255, 0, 0), 1)

        all_component_list.append(component_list)

    return copy_img


def simple_sub(image, bg):
    front = image - bg
    plt.imshow(front)
    plt.show()


if __name__ == "__main__":

    IMG_PATH = 'image4.png'
    img = cv2.imread(IMG_PATH, 1)
    bg = cv2.imread("bg.png", 1)

    # detect_human((sub_lab(img, bg)))
    # sub_lab(img, bg, True)

    # for num in range(1, 5):
    #     img = cv2.imread("image%d.png" % num, 1)
    #     sub_lab(img, bg, "after_sub_%d.png" % num)

    simple_sub(img, bg)
