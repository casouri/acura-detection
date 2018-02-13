import cv2


class VideoProcessor():
    """An iterator that process video 
and return message string.(for now)
"""

    def __init__(self, video_path, message_type="raw"):
        """Return a video processor.
        
        Arguments:
        * video_path (str): the path to video file.
        * message_type (str): can be 'raw' or 'processed'.
        """
        self.cap = cv2.VideoCapture(video_path)
        self.message_type = message_type

    def __iter__(self):
        return self

    def __next__(self):
        ret, frame = self.cap.read()
        if ret:
            return self.process_image(frame, self.message_type)
        else:
            raise StopIteration

    def process_image(self, image, message_type):
        return "cool"


# processor = VideoProcessor("video.mp4", "raw")
# for message in processor:
#     print(message)
