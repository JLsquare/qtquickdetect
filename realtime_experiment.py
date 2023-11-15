from pipeline.realtime_detection import RealtimeDetectionPipeline
from PyQt6.QtCore import pyqtSignal, QThread, QMutex
from PyQt6.QtWidgets import QMainWindow, QApplication
import cv2 as cv

class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self._pipeline = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Test')
        self.setGeometry(100, 100, 480, 240)

        self._pipeline = RealtimeDetectionPipeline('http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4', 'yolov8x.pt')

        def show_img_signal_cb(img):
            cv.imshow('Test', img)
            cv.waitKey(1)

        self._pipeline.progress_signal.connect(show_img_signal_cb)
        self._pipeline.start()

        self.show()

if __name__ == '__main__':
    app = QApplication([])
    ex = TestApp()
    app.exec()