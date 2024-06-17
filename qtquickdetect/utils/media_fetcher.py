import time
import cv2 as cv
import numpy as np


class MediaFetcher:
    """
    Class to fetch frames from a video stream, not on a separate thread, has a method to fetch the frame.
    """
    def __init__(self, url_or_device: str | int):
        """
        Initializes the MediaFetcher object.

        :param url_or_device: The URL of the video stream or the index of the webcam device.
        """
        self.cap = cv.VideoCapture(url_or_device)
        self.fps = self.cap.get(cv.CAP_PROP_FPS)
        self.last_fetch_time = None
        if not self.cap.isOpened():
            raise IOError(f"Failed to open stream: {url_or_device}")

    def fetch_frame(self) -> tuple[np.ndarray, bool]:
        """
        Fetches the latest frame from the stream.

        :return: The frame and a boolean indicating if the frame is available.
        """
        if self.cap is None or not self.cap.isOpened():
            raise ValueError("VideoCapture is not initialized or already released.")

        current_time = time.time()

        # Skip frames if necessary
        if self.last_fetch_time is not None:
            elapsed_time = current_time - self.last_fetch_time
            frame_interval = 1.0 / self.fps
            frames_to_skip = int(elapsed_time / frame_interval)
            for _ in range(frames_to_skip):
                self.cap.read()

        # Fetch the frame
        frame_available, frame = self.cap.read()

        self.last_fetch_time = time.time()
        return frame, frame_available

    def release(self) -> None:
        """
        Releases the VideoCapture object.
        """
        if self.cap:
            self.cap.release()
