import numpy as np
import cv2 as cv
import time

from PyQt6.QtCore import pyqtSignal, QThread


class ThreadedMediaFetcher(QThread):
    """Class to fetch frames from a video stream on a separate thread, emits a signal when a frame is fetched."""
    frame_signal = pyqtSignal(np.ndarray, bool) # Frame, is_frame_available

    def __init__(self, url: str, max_fps: float):
        """
        Initializes the ThreadedMediaFetcher.

        :param url: URL of the video stream.
        :param max_fps: Maximum FPS to fetch frames.
        """
        super().__init__()
        self._cancel_requested = False
        self.url = url
        self._max_fps = max_fps
        self._last_frame = None
        self.fps = 0.0

    def request_cancel(self):
        """Requests cancellation of the ongoing process."""
        self._cancel_requested = True

    def run(self):
        """Runs the media fetcher on a separate thread."""
        if self.url is None:
            return

        # Open the video stream and set the frame interval
        cap = cv.VideoCapture(self.url)
        self.fps = cap.get(cv.CAP_PROP_FPS)
        frame_interval = 1.0 / min(self.fps, self._max_fps)
        last_frame_time = time.time()

        # Fetch frames
        while not self._cancel_requested:
            frame_available, frame = cap.read()
            current_time = time.time()
            elapsed_since_last_frame = current_time - last_frame_time

            # Emit the frame if the frame interval has passed
            if elapsed_since_last_frame >= frame_interval:
                if frame_available:
                    self._last_frame = frame
                    self.frame_signal.emit(frame, True)
                elif self._last_frame is not None:
                    self.frame_signal.emit(self._last_frame, False)
                last_frame_time = current_time

            # Sleep to maintain the desired FPS
            time_to_wait = frame_interval - (time.time() - current_time)
            time.sleep(max(0.0, time_to_wait))

        # Release the video capture
        cap.release()
