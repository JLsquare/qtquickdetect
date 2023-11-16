from collections import deque
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from pipeline.realtime_detection import RealtimeDetectionPipeline
import logging


class LiveResultWidget(QWidget):
    def __init__(self, live_url: str, model_path: str):
        super().__init__()

        self._info_label = None
        self._live_label = None

        self._timer = None
        self._pipeline = RealtimeDetectionPipeline(live_url, model_path)
        self._frame_buffer = deque(maxlen=30)
        self._buffer_rate = 0.80

        self._frame_update_count = 0
        self._real_fps = 0
        self._fps_timer = QTimer(self)
        self._fps_timer.timeout.connect(self.calculate_real_fps)
        self._fps_timer.start(1000)

        self.init_ui()
        self.start()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        live_label = QLabel('Live loading...')
        live_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        live_label.setFixedSize(640, 480)
        self._live_label = live_label

        info_label = QLabel('FPS: 0, Buffer Size: 0, Buffer Rate: 0.80')
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._info_label = info_label

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(live_label)
        layout.addWidget(info_label)
        self.setLayout(layout)

    ##############################
    #         CONTROLLER         #
    ##############################

    def start(self):
        """
        Start the pipeline and timer
        Set the timer to update frame at the rate of pipeline fps * buffer rate
        """
        self._pipeline.progress_signal.connect(self.receive_frame)
        self._pipeline.start()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_frame)

    def receive_frame(self, frame):
        """
        Receive frame from pipeline and add to buffer if buffer is not full,
        otherwise update the frame.
        """
        if not self._timer.isActive():
            self._timer.start(int(1000.0 / (self._pipeline.fetcher.fps * self._buffer_rate)))
        if len(self._frame_buffer) < 30:
            self._frame_buffer.append(frame)
        else:
            self.update_frame()
            self._frame_buffer.append(frame)

    def update_frame(self):
        """
        Update the frame in the buffer to the live label
        """
        if len(self._frame_buffer) == 0:
            logging.debug('No frame in buffer')
            return

        frame = self._frame_buffer.popleft()
        self._frame_update_count += 1

        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img)
        self._live_label.setPixmap(pixmap.scaled(self._live_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

        self.update_info_label()

    def stop(self):
        """Stop the pipeline and timer"""
        self._pipeline.request_cancel()
        self._timer.stop()

    def calculate_real_fps(self):
        """Calculate the real fps"""
        self._real_fps = self._frame_update_count
        self._frame_update_count = 0
        self.update_info_label()

    def update_info_label(self):
        """Update the info label"""
        fetcher_fps = self._pipeline.fetcher.fps
        buffer_size = len(self._frame_buffer)
        self._info_label.setText(f'Real FPS: {self._real_fps}, Fetcher FPS: {fetcher_fps:.2f}, '
                                 f'Buffer Size: {buffer_size}, Buffer Rate: {self._buffer_rate:.2f}')
