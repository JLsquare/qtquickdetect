import logging

import numpy as np
import torch

from pathlib import Path
from ultralytics import YOLO
from ..models.preset import Preset
from ..pipeline.pipeline import Pipeline
from ..utils.image_helpers import draw_bounding_box, generate_color, draw_keypoints


class YoloPosePipeline(Pipeline):
    """Pipeline for detecting objects in images and videos using YoloV8."""

    def __init__(self, weight: str, preset: Preset, images_paths: list[Path] | None, videos_paths: list[Path] | None,
                 stream_url: str | None, results_path: Path | None):
        """
        Initializes the pipeline.

        :param weight: The weight file path to use.
        :param images_paths: List of image paths if processing images.
        :param videos_paths: List of video paths if processing videos.
        :param stream_url: URL of the video stream if processing a stream.
        :param results_path: Path to save the results if processing images or videos.
        :param preset: Project object.
        """
        super().__init__(weight, preset, images_paths, videos_paths, stream_url, results_path)
        self.device = torch.device(self.preset.device)
        self.model = YOLO(weight).to(self.device)

    def _process_image(self, image: np.ndarray) -> tuple[np.ndarray, list[dict]]:
        """
        Processes a single image with YoloV8 detection.

        :param image: The input image.
        :return: The processed image and the results array.
        """
        # Inference
        result = self.model(image, half=(self.device.type == 'cuda' and self.preset.half_precision),
                            verbose=False, iou=self.preset.iou_threshold)[0].cpu()

        results_array = []
        # For each box in the result
        for pose in result:
            # Draw keypoints
            xy = [(int(xy[0]), int(xy[1])) for xy in pose.keypoints[0].xy[0]]
            draw_keypoints(image, xy, generate_color(0), 3)

            results_array.append({
                'xy': xy,
                'confidence': np.mean([float(conf) for conf in pose.keypoints[0].conf[0]])
            })

        return image, results_array

    def _make_results(self, results_array: list) -> dict:
        """
        Creates the results dictionary with YoloV8 specific information.

        :param results_array: The list of results.
        :return: The results dictionary.
        """
        return {
            'model_name': 'Yolo',
            'weight': self.weight,
            'task': 'pose',
            'classes': list(self.model.names.values()),
            'results': results_array
        }
