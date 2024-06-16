from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea


class AboutWidget(QWidget):
    """
    AboutWidget is a QWidget that displays information about the application.
    """
    def __init__(self):
        """
        Initializes the AboutWidget.
        """
        super().__init__()

        # PyQt6 Components
        self._main_layout: Optional[QVBoxLayout] = None
        self._scroll_area: Optional[QScrollArea] = None
        self._content_widget: Optional[QWidget] = None
        self._content_layout: Optional[QVBoxLayout] = None
        self._label: Optional[QLabel] = None

        self.init_ui()

    def init_ui(self) -> None:
        """
        Initializes the user interface components.
        """
        self._main_layout = QVBoxLayout()
        self._main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Add scroll area
        self._scroll_area = QScrollArea()
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_widget.setLayout(self._content_layout)

        self._label = QLabel("""
        <h1>About QTQuickDetect</h1>
        <p>QTQuickDetect is a powerful application for image and video analysis, leveraging state-of-the-art deep learning models.</p>
        <p>It provides functionalities for object detection, segmentation, classification, and pose estimation.</p>
        
        <h2>How It Works</h2>
        <p>The application utilizes the following technologies:</p>
        <ul>
            <li><b>Ultralytics YOLO:</b> For robust and efficient object detection models. <a href="https://github.com/ultralytics/ultralytics">(More info)</a></li>
            <li><b>Torchvision:</b> For a variety of pre-trained models and weights. <a href="https://pytorch.org/vision/stable/models.html#">(More info)</a></li>
            <li><b>OpenCV:</b> For image processing tasks such as reading, writing, and manipulating images and videos. <a href="https://opencv.org/">(More info)</a></li>
            <li><b>PyQt6:</b> For the user interface, providing a seamless and intuitive user experience. <a href="https://doc.qt.io/qtforpython/">(More info)</a></li>
        </ul>
        <p>While Ultralytics and Torchvision provide the models and weights, the utility functions are custom implemented to ensure flexibility and performance.</p>
        <p>The application is modular, making it easy to add entire pipelines for additional tasks and models.</p>
        
        <h2>Features</h2>
        <p>QTQuickDetect offers a wide range of features:</p>
        <ul>
            <li>Perform inference on images, videos, and live streams.</li>
            <li>Choose between detection, segmentation, classification, and pose estimation tasks.</li>
            <li>Customize inference settings, such as device, precision, and colors.</li>
            <li>Manage and organize image and video collections.</li>
            <li>View inference history and results, and save outputs in various formats.</li>
        </ul>
        
        <h2>Tasks</h2>
        <p>QTQuickDetect can perform the following tasks:</p>
        <ul>
            <li><b>Detection:</b> Identify and locate objects within an image or video. This task draws bounding boxes around detected objects. <a href="https://docs.ultralytics.com/tasks/detect/">(More info)</a></li>
            <li><b>Segmentation:</b> Classify each pixel in an image to determine the exact shape and boundary of objects. <a href="https://docs.ultralytics.com/tasks/segment/">(More info)</a></li>
            <li><b>Classification:</b> Assign a label to an entire image or a specific region of interest. This task returns the top 5 classes with their confidence scores. <a href="https://docs.ultralytics.com/tasks/classify/">(More info)</a></li>
            <li><b>Pose Estimation:</b> Detect the positions of key points on objects, typically used for human pose estimation to identify body parts and their configurations. <a href="https://docs.ultralytics.com/tasks/pose/">(More info)</a></li>
        </ul>

        <h2>Inference Output</h2>
        <p>QTQuickDetect generates comprehensive results for each inference task. These results include:</p>
        <ul>
            <li>The processed media (images or video) with bounding boxes, segmentation masks, etc.</li>
            <li>A JSON file containing detailed information about each object detected, including class labels, confidence scores, and coordinates.</li>
        </ul>
        
        <h2>How to Use</h2>
        <p>To use QTQuickDetect, follow these steps:</p>
        <ol>
            <li>Import the images or videos you want to analyze through the 'Image Collections' or 'Video Collections' section.</li>
            <li>Configure the presets through the 'Presets' section. Here are the preset settings:</li>
            <ul>
                <li>Device: 'cpu' or 'gpu'</li>
                <li>Half Precision: Enable or disable half precision (FP16)</li>
                <li>IOU Threshold: Set the IOU threshold value</li>
                <li>Image Format: Choose between 'png', 'jpg', etc.</li>
                <li>Video Format: Choose between 'mp4', 'avi', etc.</li>
                <li>Box Color: Set the RGBA color for the bounding box</li>
                <li>Segment Color: Set the RGBA color for segmentation</li>
                <li>Pose Colors: Set the RGBA colors for pose keypoints and lines</li>
                <li>Text Color: Set the RGBA color for text annotations</li>
                <li>Text Size: Set the size for text annotations</li>
            </ul>
            <li>Select the desired inference task (detection, segmentation, classification, or pose), choose the weights you want to use, the preset, and the collection.</li>
            <li>Run the inference, after that if it's images or videos, an inference result will be displayed, if it's a live stream, the result will be displayed in real-time.</li>
            <li>If it's an image or video, select the file and the model you want to see, select / deselect the objects you want to see, and save the result if needed.</li>
            <li>Open old results through the 'Inference History' section.</li>
        </ol>
        
        <h2>Authors</h2>
        <p>QTQuickDetect was developed by Jean-Loup Mellion and Gatien Da Rocha, students at the University IUT Vannes, France.
        """)
        self._label.setOpenExternalLinks(True)
        self._content_layout.addWidget(self._label)
        self._scroll_area.setWidget(self._content_widget)
        self._scroll_area.setWidgetResizable(True)
        self._main_layout.addWidget(self._scroll_area)
        self.setLayout(self._main_layout)
