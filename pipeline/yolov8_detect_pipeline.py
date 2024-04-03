import cv2 as cv
from ultralytics import YOLO
from pipeline.pipeline import Pipeline
from utils.image_helpers import draw_bounding_box


class YoloV8DetectPipeline(Pipeline):
    """Pipeline for detecting objects in images and videos using YoloV8."""

    def __init__(self, weight: str, results_path: str | None, project):
        super().__init__(weight, results_path, project)
        self.model = YOLO(weight).to(self.project.device)

    def _process_image(self, image):
        """Processes a single image / frame"""
        if self.project.device.type == 'cuda' and self.project.config.half_precision:
            result = self.model(image, half=True, verbose=False, iou=self.project.config.iou_threshold)[0].cpu()
        else:
            result = self.model(image, verbose=False, iou=self.project.config.iou_threshold)[0].cpu()

        results_array = []
        for box in result.boxes:
            flat = box.xyxy.flatten()
            top_left, bottom_right = (int(flat[0]), int(flat[1])), (int(flat[2]), int(flat[3]))
            class_id, class_name = int(box.cls), self.model.names[int(box.cls)]
            conf = float(box.conf[0])

            draw_bounding_box(
                image, top_left, bottom_right, class_name, conf,
                self.project.config.video_box_color, self.project.config.video_text_color,
                self.project.config.video_box_thickness, self.project.config.video_text_size
            )

            results_array.append({
                'x1': top_left[0],
                'y1': top_left[1],
                'x2': bottom_right[0],
                'y2': bottom_right[1],
                'classid': class_id,
                'confidence': conf,
            })

        return image, results_array

    def _process_video(self, input_path: str, output_path: str):
        """Processes a video file."""
        cap = cv.VideoCapture(input_path)
        width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv.CAP_PROP_FPS)
        codec = cv.VideoWriter_fourcc(*'mp4v')
        out = cv.VideoWriter(output_path, codec, fps, (width, height))

        results_array = []
        while True:
            ret, frame = cap.read()
            if not ret or self.cancel_requested:
                break

            result_frame, result_json = self._process_image(frame)
            out.write(result_frame)
            results_array.extend(result_json)
            self.progress_signal.emit(cap.get(cv.CAP_PROP_POS_FRAMES) / cap.get(cv.CAP_PROP_FRAME_COUNT))

        cap.release()
        out.release()

        return results_array

    def _make_results(self, results_array: list):
        """Creates the results dictionary."""
        return {
            'model_name': self.weight,
            'task': "detection",
            'classes': self.model.names,
            'results': results_array
        }
