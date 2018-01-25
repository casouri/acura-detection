import cv2


def process_video(video_path, callback_function, camera_id, gps_coordinate,
                  camera_angle, space, local_space, focus):
    """Process a video.

    Take a video and run through it to detect human interactions.

    * Arguments:
     * video_path (str): the path to the video file
     * call_back_function (object): the function to be called with generated messages and processed images
     * camera_id (int): the id of camera
     * gps_coordinate (tuple): a tuple contains the GPS coordinate of the camera
     * space (str): the location of the scene
     * local_space (str): the room at where the camera is
    """

    # videos in opencv https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_video_display/py_video_display.html
    capture = cv2.VideoCapture(video_path)
    while (capture.isOpened()):
        ret, frame = capture.read()

        # do stuff with the frame
        message = ""
        process_image(frame, message)

        callback_function(frame, message)


def process_image(image):
    pass
