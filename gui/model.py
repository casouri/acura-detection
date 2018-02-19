import cv2

import background


class VideoProcessor:
    """An iterator that process video 
    and return message string.(for now)
    """

    def __init__(self,
                 video_path,
                 message_type="raw",
                 export=False,
                 bg_alpha=0.001):
        """Return a video processor.
        
        Arguments:
        * video_path (str): the path to video file.
        * message_type (str): can be 'raw' or 'processed'. Default "raw"
        * export (bool): whether to export prcessed video. Default "False"
        * bg_alpha: The background learning factor, its value should
	be between 0 and 1. The higher the value, the more quickly
	your program learns the changes in the background. Therefore, 
	for a static background use a lower value, like 0.001. But if 
	your background has moving trees and stuff, use a higher value,
	maybe start with 0.01. Default 0.001. Only need for subtract2.
        """
        self.cap = cv2.VideoCapture(video_path)
        self.message_type = message_type
        self.export = export
        fourcc = cv2.VideoWriter_fourcc(* "mp4v")
        self.writer = cv2.VideoWriter('output.mp4', fourcc, 20.0, (320, 200))
        self._get_background()
        self.bg_subtractor = background.BG_subtractor(self.background)

    def _get_background(self):
        # get background from the last frame
        count = self.cap.get(1)
        self.cap.set(1, count - 1)
        # normal process
        ret, frame = self.cap.read()
        self.background = frame
        # set frame back
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def __iter__(self):
        return self

    def __next__(self):
        ret, frame = self.cap.read()
        if ret:
            return self.process_image(frame, self.message_type)
        else:
            raise StopIteration

    def process_image(self, image, message_type):
        img = self.bg_subtractor.subtract(image)
        if self.export:
            self.writer.write(img)

        # use previous frame as background
        # self.background = image
        return "cool"


if __name__ == "__main__":
    processor = VideoProcessor("video.mp4", "raw", True)
    for message in processor:
        print(message)
