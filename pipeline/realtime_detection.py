from PyQt6.QtCore import pyqtSignal, QThread
from utils.image_helpers import *
from models.app_state import AppState
from utils.media_fetcher import MediaFetcher
import logging
import ultralytics
import ultralytics.engine.model
import ultralytics.engine.results
import numpy as np

appstate = AppState.get_instance()


class RealtimeDetectionPipeline(QThread):
    progress_signal = pyqtSignal(np.ndarray)
    finished_signal = pyqtSignal(str, str)
    error_signal = pyqtSignal(str, Exception)

    def __init__(self, url: str, model_path: str):
        super().__init__()
        self._model = self.load_model(model_path)
        self._url = url
        self.fetcher = MediaFetcher(url, 60)
        self.fetcher.frame_signal.connect(self.process_frame)

    def request_cancel(self):
        """Public method to request cancellation of the process."""
        self.fetcher.request_cancel()

    def load_model(self, model_path) -> ultralytics.YOLO:
        try:
            model = ultralytics.YOLO(model_path).to(appstate.device)
            if model.task != 'detect':
                raise ValueError(f'Model task ({model.task}) does not match pipeline task')

            return model

        except Exception as e:
            logging.error(f'Failed to load model: {e}')
            raise e

    def run(self):
        self.fetcher.start()

    def process_frame(self, frame, frame_available):
        if frame_available:
            results = self._model(frame, verbose=False)[0].cpu()
            for box in results.boxes:
                flat = box.xyxy.flatten()
                topleft = (int(flat[0]), int(flat[1]))
                bottomright = (int(flat[2]), int(flat[3]))
                classname = self._model.names[int(box.cls)]
                conf = box.conf[0]

                config = appstate.config
                draw_bounding_box(frame, topleft, bottomright, classname, conf, config.video_box_color,
                                  config.video_text_color, config.video_box_thickness, config.video_text_size)
            self.progress_signal.emit(frame)
