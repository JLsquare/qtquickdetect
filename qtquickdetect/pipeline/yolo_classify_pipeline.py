import numpy as np
import torch

from pathlib import Path
from ultralytics import YOLO
from ..utils.image_helpers import draw_classification_label
from ..models.preset import Preset
from ..pipeline.pipeline import Pipeline


class YoloClassifyPipeline(Pipeline):
    """Pipeline for classifying objects in images and videos using YoloV8."""

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
        Processes a single image with YoloV8 classification.

        :param image: The input image.
        :return: The processed image and the results array.
        """
        # Inference
        result = self.model(image, half=(self.device.type == 'cuda' and self.preset.half_precision),
                            verbose=False, iou=self.preset.iou_threshold)[0].cpu()

        top5_classe_ids = result.probs.top5
        top5_confidences = result.probs.top5conf
        top5_classe_names = [self.model.names[int(class_id)] for class_id in top5_classe_ids]

        results_array = []
        # add top 5 classes to results array
        for i in range(5):
            draw_classification_label(image, top5_classe_names[i], top5_confidences[i], self.preset.text_color, i)

            results_array.append({
                'classid': int(top5_classe_ids[i]),
                'confidence': float(top5_confidences[i])
            })

        return image, results_array

    def _make_results(self, results_array: list) -> dict:
        """
        Creates the results dictionary with YoloV8 specific information.

        :param results_array: The list of results.
        :return: The result's dictionary.
        """
        return {
            'model_name': 'Yolo',
            'weight': self.weight,
            'task': 'classification',
            'classes': list(self.model.names.values()),
            'results': results_array
        }
