import numpy as np
import torch
import torchvision.transforms as T
import torchvision.models as models

from pathlib import Path
from ..models.preset import Preset
from ..pipeline.pipeline import Pipeline
from ..utils.image_helpers import draw_classification_label
from ..utils.filepaths import get_base_data_dir

CLASS_NAMES = models.DenseNet121_Weights.DEFAULT.meta['categories']


class TorchVisionClassifyPipeline(Pipeline):
    """
    Pipeline for classifying objects in images using TorchVision models with pre-trained weights.
    """

    def __init__(self, model_name: str, model_builder: str, weight: str, preset: Preset, images_paths: list[Path] | None,
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
        super().__init__(model_name, model_builder, weight, preset, images_paths, videos_paths, stream_url,
                         results_path)
        self.device = torch.device(self.preset.device)
        self.transform = T.Compose([T.ToTensor()])

        if weight in ['IMAGENET1K_V1', 'IMAGENET1K_V2', 'IMAGENET1K_SWAG_E2E_V1', 'IMAGENET1K_SWAG_LINEAR_V1']:
            self.model = getattr(models, model_builder)(weights=weight).to(self.device)
        else:  # Custom weights
            self.model = getattr(models, model_builder)(weights=None).to(self.device)
            self.model.load_state_dict(torch.load(get_base_data_dir() / 'weights' / weight))
        self.model.eval()

    def _process_image(self, image: np.ndarray) -> tuple[np.ndarray, list[dict]]:
        """
        Processes a single image with TorchVision classification.

        :param image: The input image.
        :return: The processed image and the results array.
        """
        # Preprocess image
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            predictions = self.model(image_tensor)[0].squeeze().softmax(0)

        top5_probs, top5_indices = torch.topk(predictions, 5)
        results_array = []
        # Process top 5 predictions
        for i in range(5):
            class_id = top5_indices[i].item()
            confidence = top5_probs[i].item()
            class_name = CLASS_NAMES[class_id]
            draw_classification_label(image, class_name, confidence, self.preset, i)

            results_array.append({
                'classid': class_id,
                'confidence': confidence
            })

        return image, results_array

    def _make_results(self, results_array: list) -> dict:
        """
        Creates the results dictionary with TorchVision specific information.

        :param results_array: The list of results.
        :return: The result's dictionary.
        """
        return {
            'pipeline': 'TorchVisionClassifyPipeline',
            'model_name': self.model_name,
            'model_builder': self.model_builder,
            'weight': self.weight,
            'task': 'classification',
            'classes': CLASS_NAMES,
            'results': results_array
        }
