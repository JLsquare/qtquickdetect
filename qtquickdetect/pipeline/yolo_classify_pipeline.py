import numpy as np
import torch

from ultralytics import YOLO
from ..models.preset import Preset
from ..pipeline.pipeline import Pipeline


class YoloClassifyPipeline(Pipeline):
    """Pipeline for classifying objects in images and videos using YoloV8."""

    def __init__(self, weight: str, preset: Preset, images_paths: list[str] | None, videos_paths: list[str] | None,
                 stream_url: str | None, results_path: str | None):
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
        Processes a single image with YoloV8 classification.

        :param image: The input image.
        :return: The processed image and the results array.
        """
        # Inference
        result = self.model(image, half=(self.device.type == 'cuda' and self.preset.half_precision),
                            verbose=False, iou=self.preset.iou_threshold)[0].cpu()

        results_array = []
        # add top 5 classes to results array
        for i in range(5):
            results_array.append({
                'classid': int(result.probs.top5[i]),
                'confidence': float(result.probs.top5conf[i])
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
            'task': "classification",
            'classes': list(self.model.names.values()),
            'results': results_array
        }
