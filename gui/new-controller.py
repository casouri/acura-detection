import json
import sys

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QHBoxLayout,
                             QLabel, QMainWindow, QMenu, QPushButton,
                             QTextEdit, QToolButton, QVBoxLayout, QWidget)

import cv2
import model


def import_config():
    """Import config from config file."""
    with open("config.json") as config_file:
        return json.load(config_file)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.resize(self.config["width"], self.config["height"])
        self.setWindowTitle("Detection")

    def init_ui(self):
        """Initialize UI."""
        # import config
        self.config = import_config()

        # menu bar
        main_menubar = self.menuBar()
        main_menubar.setNativeMenuBar(False)

        # main widget
        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)

        # file menu & actions
        # open doen't do anything now
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.main_widget.open_filename_dialog)
        open_action.setShortcut("Ctrl+O")  # actually command on Mac

        run_action = QAction("Run", self)
        run_action.triggered.connect(self.main_widget.run_video)

        file_menu = main_menubar.addMenu("&File")
        file_menu.addAction(open_action)
        file_menu.addAction(run_action)

        self.show()


class MainWidget(QWidget):
    """Main widget."""

    video_changed_signal = pyqtSignal(str)

    def __init__(self):
        """Init."""
        super().__init__()

        # path to the processing video
        self.video_path = ""

        # corresponding to four image box
        self.image_boxes = []

        # when change video with open_file_name_dialog
        # run change_video
        self.video_changed_signal.connect(self.change_video)

        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        # import config
        self.config = import_config()

        self.resize(self.config["width"], self.config["height"])

        self.textbox = QTextEdit(self)

        # layout is made up by three layers of boxes,
        # the lowest layer is hboxes, then above them is vboxes.
        # Above vboxes there is a single top box top_hbox
        self.image_hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.top_hbox = QHBoxLayout()

        self.vbox.addLayout(self.image_hbox)
        self.vbox.addStretch(0)
        self.vbox.addWidget(self.textbox)
        self.top_hbox.addLayout(self.vbox)

        for count in [0, 1, 2, 3]:
            self.image_boxes.append(
                ImageBox(self.config["default-image"], self))

        self.relayout()

    def change_video(self, video_path):
        self.video_path = video_path
        self.textbox.append("video changed to {}".format(video_path))

    def relayout(self):
        """Redraw the whole display."""
        self.setLayout(self.top_hbox)

    def open_filename_dialog(self):
        """Open a file explorer to open a file."""
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        # All Files (*);;
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            ".",
            "Images (*.png *.jpg *.jpeg)",
            options=options)
        self.video_changed_signal.emit(filename)
        return filename

    def log_text_change_image(self, text):
        """Print log imformation in text box."""
        for image_box in self.image_boxes:
            image_box.change_image_after_function()
        # debug
        self.textbox.append(text)

    def run_video(self):
        pass


class ImageBox():
    """Represents each image and their corresponding buttons as a box."""

    def __init__(self, path, parent_widget):
        self.parent_widget = parent_widget
        self.construct_box(path)
        parent_widget.image_hbox.addLayout(self.container_vbox)

    def array_to_image(self, array):
        """Convert an array to an QImage object."""
        height, width, channel = array.shape
        bytes_per_line = width * 3
        # format: http://doc.qt.io/qt-5/qimage.html#Format-enum
        return QImage(array.data, width, height, bytes_per_line,
                      QImage.Format_RGB888)

    def _read_image(self, path):
        """Read image into self.image."""
        # imread: https://docs.opencv.org/3.1.0/dc/d2e/tutorial_py_image_display.html
        # if user click "cancel" when selecting image
        # path is ""
        if path == "":
            return
        BGR_image = cv2.imread(path)
        # opencv loads image in BGR format
        # it seems opencv changed that
        # RGB_image = cv2.cvtColor(BGR_image, cv2.COLOR_BGR2RGB)
        # self.image = RGB_image
        self.image = BGR_image

    def construct_box(self, path):
        """Construct the layout boxes and buttons.

        Should be called only at first time.
        """
        self._read_image(path)
        self.label = QLabel(self.parent_widget)
        self.label.setPixmap(QPixmap(path))
        self.container_vbox = QVBoxLayout()
        self.container_vbox.addWidget(self.label)
        # parent_widget will open file brower and get file path
        # and call ImageBox.change_image(path)

    def change_image(self, path):
        """Change the displaying image.

        Should be used everytime user click change button and change a image.
        """
        self._read_image(path)
        self.change_image_after_function()

    def change_image_after_function(self):
        """Directly update image from self.images"""
        qimage = self.array_to_image(self.image)
        self.label.setPixmap(QPixmap(qimage))


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec_())
