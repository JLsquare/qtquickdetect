from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from pipeline.realtime_detection import RealtimeDetectionPipeline


class LiveResultWidget(QWidget):
    def __init__(self, live_url: str, model_path: str):
        super().__init__()
        self._pipeline = RealtimeDetectionPipeline(live_url, model_path)
        self._live_label = None
        self.init_ui()
        self.start()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        live_label = QLabel('Live loading...')
        self._live_label = live_label
        self._live_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._live_label.setFixedSize(640, 480)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(live_label)
        self.setLayout(layout)

    ##############################
    #         CONTROLLER         #
    ##############################

    def start(self):
        self._pipeline.progress_signal.connect(self.update_frame)
        self._pipeline.start()

    def update_frame(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img)
        self._live_label.setPixmap(pixmap.scaled(self._live_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def stop(self):
        self._pipeline.request_cancel()
        