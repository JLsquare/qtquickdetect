import numpy as np

from collections import deque
from typing import Optional
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsScene, QGraphicsPixmapItem, QHBoxLayout, QPushButton
from ..models.preset import Preset
from ..pipeline.pipeline_manager import PipelineManager
from ..views.resizeable_graphics_widget import ResizeableGraphicsWidget


class StreamWidget(QWidget):
    """
    StreamWidget is a QWidget that displays the live stream from the specified URL, using the specified task and model.
    """
    def __init__(self, live_url: str, task: str, preset: Preset, models: dict[str, list[str]], return_to_main: callable):
        """
        Initializes the StreamWidget.

        :param live_url: The URL of the live stream.
        :param task: The task to perform on the live stream.
        :param preset: The selected preset.
        :param models: The selected models. (only one model is used)
        :param return_to_main: The function to call to return to the main view.
        """
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
        self._return_button: Optional[QPushButton] = None
        self._stats_layout: Optional[QVBoxLayout] = None
        self._main_layout: Optional[QHBoxLayout] = None

        self._timer: Optional[QTimer] = None
        self._live_url: str = live_url
        self._pipeline_manager: PipelineManager = PipelineManager(task, preset, models)
        self._frame_buffer: deque[np.ndarray] = deque(maxlen=30)
        self._buffer_rate: float = 1.0
        self._frame_update_count: int = 0
        self._real_fps: int = 0
        self._fps_timer: QTimer = QTimer(self)
        self._fps_timer.timeout.connect(self.calculate_real_fps)
        self._fps_timer.start(1000)
        self._return_to_main: callable = return_to_main

        self.init_ui()
        self.start()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self) -> None:
        """
        Initializes the user interface components.
        """
        self._container_widget = QWidget(self)
        self._container_layout = QHBoxLayout(self._container_widget)
        self._container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._scene = QGraphicsScene(self._container_widget)

        self._view = ResizeableGraphicsWidget(self._scene, self._container_widget)
        self._view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._container_layout.addWidget(self._view, 1)
        self._container_widget.setLayout(self._container_layout)

        self._stats_label = QLabel(self.tr('Live stats: '))
        self._real_fps_label = QLabel('FPS: 0')
        self._fetcher_fps_label = QLabel(self.tr('Fetcher FPS: 0'))
        self._buffer_size_label = QLabel(self.tr('Buffer Size: 0'))
        self._buffer_max_size_label = QLabel(f"{self.tr('Buffer Max Size')}: {self._frame_buffer.maxlen}")
        self._buffer_rate_label = QLabel(f"{self.tr('Buffer Rate')}: {self._buffer_rate}")
        self._return_button = QPushButton(self.tr('Return'))
        self._return_button.clicked.connect(self.return_to_main_view)

        self._stats_layout = QVBoxLayout()
        self._stats_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._stats_layout.addWidget(self._stats_label)
        self._stats_layout.addWidget(self._real_fps_label)
        self._stats_layout.addWidget(self._fetcher_fps_label)
        self._stats_layout.addWidget(self._buffer_size_label)
        self._stats_layout.addWidget(self._buffer_max_size_label)
        self._stats_layout.addWidget(self._buffer_rate_label)
        self._stats_layout.addWidget(self._return_button)

        self._main_layout = QHBoxLayout()
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._main_layout.addWidget(self._container_widget)
        self._main_layout.addLayout(self._stats_layout)
        self.setLayout(self._main_layout)

    ##############################
    #         CONTROLLER         #
    ##############################

    def start(self) -> None:
        """
        Start the pipeline and timer
        Set the timer to update frame at the rate of pipeline fps * buffer rate
        """
        self._pipeline_manager.finished_stream_frame_signal.connect(self.receive_frame)
        self._pipeline_manager.run_stream(self._live_url)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_frame)

    def receive_frame(self, frame: np.ndarray) -> None:
        """
        Receive frame from pipeline and add to buffer if buffer is not full, otherwise update the frame.
        Adjust the buffer rate according to the buffer size.

        :param frame: The frame received from the pipeline.
        """
        if not self._timer.isActive():
            self._timer.start(int(1000.0 / (self._pipeline_manager.current_pipeline.stream_fps * self._buffer_rate)))
        if len(self._frame_buffer) < 30:
            self._frame_buffer.append(frame)
        else:
            self.update_frame()
            self._frame_buffer.append(frame)
        self._buffer_rate = len(self._frame_buffer) / self._frame_buffer.maxlen
        self._timer.setInterval(int(1000.0 / (self._pipeline_manager.current_pipeline.stream_fps * self._buffer_rate)))

    def update_frame(self) -> None:
        """
        Update the frame in the buffer to the live label
        """
        if len(self._frame_buffer) == 0:
            return

        frame = self._frame_buffer.popleft()
        self._frame_update_count += 1

        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img)
        self.resize_and_add_pixmap(pixmap)

        self.update_info_label()

    def resize_and_add_pixmap(self, pixmap: QPixmap) -> None:
        """
        Resize the pixmap and add to the scene

        :param pixmap: The pixmap to add to the scene
        """
        view = self._scene.views()[0]
        view_size = view.size()

        scale_factor = min(view_size.width() / pixmap.width(), view_size.height() / pixmap.height())

        frame_item = QGraphicsPixmapItem(pixmap)
        frame_item.setScale(scale_factor)

        self._scene.clear()
        self._scene.addItem(frame_item)

    def stop(self) -> None:
        """
        Stop the pipeline and timer
        """
        self._pipeline_manager.request_cancel()
        self._timer.stop()
        self._fps_timer.stop()
        self._timer = None
        self._pipeline_manager = None
        self._fps_timer = None

    def calculate_real_fps(self) -> None:
        """
        Calculate the real fps
        """
        self._real_fps = self._frame_update_count
        self._frame_update_count = 0
        self.update_info_label()

    def update_info_label(self) -> None:
        """
        Update the info label
        """
        fetcher_fps = self._pipeline_manager.current_pipeline.stream_fps
        buffer_size = len(self._frame_buffer)
        self._real_fps_label.setText(f'FPS: {self._real_fps}')
        self._fetcher_fps_label.setText(f'Fetcher FPS: {fetcher_fps:.2f}')
        self._buffer_size_label.setText(f'Buffer Size: {buffer_size}')
        self._buffer_rate_label.setText(f'Buffer Rate: {self._buffer_rate:.2f}')

    def return_to_main_view(self) -> None:
        """
        Return to the main view
        """
        self.stop()
        self._return_to_main()
