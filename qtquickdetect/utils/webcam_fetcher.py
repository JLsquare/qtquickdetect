import time
import cv2 as cv
import numpy as np


class WebcamFetcher:
    """
    Class to fetch frames from a webcam stream.
    """
    def __init__(self, device_index: int):
        """
        Initializes the WebcamFetcher object.

        :param device_index: The index of the webcam device.
        """
        self.cap = cv.VideoCapture(device_index)
        self.fps = self.cap.get(cv.CAP_PROP_FPS)
        self.last_fetch_time = None
        if not self.cap.isOpened():
            raise IOError(f"Failed to open webcam device: {device_index}")

    def fetch_frame(self) -> tuple[np.ndarray, bool]:
        """
        Fetches the latest frame from the webcam.

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
