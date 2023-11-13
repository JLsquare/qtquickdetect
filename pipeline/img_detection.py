from PyQt6.QtCore import QThread, pyqtSignal
from utils.file_handling import *
from utils.image_helpers import *
from models.app_state import AppState
import torch
import logging
import ultralytics
import ultralytics.engine.model
import ultralytics.engine.results
import cv2 as cv
import json
import urllib

appstate = AppState.get_instance()


class ImgDetectionPipeline(QThread):
    finished_signal = pyqtSignal(str, set) # Source file, data
    error_signal = pyqtSignal(str, Exception) # Source file, Exception

    '''
    Data format:
    {
        "classes": <dict of classes>,
        "model_name": <str>,
        "task": <str>,
        "results": [
            [
                "x1": <int>,
                "y1": <int>,
                "x2": <int>,
                "y2": <int>,
                "classid": <int>,
                "confidence": <float>
            ]
        ]
    }
    '''

    def __init__(self, inputs: list[str], model_path: str):
        """
        Pipeline class, used to run inference on a list of inputs

        :param inputs: List of input paths or URLs
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
        self._results = dict()

        model_name = os.path.basename(model_path)

        self._results['classes'] = self._names
        self._results['model_name'] = model_name
        self._results['task'] = "detection"
        self._results['results'] = []


    def run(self):
        """
        Runs a detection for all images in the input list
        """

        for src in self._inputs:
            try:
                result = self._model(src)

                result = result[0].cpu()

                results_array = []

                for box in result.boxes:
                    flat = box.xyxy.flatten()
                    topleft = (int(flat[0]), int(flat[1]))
                    bottomright = (int(flat[2]), int(flat[3]))
                    classid = int(box.cls)
                    conf = float(box.conf[0])  # It's a tensor [x]
                    
                    results_array.append({
                        'x1': topleft[0],
                        'y1': topleft[1],
                        'x2': bottomright[0],
                        'y2': bottomright[1],
                        'classid': classid,
                        'confidence': conf
                    })

                self._results['results'].append(results_array)

                results_json = json.dumps(self._results)
                print(results_json)

                self.finished_signal.emit(src, self._results)

            except Exception as e:
                self.error_signal.emit(src, e)
