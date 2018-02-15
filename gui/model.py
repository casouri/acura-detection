import background
import cv2


class VideoProcessor():
    """An iterator that process video 
    and return message string.(for now)
    """

    def __init__(self, video_path, message_type="raw", export=False):
        """Return a video processor.
        
        Arguments:
        * video_path (str): the path to video file.
        * message_type (str): can be 'raw' or 'processed'.
        """
        self.cap = cv2.VideoCapture(video_path)
        self.message_type = message_type
        self.export = export
        fourcc = cv2.VideoWriter_fourcc(* "mp4v")
        self.writer = cv2.VideoWriter('output.mp4', fourcc, 20.0, (320, 200))
        self.bg_sub = background.subtract
        self._get_background()

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
        img = self.bg_sub(image, self.background)
        if self.export:
            self.writer.write(img)

        # use previous frame as background
        # self.background = image
        return "cool"


if __name__ == "__main__":
    processor = VideoProcessor("video.mp4", "raw", True)
    for message in processor:
        print(message)
