import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel, QHBoxLayout, QPushButton, QFileDialog, \
    QMessageBox, QGraphicsPixmapItem, QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QFile
from models.app_state import AppState
from utils.image_helpers import draw_bounding_box
import logging
import json

from views.resizeable_graphics_widget import ResizeableGraphicsWidget

appstate = AppState.get_instance()


class ImageResultWidget(QWidget):
    def __init__(self, input_image: str, result_json: str):
        super().__init__()
        self._input_image = input_image
        self._result_json = result_json
        self._layer_visibility = {}
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Tab input / result image
        tab = QTabWidget(self)
        tab.addTab(self.input_image_ui(), "Input")
        tab.addTab(self.result_image_ui(), "Result")
        tab.setCurrentIndex(1)

        # Middle layout
        middle_layout = QHBoxLayout()
        middle_layout.addStretch(1)
        middle_layout.addWidget(tab, 1)

        # Bottom layout
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.save_json_button_ui())
        bottom_layout.addWidget(self.save_image_button_ui())

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def input_image_ui(self) -> QLabel:
        input_image = QLabel(self)
        input_image.setPixmap(QPixmap(self._input_image).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                                Qt.TransformationMode.SmoothTransformation))
        return input_image

    def result_image_ui(self) -> QWidget:
        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)

        scene = QGraphicsScene(container_widget)

        pixmap = QPixmap(self._input_image)
        img_size = pixmap.size()
        base_image_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(base_image_item)

        with open(self._result_json, 'r') as file:
            result_json = json.load(file)

        results = result_json['results']
        classes = result_json['classes']

        self._layer_visibility = {}

        for result in results:
            top_left = (int(result['x1']), int(result['y1']))
            bottom_right = (int(result['x2']), int(result['y2']))
            classname = classes[str(result['classid'])]
            confidence = result['confidence']
            config = appstate.config

            layer = np.full((img_size.width(), img_size.height(), 4), 0, np.uint8)
            draw_bounding_box(layer, top_left, bottom_right, classname, confidence,
                              config.video_box_color, config.video_text_color,
                              config.video_box_thickness, config.video_text_size)

            height, width, channel = layer.shape
            bytes_per_line = 4 * width
            q_img = QImage(layer.data, width, height, bytes_per_line, QImage.Format.Format_RGBA8888)
            layer_pixmap = QPixmap(q_img)
            layer_item = QGraphicsPixmapItem(layer_pixmap)
            layer_item.setPos(0, 0)
            scene.addItem(layer_item)

            self._layer_visibility[result['classid']] = {
                'item': layer_item,
                'visible': True
            }

        view = ResizeableGraphicsWidget(scene, container_widget)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container_layout.addWidget(view)

        container_widget.setLayout(container_layout)
        return container_widget

    def toggle_layer(self, class_id: int):
        layer_info = self._layer_visibility.get(class_id)
        if layer_info:
            layer_item = layer_info['item']
            layer_item.setVisible(not layer_item.isVisible())
            layer_info['visible'] = layer_item.isVisible()

    def save_json_button_ui(self) -> QPushButton:
        save_json_button = QPushButton('Save JSON')
        return save_json_button

    def save_image_button_ui(self) -> QPushButton:
        save_image_button = QPushButton('Save Image')
        save_image_button.clicked.connect(self.save_image)
        return save_image_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def save_image(self):
        if self._result_json.lower().endswith('.jpg') or self._result_json.lower().endswith('.jpeg'):
            format_filter = 'JPEG (*.jpg, *.jpeg)'
        else:
            format_filter = 'PNG (*.png)'
        file_name, selected_filter = QFileDialog.getSaveFileName(self, "Save Image", "", format_filter)
        if file_name:
            if selected_filter == 'JPEG (*.jpg, *.jpeg)' and not file_name.lower().endswith('.jpg'):
                file_name += ".jpg"
            if selected_filter == 'PNG (*.png)' and not file_name.lower().endswith('.png'):
                file_name += ".png"
            if QFile.copy(self._result_json, file_name):
                QMessageBox.information(self, "Success", "Image saved successfully!")
                logging.debug(f'Saved image to {file_name}')
            else:
                QMessageBox.critical(self, "Error", "An error occurred while saving the image.")
                logging.error(f'Could not save image to {file_name}')
