import cv2

import backend


class VideoProcessor:
    """An iterator that process video 
    and return message string.(for now)
    """

    def __init__(self,
                 video_path,
                 message_type="raw",
                 export="",
                 bg_alpha=0.001):
        """Return a video processor.
        
        Arguments:
        * video_path (str): the path to video file.
        * message_type (str): can be 'raw' or 'processed'. Default "raw"
        * export (str): If "", don't export, if not empty, export as filename.
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
        if export != "":
            self.writer = cv2.VideoWriter(export, fourcc, 20.0, (320, 200))
        self._get_background()
        self.backend = backend.Backend(self.background)

    def _get_background(self):
        """Set self.background and save it to current_bg.png."""
        # get background from the last frame
        # count = self.cap.get(1)
        # self.cap.set(1, count - 1)
        # normal process
        ret, frame = self.cap.read()
        cv2.imwrite("curren_bg.png", frame)
        self.background = frame
        # set frame back
        # self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def __iter__(self):
        return self

    def __next__(self):
        ret, frame = self.cap.read()
        if ret:
            return self.process_image(frame, self.message_type)
        else:
            raise StopIteration

    def process_image(self, image, message_type):
        self.backend.read(image)
        after_sub = self.backend.sub_lab()
        after_detect = self.backend.detect_human(after_sub)
        if self.export:
            self.writer.write(after_detect)
        # return "cool"


if __name__ == "__main__":
    # for num in range(1, 11):
    #     processor = VideoProcessor("video-%d.mp4" % num, "raw",
    #                                "output-lab-%d.mp4" % num)
    #     for message in processor:
    #         pass
    #         # print(message)

    processor = VideoProcessor("video-2.mp4", "raw", "output.mp4")
    for message in processor:
        pass
        # print(message)
