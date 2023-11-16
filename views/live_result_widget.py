from collections import deque
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsScene, QGraphicsPixmapItem, QHBoxLayout
from pipeline.realtime_detection import RealtimeDetectionPipeline
from views.resizeable_graphics_widget import ResizeableGraphicsWidget
import logging


class LiveResultWidget(QWidget):
    def __init__(self, live_url: str, model_path: str):
        super().__init__()

        self._buffer_size_label = None
        self._fetcher_fps_label = None
        self._real_fps_label = None
        self._scene = None
        self._info_label = None

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
        container_widget = QWidget(self)
        container_layout = QHBoxLayout(container_widget)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        scene = QGraphicsScene(container_widget)
        self._scene = scene

        view = ResizeableGraphicsWidget(scene, container_widget)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container_layout.addWidget(view, 1)
        container_widget.setLayout(container_layout)

        stats_label = QLabel('Live stats: ')
        real_fps_label = QLabel('FPS: 0')
        self._real_fps_label = real_fps_label
        fetcher_fps_label = QLabel(f'Fetcher FPS: 0')
        self._fetcher_fps_label = fetcher_fps_label
        buffer_size_label = QLabel('Buffer Size: 0')
        self._buffer_size_label = buffer_size_label
        buffer_max_size_label = QLabel(f'Buffer Max Size: {self._frame_buffer.maxlen}')
        buffer_rate_label = QLabel(f'Buffer Rate: {self._buffer_rate}')

        stats_layout = QVBoxLayout()
        stats_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        stats_layout.addWidget(stats_label)
        stats_layout.addWidget(real_fps_label)
        stats_layout.addWidget(fetcher_fps_label)
        stats_layout.addWidget(buffer_size_label)
        stats_layout.addWidget(buffer_max_size_label)
        stats_layout.addWidget(buffer_rate_label)

        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(container_widget)
        main_layout.addLayout(stats_layout)
        self.setLayout(main_layout)

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
