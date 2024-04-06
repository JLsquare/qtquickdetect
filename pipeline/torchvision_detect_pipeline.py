import numpy as np
import torch
import torchvision.transforms as T
from torchvision.models.detection import fasterrcnn_resnet50_fpn, maskrcnn_resnet50_fpn, retinanet_resnet50_fpn, ssd300_vgg16, ssdlite320_mobilenet_v3_large
from pipeline.pipeline import Pipeline
from utils.image_helpers import draw_bounding_box

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


class TorchVisionDetectPipeline(Pipeline):
    """Pipeline for detecting objects in images and videos using TorchVision models with pre-trained weights."""

    def __init__(self, weight: str, images_paths: list[str] | None = None, videos_paths: list[str] | None = None,
                 stream_url: str | None = None, results_path: str | None = None, project = None):
        """
        Initializes the pipeline.

        :param weight: The weight to use.
        :param images_paths: List of image paths if processing images.
        :param videos_paths: List of video paths if processing videos.
        :param stream_url: URL of the video stream if processing a stream.
        :param results_path: Path to save the results if processing images or videos.
        :param project: Project object.
        """
        super().__init__(weight, images_paths, videos_paths, stream_url, results_path, project)
        self._load_model(weight)
        self.transform = T.Compose([T.ToTensor()])
        self.categories = CLASS_NAMES

    def _load_model(self, model_name: str):
        """
        Loads the specified model with the specified weights.

        :param model_name: The name of the model to load.
        """
        if model_name == 'fasterrcnn':
            self.model = fasterrcnn_resnet50_fpn(pretrained=True)
        elif model_name == 'maskrcnn':
            self.model = maskrcnn_resnet50_fpn(pretrained=True)
        elif model_name == 'retinanet':
            self.model = retinanet_resnet50_fpn(pretrained=True)
        elif model_name == 'ssd300':
            self.model = ssd300_vgg16(pretrained=True)
        elif model_name == 'ssdlite320':
            self.model = ssdlite320_mobilenet_v3_large(pretrained=True)
        else:
            raise ValueError(f"Unknown model name: {model_name}")
        self.model.eval()

    def _process_image(self, image: np.ndarray) -> tuple[np.ndarray, list[dict]]:
        """
        Processes a single image with TorchVision detection.

        :param image: The input image.
        :return: The processed image and the results array.
        """
        # Inference
        image_tensor = self.transform(image).unsqueeze(0)
        with torch.no_grad():
            predictions = self.model(image_tensor)[0]

        results_array = []
        # For each box in the result
        for i in range(len(predictions['labels'])):
            # Extract box information
            box = predictions['boxes'][i].cpu().numpy()
            label = int(predictions['labels'][i].item())
            score = predictions['scores'][i].item()

            # Temp, threshold
            if score < 0.3:
                continue

            # Draw bounding box
            draw_bounding_box(
                image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), self.categories[label], score,
                self.project.config.video_box_color, self.project.config.video_text_color,
                self.project.config.video_box_thickness, self.project.config.video_text_size
            )

            # Append the box to the results array
            results_array.append({
                'x1': int(box[0]),
                'y1': int(box[1]),
                'x2': int(box[2]),
                'y2': int(box[3]),
                'classid': label,
                'confidence': score,
            })

        return image, results_array

    def _make_results(self, results_array: list) -> dict:
        """
        Creates the results dictionary with TorchVision specific information.

        :param results_array: The list of results.
        """
        return {
            'model_name': 'TorchVision',
            'weight': self.weight,
            'task': "detection",
            'classes': self.categories,
            'results': results_array
        }
