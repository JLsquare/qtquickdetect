from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QPushButton, QGraphicsPixmapItem, \
    QGraphicsScene, QComboBox, QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from models.app_state import AppState
from utils.image_helpers import draw_bounding_box
from views.resizeable_graphics_widget import ResizeableGraphicsWidget
import json
import os
import numpy as np

appstate = AppState.get_instance()


class ImageResultWidget(QWidget):
    def __init__(self):
        super().__init__()

        self._middle_layout = None
        self._input_images = []
        self._result_jsons = []
        self._layer_visibility = {}

        self._file_select_combo = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Middle layout
        middle_layout = QHBoxLayout()
        middle_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        middle_layout.addLayout(self.left_ui(), 1)
        self._middle_layout = middle_layout

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

    def left_ui(self) -> QVBoxLayout:
        file_select_label = QLabel('Select file:')
        file_select = QComboBox()
        file_select.currentIndexChanged.connect(self.open_current_file)
        self._file_select_combo = file_select

        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_layout.addWidget(file_select_label)
        left_layout.addWidget(file_select)

        return left_layout

    def input_image_ui(self, input_image: str) -> QWidget:
        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)

        scene = QGraphicsScene(container_widget)

        pixmap = QPixmap(input_image)
        base_image_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(base_image_item)

        view = ResizeableGraphicsWidget(scene, container_widget)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container_layout.addWidget(view)

        container_widget.setLayout(container_layout)
        return container_widget

    def result_image_ui(self, input_image: str, result_json: str) -> QWidget:
        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)

        scene = QGraphicsScene(container_widget)

        pixmap = QPixmap(input_image)
        img_size = pixmap.size()
        base_image_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(base_image_item)

        with open(result_json, 'r') as file:
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

    # def toggle_layer(self, class_id: int):
    #    layer_info = self._layer_visibility.get(class_id)
    #    if layer_info:
    #        layer_item = layer_info['item']
    #        layer_item.setVisible(not layer_item.isVisible())
    #        layer_info['visible'] = layer_item.isVisible()

    def save_json_button_ui(self) -> QPushButton:
        save_json_button = QPushButton('Save JSON')
        save_json_button.clicked.connect(self.save_json)
        return save_json_button

    def save_image_button_ui(self) -> QPushButton:
        save_image_button = QPushButton('Save Image')
        save_image_button.clicked.connect(self.save_image)
        return save_image_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def save_image(self):
        pass

    def save_json(self):
        pass

    def add_input_and_result(self, input_image: str, result_json: str):
        self._input_images.append(input_image)
        self._result_jsons.append(result_json)
        self._file_select_combo.addItem(os.path.basename(input_image), result_json)

    def open_current_file(self):
        tab = QTabWidget()
        input_image = self._input_images[self._file_select_combo.currentIndex()]
        result_json = self._result_jsons[self._file_select_combo.currentIndex()]
        tab.addTab(self.input_image_ui(input_image), 'Input')
        tab.addTab(self.result_image_ui(input_image, result_json), 'Result')
        tab.setCurrentIndex(1)
        if self._middle_layout.count() > 1:
            self._middle_layout.itemAt(1).widget().deleteLater()
        self._middle_layout.addWidget(tab, 1)
