import numpy as np
import torch
import torchvision.transforms as T
import torchvision.models as models
import cv2 as cv

from pathlib import Path
from ..models.preset import Preset
from ..pipeline.pipeline import Pipeline
from ..utils.image_helpers import draw_segmentation_mask_from_points, generate_color

# COCO classes used for TorchVision models
# https://pytorch.org/vision/0.9/models.html#object-detection-instance-segmentation-and-person-keypoint-detection
CLASS_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
    'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
    'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
    'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
    'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]


class TorchVisionSegmentPipeline(Pipeline):
    """Pipeline for segmenting objects in images and videos using TorchVision models with pre-trained weights."""

    def __init__(self, weight: str, preset: Preset, images_paths: list[Path] | None, videos_paths: list[Path] | None,
                 stream_url: str | None, results_path: Path | None):
        """
        Initializes the pipeline.

        :param images_paths: List of image paths if processing images.
        :param videos_paths: List of video paths if processing videos.
        :param stream_url: URL of the video stream if processing a stream.
        :param results_path: Path to save the results if processing images or videos.
        :param preset: Project object.
        """
        super().__init__(weight, preset, images_paths, videos_paths, stream_url, results_path)
        self.device = torch.device(self.preset.device)
        self.model = getattr(models.detection, weight)(pretrained=True).to(self.device)
        self.model.eval()
        self.transform = T.Compose([T.ToTensor()])

    def _process_image(self, image: np.ndarray) -> tuple[np.ndarray, list[dict]]:
        """
        Processes a single image with TorchVision detection and segmentation.

        :param image: The input image.
        :return: The processed image and the results array.
        """
        # Inference
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            predictions = self.model(image_tensor)[0]

        results_array = []
        for i in range(len(predictions['labels'])):
            box = predictions['boxes'][i].cpu().numpy()
            label = int(predictions['labels'][i])
            score = predictions['scores'][i].item()
            if score < 0.5:
                continue

            # Extract mask
            mask = predictions['masks'][i, 0].cpu().numpy()
            mask = mask > 0.5

            # Extract polygon from mask
            contours, _ = cv.findContours((mask * 255).astype(np.uint8), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            polygons = [contour.astype(np.float32).squeeze(axis=1).tolist() for contour in contours]
            polygon = max(polygons, key=lambda x: len(x))

            # Draw segmentation mask
            if self.preset.segment_color_per_class:
                segment_color = generate_color(label)
            else:
                segment_color = self.preset.segment_color
            draw_segmentation_mask_from_points(image, polygon, segment_color, self.preset.segment_thickness)

            # Append the box to the results array
            results_array.append({
                'x1': int(box[0]),
                'y1': int(box[1]),
                'x2': int(box[2]),
                'y2': int(box[3]),
                'mask': polygon,
                'classid': label,
                'confidence': score,
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
            'task': 'segmentation',
            'classes': CLASS_NAMES,
            'results': results_array
        }
