from PyQt6.QtCore import pyqtSignal, QThread, QRunnable, QThreadPool, QObject
from utils.image_helpers import *
from models.app_state import AppState
from utils.media_fetcher import MediaFetcher
from utils.model_loader import load_model
import numpy as np

appstate = AppState.get_instance()


class FrameProcessorSignals(QObject):
    """Signals for the FrameProcessor class who can't inherit from QThread."""
    finished = pyqtSignal(np.ndarray)


class FrameProcessor(QRunnable):
    """Processes a single frame from a video stream asynchronously."""
    def __init__(self, frame, model):
        super().__init__()
        self._frame = frame
        self._model = model
        self.signals = FrameProcessorSignals()

    def run(self):
        """Runs the model on the frame and emits the result."""
        results = self._model(self._frame, verbose=False)[0].cpu()

        for box in results.boxes:
            flat = box.xyxy.flatten()
            topleft = (int(flat[0]), int(flat[1]))
            bottomright = (int(flat[2]), int(flat[3]))
            classname = self._model.names[int(box.cls)]
            conf = box.conf[0]

            config = appstate.config
            draw_bounding_box(self._frame, topleft, bottomright, classname, conf, config.video_box_color,
                              config.video_text_color, config.video_box_thickness, config.video_text_size)

        self.signals.finished.emit(self._frame)


class RealtimeDetectionPipeline(QThread):
    """Pipeline for performing detection on a video stream."""
    progress_signal = pyqtSignal(np.ndarray)
    finished_signal = pyqtSignal(str, str)
    error_signal = pyqtSignal(str, Exception)

    def __init__(self, url: str, model_path: str):
        super().__init__()
        self._model = load_model(model_path)
        self._url = url
        self._is_processing = False
        self._thread_pool = QThreadPool()
        self.fetcher = MediaFetcher(url, 60)
        self.fetcher.frame_signal.connect(self.process_frame)

    def request_cancel(self):
        """Public method to request cancellation of the process."""
        self.fetcher.request_cancel()

    def run(self):
        """Starts the video stream and waits for frames to be processed."""
        self.fetcher.start()

    def process_frame(self, frame, frame_available):
        """Try to process a frame if it's available and we're not already processing one."""
        if frame_available and not self._is_processing:
            self._is_processing = True
            processor = FrameProcessor(frame, self._model)
            processor.signals.finished.connect(self.on_frame_processed)
            self._thread_pool.start(processor)

    def on_frame_processed(self, processed_frame):
        """Callback for when a frame has been processed."""
        self.progress_signal.emit(processed_frame)
        self._is_processing = False
