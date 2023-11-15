from PyQt6.QtCore import pyqtSignal, QThread
from utils.image_helpers import *
from models.app_state import AppState
import torch
import logging
import ultralytics
import ultralytics.engine.model
import ultralytics.engine.results
import cv2 as cv
import os
import json

appstate = AppState.get_instance()


class VidDetectionPipeline(QThread):
    progress_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(str, str, str)
    error_signal = pyqtSignal(str, Exception)

    def __init__(self, inputs: list[str], model_path: str, results_path: str):
        """
        Pipeline class, used to run inference on a list of inputs

        :param inputs: List of input paths
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
        self._inputs = inputs
        self._results_path = results_path
        self._results = dict()

        model_name = os.path.basename(model_path)

        self._results['model_name'] = model_name
        self._results['task'] = "detection"
        self._results['classes'] = self._names
        self._results['results'] = []

    def run(self):
        """
        Runs a detection for all videos in the input list
        """

        for src in self._inputs:
            try:
                video_name = os.path.basename(src)
                output = os.path.join(self._results_path, video_name)

                cap = cv.VideoCapture(src)
                width, height, fps, frame_count = int(cap.get(cv.CAP_PROP_FRAME_WIDTH)), int(
                    cap.get(cv.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv.CAP_PROP_FPS)), int(
                    cap.get(cv.CAP_PROP_FRAME_COUNT))
                if appstate.config.video_format == 'avi':
                    codec = 'XVID'
                else:
                    codec = 'mp4v'
                writer = cv.VideoWriter(output, cv.VideoWriter_fourcc(*codec), fps, (width, height))
                frame_index = 0

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # Inference
                    results = self._model(frame)[0].cpu()

                    results_array = []

                    for box in results.boxes:
                        flat = box.xyxy.flatten()
                        topleft = (int(flat[0]), int(flat[1]))
                        bottomright = (int(flat[2]), int(flat[3]))
                        classid = int(box.cls)
                        classname = self._names[classid]
                        conf = float(box.conf[0])

                        config = appstate.config
                        draw_bounding_box(frame, topleft, bottomright, classname, conf, config.video_box_color,
                                          config.video_text_color, config.video_box_thickness, config.video_text_size)

                        results_array.append({
                            'x1': topleft[0],
                            'y1': topleft[1],
                            'x2': bottomright[0],
                            'y2': bottomright[1],
                            'classid': classid,
                            'confidence': conf
                        })

                    self._results['results'].append(results_array)

                    writer.write(frame)
                    frame_index += 1
                    self.progress_signal.emit(frame_index, frame_count)

                cap.release()
                writer.release()

                json_name = os.path.basename(src).split('.')[0] + '.json'
                json_path = os.path.join(self._results_path, json_name)

                with open(json_path, 'w') as f:
                    json.dump(self._results, f, indent=4)

                self.finished_signal.emit(src, output, json_path)

            except Exception as e:
                self.error_signal.emit(src, e)
