from PyQt6.QtCore import pyqtSignal, QThread, QMutex
from utils.image_helpers import *
from models.app_state import AppState
import torch
import logging
import ultralytics
import ultralytics.engine.model
import ultralytics.engine.results
import cv2 as cv
import time
import numpy as np

appstate = AppState.get_instance()

mutex = QMutex()
frame_available = False
video_frame = None

class MediaFetcher(QThread):
    quit_signal = pyqtSignal()

    def __init__(self, url: str):
        super().__init__()
        self._url = url

        self.quit_signal.connect(self.quit)

    def run(self):
        global frame_available
        global video_frame

        cap = cv.VideoCapture(self._url)
        fps = cap.get(cv.CAP_PROP_FPS)
        last_frame_time = time.time()

        while True:
            mutex.lock()
            frame_available, video_frame = cap.read()
            mutex.unlock()

            if frame_available:
                elapsed = time.time() - last_frame_time
                time.sleep(max(0, 1 / fps - elapsed))

                last_frame_time = time.time()

class RealtimeDetectionPipeline(QThread):
    progress_signal = pyqtSignal(np.ndarray) # TODO: DEFINE SIGNALS SIGNATURES
    finished_signal = pyqtSignal(str, str)
    error_signal = pyqtSignal(str, Exception)

    def __init__(self, url: str, model_path: str):
        """
        Pipeline class, used to run inference on a realtime stream

        :param url: stream url
        :param model_path: Path to the model
        :raises Exception: If the model fails to load or if it's task does not match the pipeline task
        """

        super().__init__()
        model = None
        device = appstate.device

        try:
            model = ultralytics.YOLO(model_path).to(device)
        except Exception as e:
            logging.error('Failed to load model: {}'.format(e))
            raise e

        if model.task != 'detect':
            logging.error('Model task ({}) does not match pipeline task'.format(model.task))
            raise ValueError('Model task ({}) does not match pipeline task'.format(model.task))

        self._names = model.names
        self._model: ultralytics.engine.model.Model = model
        self._device: torch.device = device
        self._url = url

    def run(self):
        """
        Launches the inference process, and calls back with 
        """

        self._fetcher = MediaFetcher(self._url)
        self._fetcher.start()

        global frame_available
        global video_frame

        while True:
            if frame_available:
                mutex.lock()
                if not frame_available:
                    mutex.unlock()
                    time.sleep(0.001) # Dirty hack to avoid busy waiting
                    continue

                frame = video_frame.copy()
                frame_available = False
                mutex.unlock()

                results = self._model(frame)[0].cpu()
                for box in results.boxes:
                    flat = box.xyxy.flatten()
                    topleft = (int(flat[0]), int(flat[1]))
                    bottomright = (int(flat[2]), int(flat[3]))
                    classname = self._names[int(box.cls)]
                    conf = box.conf[0]

                    config = appstate.config
                    draw_bounding_box(frame, topleft, bottomright, classname, conf, config.video_box_color,
                                        config.video_text_color, config.video_box_thickness, config.video_text_size)
                self.progress_signal.emit(frame)
