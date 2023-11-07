import torch
import logging
import ultralytics
import ultralytics.engine.model
import ultralytics.engine.results
from typing import List, Callable, Any
import os
import random
import cv2 as cv

from utils.file_handling import *
from utils.image_helpers import *

class ImgDetectionPipeline:
    def __init__(self, inputs: List[str], model_path: str):
        """
        Pipeline class, used to run inference on a list of inputs

        :param inputs: List of input paths
        :param model_path: Path to the model
        :raises Exception: If the model fails to load or if it's task does not match the pipeline task
        """

        device = torch.device('cpu')
        model = None     

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
        
    def infer_each(self, cb_ok, cb_err):
        """
        Runs a detection for all images in the input list
        :param callback_ok: Callback function `callback(input_path, output_media_path)`
        :param callback_err: Callback function `callback(input_media_path, exception)`
        """

        for src in self._inputs:
            try:
                result = self._model(src)

                result = result[0].cpu()
                json = result.tojson()

                opencv_img = cv.imread(src)

                for box in result.boxes:
                    flat = box.xyxy.flatten()
                    topleft = (int(flat[0]), int(flat[1]))
                    bottomright = (int(flat[2]), int(flat[3]))
                    classname = self._names[int(box.cls)] # type: ignore
                    conf = box.conf[0] # It's a tensor [x]

                    draw_bounding_box(opencv_img, topleft, bottomright, classname, conf, (0, 255, 0), 2)

                dst = get_tmp_filepath('.png')

                cv.imwrite(dst, opencv_img)
                del opencv_img
                
                cb_ok(src, dst)

            except Exception as e:
                cb_err(src, e)

    

