import torch
import logging
import ultralytics
import ultralytics.engine.model
import ultralytics.engine.results
from typing import List
import cv2 as cv

from utils.file_handling import *
from utils.image_helpers import *
from models.app_state import AppState

appstate = AppState.get_instance()

class VidDetectionPipeline:
    def __init__(self, inputs: List[str], model_path: str):
        """
        Pipeline class, used to run inference on a list of inputs

        :param inputs: List of input paths
        :param model_path: Path to the model
        :raises Exception: If the model fails to load or if it's task does not match the pipeline task
        """

        device = appstate.device

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
        
    def infer_each(self, cb_frame, cb_ok, cb_err):
        """
        Runs a detection for all videos in the input list

        :param cb_frame: Callback function `callback(current_frame, total_frames)`
            where current_frame is the current frame number and total_frames is the total number of frames in the video
        :param cb_ok: Callback function `callback(input_path, output_media_path)` called when a video is successfully processed
        :param cb_err: Callback function `callback(input_media_path, exception)` called when a video fails to process
        """

        for src in self._inputs:
            try:
                output = get_tmp_filepath(f'.{appstate.config.video_format}')

                cap = cv.VideoCapture(src)
                width, height, fps, frame_count = int(cap.get(cv.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv.CAP_PROP_FPS)), int(cap.get(cv.CAP_PROP_FRAME_COUNT))
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

                    for box in results.boxes:
                        flat = box.xyxy.flatten()
                        topleft = (int(flat[0]), int(flat[1]))
                        bottomright = (int(flat[2]), int(flat[3]))
                        classname = self._names[int(box.cls)]
                        conf = box.conf[0]

                        draw_bounding_box(frame, topleft, bottomright, classname, conf, (0, 255, 0), 2)

                    writer.write(frame)
                    frame_index += 1
                    cb_frame(frame_index, frame_count)

                cap.release()
                writer.release()

                cb_ok(src, output)

            except Exception as e:
                cb_err(src, e)

    

