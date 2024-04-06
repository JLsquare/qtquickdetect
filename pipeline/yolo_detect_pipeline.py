import numpy as np
from ultralytics import YOLO
from pipeline.pipeline import Pipeline
from utils.image_helpers import draw_bounding_box


class YoloDetectPipeline(Pipeline):
    """Pipeline for detecting objects in images and videos using YoloV8."""

    def __init__(self, weight: str, images_paths: list[str] | None, videos_paths: list[str] | None,
                 stream_url: str | None, results_path: str | None, project):
        """
        Initializes the pipeline.

        :param weight: The weight file path to use.
        :param images_paths: List of image paths if processing images.
        :param videos_paths: List of video paths if processing videos.
        :param stream_url: URL of the video stream if processing a stream.
        :param results_path: Path to save the results if processing images or videos.
        :param project: Project object.
        """
        super().__init__(weight, images_paths, videos_paths, stream_url, results_path, project)
        self.model = YOLO(weight).to(self.project.device)

    def _process_image(self, image: np.ndarray) -> tuple[np.ndarray, list[dict]]:
        """
        Processes a single image with YoloV8 detection.

        :param image: The input image.
        :return: The processed image and the results array.
        """
        # Inference
        result = self.model(image, half=(self.project.device.type == 'cuda' and self.project.config.half_precision),
                            verbose=False, iou=self.project.config.iou_threshold)[0].cpu()

        results_array = []
        # For each box in the result
        for box in result.boxes:
            # Extract box information
            flat = box.xyxy.flatten()
            top_left, bottom_right = (int(flat[0]), int(flat[1])), (int(flat[2]), int(flat[3]))
            class_id, class_name = int(box.cls), self.model.names[int(box.cls)]
            conf = float(box.conf[0])

            # Draw bounding box
            draw_bounding_box(
                image, top_left, bottom_right, class_name, conf,
                self.project.config.video_box_color, self.project.config.video_text_color,
                self.project.config.video_box_thickness, self.project.config.video_text_size
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
