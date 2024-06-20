import numpy as np
import torch

from pathlib import Path
from ultralytics import YOLO
from ..models.preset import Preset
from ..pipeline.pipeline import Pipeline
from ..utils.image_helpers import draw_keypoints
from ..utils.filepaths import get_base_data_dir


class YoloPosePipeline(Pipeline):
    """
    Pipeline for posing persons in images and videos using YoloV8.
    """

    def __init__(self, model_name: str, model_builder: str, weight: str, preset: Preset, images_paths: list[Path] | None,
                 videos_paths: list[Path] | None, stream_url: str | None, results_path: Path | None):
        """
        Initializes the pipeline.

        :param weight: The weight file path to use.
        :param images_paths: List of image paths if processing images.
        :param videos_paths: List of video paths if processing videos.
        :param stream_url: URL of the video stream if processing a stream.
        :param results_path: Path to save the results if processing images or videos.
        :param preset: Project object.
        """
        super().__init__(model_name, model_builder, weight, preset, images_paths, videos_paths, stream_url,
                         results_path)
        self.device = torch.device(self.preset.device)
        self.model = YOLO(get_base_data_dir() / 'weights' / weight).to(self.device)

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
        # For each pose in the result
        for pose in result:
            # Draw keypoints
            xy = [(int(xy[0]), int(xy[1])) for xy in pose.keypoints[0].xy[0]]
            draw_keypoints(image, xy, self.preset)

            results_array.append({
                'xy': xy,
                'confidence': np.mean([float(conf) for conf in pose.keypoints[0].conf[0]])
            })

        return image, results_array

    def _make_results(self, results_array: list) -> dict:
        """
        Creates the results dictionary with YoloV8 specific information.

        :param results_array: The list of results.
        :return: The result's dictionary.
        """
        return {
            'pipeline': 'YoloPosePipeline',
            'model_name': self.model_name,
            'model_builder': self.model_builder,
            'weight': self.weight,
            'task': 'pose',
            'classes': ['person'],
            'results': results_array
        }
