from typing import Callable
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

class ImgDetectionPipeline:
    def __init__(self, inputs: list[str], model_path: str):
        """
        Pipeline class, used to run inference on a list of inputs

        :param inputs: List of input paths or URLs
        :param model_path: Path to the model
        :raises Exception: If the model fails to load or if it's task does not match the pipeline task
        """

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
        
    def infer_each(self, cb_ok: Callable[[str, str], None], cb_err: Callable[[str, Exception], None]):
        """
        Runs a detection for all images in the input list
        :param cb_ok: Callback function `callback(input_path, output_media_path, output_json_path)`
        :param cb_err: Callback function `callback(input_media_path, exception)`
        """

        for src in self._inputs:
            try:
                # Check if src is a local file
                if src.startswith('http'):
                    # Download file
                    media = urllib.request.urlopen(src)
                    ext = src.split('.')[-1]
                    src = get_tmp_filepath('.' + ext)
                    with open(src, 'wb') as f:
                        f.write(media.read())

                result = self._model(src)

                result = result[0].cpu()

                opencv_img = cv.imread(src)
                json_result = []

                for box in result.boxes:
                    flat = box.xyxy.flatten()
                    topleft = (int(flat[0]), int(flat[1]))
                    bottomright = (int(flat[2]), int(flat[3]))
                    classname = self._names[int(box.cls)] # type: ignore
                    conf = box.conf[0] # It's a tensor [x]
                    json_result.append({'x1': topleft[0], 'y1': topleft[1], 'x2': bottomright[0], 'y2': bottomright[1], 'class': classname, 'confidence': conf.item()})

                    draw_bounding_box(opencv_img, topleft, bottomright, classname, conf, (0, 255, 0), 2)

                dst = get_tmp_filepath(f'.{appstate.config.image_format}')
                dst_json = get_tmp_filepath('.json')

                with open(dst_json, 'w') as json_file:
                    json.dump(json_result, json_file)

                cv.imwrite(dst, opencv_img)
                del opencv_img
                
                cb_ok(src, dst)

            except Exception as e:
                cb_err(src, e)

    

