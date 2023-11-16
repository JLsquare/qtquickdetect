from pipeline.realtime_detection import RealtimeDetectionPipeline
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

        self._pipeline = RealtimeDetectionPipeline('https://cdn.flowplayer.com/a30bd6bc-f98b-47bc-abf5-97633d4faea0/hls/de3f6ca7-2db3-4689-8160-0f574a5996ad/playlist.m3u8', 'yolov8x.pt')

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