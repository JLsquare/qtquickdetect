import logging

import numpy as np
import torch
from ultralytics import YOLO

from models.preset import Preset
from pipeline.pipeline import Pipeline
from utils.image_helpers import draw_bounding_box, generate_color


class YoloDetectPipeline(Pipeline):
    """Pipeline for detecting objects in images and videos using YoloV8."""

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
        Processes a single image with YoloV8 detection.

        :param image: The input image.
        :return: The processed image and the results array.
        """
        # Inference
        result = self.model(image, half=(self.device.type == 'cuda' and self.preset.half_precision),
                            verbose=False, iou=self.preset.iou_threshold)[0].cpu()

        results_array = []
        # For each box in the result
        for box in result.boxes:
            # Extract box information
            flat = box.xyxy.flatten()
            top_left, bottom_right = (int(flat[0]), int(flat[1])), (int(flat[2]), int(flat[3]))
            class_id, class_name = int(box.cls), self.model.names[int(box.cls)]
            conf = float(box.conf[0])

            # Draw bounding box
            if self.preset.box_color_per_class:
                box_color = generate_color(class_id)
            else:
                box_color = self.preset.box_color
            draw_bounding_box(
                image, top_left, bottom_right, class_name, conf,
                box_color, self.preset.text_color,
                self.preset.box_thickness, self.preset.text_size
            )

            # Append the box to the results array
            results_array.append({
                'x1': top_left[0],
                'y1': top_left[1],
                'x2': bottom_right[0],
                'y2': bottom_right[1],
                'classid': class_id,
                'confidence': conf,
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
            'task': "detection",
            'classes': list(self.model.names.values()),
            'results': results_array
        }
