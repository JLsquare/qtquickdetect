from PyQt6.QtCore import pyqtSignal, QThread
import numpy as np
import cv2 as cv
import time


class MediaFetcher(QThread):
    frame_signal = pyqtSignal(np.ndarray, bool)

    def __init__(self, url: str, max_fps: float):
        super().__init__()
        self._cancel_requested = False
        self._url = url
        self._max_fps = max_fps
        self._last_frame = None
        self.fps = 0.0

    def request_cancel(self):
        self._cancel_requested = True

    def run(self):
        if self._url is None:
            return
        cap = cv.VideoCapture(self._url)
        self.fps = cap.get(cv.CAP_PROP_FPS)
        frame_interval = 1.0 / min(self.fps, self._max_fps)
        last_frame_time = time.time()

        while not self._cancel_requested:
            frame_available, frame = cap.read()
            current_time = time.time()
            elapsed_since_last_frame = current_time - last_frame_time

            if elapsed_since_last_frame >= frame_interval:
                if frame_available:
                    self._last_frame = frame
                    self.frame_signal.emit(frame, True)
                elif self._last_frame is not None:
                    self.frame_signal.emit(self._last_frame, False)
                last_frame_time = current_time

            time_to_wait = frame_interval - (time.time() - current_time)
            time.sleep(max(0.0, time_to_wait))

        cap.release()
