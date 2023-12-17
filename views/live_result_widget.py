from collections import deque
from typing import Optional
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsScene, QGraphicsPixmapItem, QHBoxLayout
from models.project import Project
from pipeline.realtime_detection import RealtimeDetectionPipeline
from views.resizeable_graphics_widget import ResizeableGraphicsWidget
import logging


class LiveResultWidget(QWidget):
    def __init__(self, live_url: str, model_path: str, project: Project):
        super().__init__()

        # PyQT6 Components
        self._container_widget: Optional[QWidget] = None
        self._container_layout: Optional[QHBoxLayout] = None
        self._scene: Optional[QGraphicsScene] = None
        self._view: Optional[ResizeableGraphicsWidget] = None
        self._stats_label: Optional[QLabel] = None
        self._real_fps_label: Optional[QLabel] = None
        self._fetcher_fps_label: Optional[QLabel] = None
        self._buffer_size_label: Optional[QLabel] = None
        self._buffer_max_size_label: Optional[QLabel] = None
        self._buffer_rate_label: Optional[QLabel] = None
        self._stats_layout: Optional[QVBoxLayout] = None
        self._main_layout: Optional[QHBoxLayout] = None

        self._timer = None
        self._pipeline = RealtimeDetectionPipeline(live_url, model_path, project)
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
        self._container_widget = QWidget(self)
        self._container_layout = QHBoxLayout(self._container_widget)
        self._container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._scene = QGraphicsScene(self._container_widget)

        self._view = ResizeableGraphicsWidget(self._scene, self._container_widget)
        self._view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._container_layout.addWidget(self._view, 1)
        self._container_widget.setLayout(self._container_layout)

        self._stats_label = QLabel('Live stats: ')
        self._real_fps_label = QLabel('FPS: 0')
        self._fetcher_fps_label = QLabel(f'Fetcher FPS: 0')
        self._buffer_size_label = QLabel('Buffer Size: 0')
        self._buffer_max_size_label = QLabel(f'Buffer Max Size: {self._frame_buffer.maxlen}')
        self._buffer_rate_label = QLabel(f'Buffer Rate: {self._buffer_rate}')

        self._stats_layout = QVBoxLayout()
        self._stats_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._stats_layout.addWidget(self._stats_label)
        self._stats_layout.addWidget(self._real_fps_label)
        self._stats_layout.addWidget(self._fetcher_fps_label)
        self._stats_layout.addWidget(self._buffer_size_label)
        self._stats_layout.addWidget(self._buffer_max_size_label)
        self._stats_layout.addWidget(self._buffer_rate_label)

        self._main_layout = QHBoxLayout()
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._main_layout.addWidget(self._container_widget)
        self._main_layout.addLayout(self._stats_layout)
        self.setLayout(self._main_layout)

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
        Receive frame from pipeline and add to buffer if buffer is not full, otherwise update the frame.
        Adjust the buffer rate according to the buffer size.
        """
        if not self._timer.isActive():
            self._timer.start(int(1000.0 / (self._pipeline.fetcher.fps * self._buffer_rate)))
        if len(self._frame_buffer) < 30:
            self._frame_buffer.append(frame)
        else:
            self.update_frame()
            self._frame_buffer.append(frame)
        if len(self._frame_buffer) < 20 and self._buffer_rate > 0.5:
            self._buffer_rate -= 0.005
            self._timer.setInterval(int(1000.0 / (self._pipeline.fetcher.fps * self._buffer_rate)))
        elif len(self._frame_buffer) > 25 and self._buffer_rate < 0.95:
            self._buffer_rate += 0.005
            self._timer.setInterval(int(1000.0 / (self._pipeline.fetcher.fps * self._buffer_rate)))

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
        self.resize_and_add_pixmap(pixmap)

        self.update_info_label()

    def resize_and_add_pixmap(self, pixmap):
        view = self._scene.views()[0]
        view_size = view.size()

        scale_factor = min(view_size.width() / pixmap.width(), view_size.height() / pixmap.height())

        frame_item = QGraphicsPixmapItem(pixmap)
        frame_item.setScale(scale_factor)

        self._scene.clear()
        self._scene.addItem(frame_item)

    def stop(self):
        """Stop the pipeline and timer"""
        self._pipeline.request_cancel()
        self._timer.stop()
        self._fps_timer.stop()
        self._timer = None
        self._pipeline = None
        self._fps_timer = None

    def calculate_real_fps(self):
        """Calculate the real fps"""
        self._real_fps = self._frame_update_count
        self._frame_update_count = 0
        self.update_info_label()

    def update_info_label(self):
        """Update the info label"""
        fetcher_fps = self._pipeline.fetcher.fps
        buffer_size = len(self._frame_buffer)
        self._real_fps_label.setText(f'FPS: {self._real_fps}')
        self._fetcher_fps_label.setText(f'Fetcher FPS: {fetcher_fps:.2f}')
        self._buffer_size_label.setText(f'Buffer Size: {buffer_size}')
        self._buffer_rate_label.setText(f'Buffer Rate: {self._buffer_rate:.2f}')

