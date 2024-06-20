import numpy as np
import torch
import torchvision.transforms as T
import torchvision.models as models

from pathlib import Path
from ..models.preset import Preset
from ..pipeline.pipeline import Pipeline
from ..utils.image_helpers import draw_keypoints


class TorchVisionPosePipeline(Pipeline):
    """
    Pipeline for posing persons in images using TorchVision models with pre-trained weights.
    """

    def __init__(self, model_builder: str, weight: str, preset: Preset, images_paths: list[Path] | None,
                 videos_paths: list[Path] | None, stream_url: str | None, results_path: Path | None):
        """
        Initializes the pipeline.

        :param weight: The weight to use.
        :param images_paths: List of image paths if processing images.
        :param videos_paths: List of video paths if processing videos.
        :param stream_url: URL of the video stream if processing a stream.
        :param results_path: Path to save the results if processing images or videos.
        :param preset: Project object.
        """
        super().__init__(model_builder, weight, preset, images_paths, videos_paths, stream_url, results_path)
        self.device = torch.device(self.preset.device)
        self.model = getattr(models, model_builder)(weights=weight).to(self.device)
        self.model.eval()
        self.transform = T.Compose([T.ToTensor()])

    def _process_image(self, image: np.ndarray) -> tuple[np.ndarray, list[dict]]:
        """
        Processes a single image with TorchVision posing.

        :param image: The input image.
        :return: The processed image and the results array.
        """
        # Preprocess image
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            predictions = self.model(image_tensor)[0]

        results_array = []
        keypoints = predictions['keypoints'].cpu().numpy()
        scores = predictions['scores'].cpu().numpy()
        # For each pose in the result
        for i in range(len(keypoints)):
            if scores[i] < self.preset.iou_threshold:
                continue

            xy = [(int(keypoint[0]), int(keypoint[1])) for keypoint in keypoints[i]]
            draw_keypoints(image, xy, self.preset)

            results_array.append({
                'xy': xy,
                'confidence': float(scores[i])
            })

        return image, results_array

    def _make_results(self, results_array: list) -> dict:
        """
        Creates the results dictionary with TorchVision specific information.

        :param results_array: The list of results.
        :return: The result's dictionary.
        """
        return {
            'model_name': 'TorchVision',
            'weight': self.weight,
            'task': 'pose',
            'classes': ['person'],
            'results': results_array
        }
