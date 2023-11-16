from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QPushButton, QGraphicsPixmapItem, \
    QGraphicsScene, QComboBox, QLabel, QListWidget, QListWidgetItem, QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtCore import Qt, QFile
from models.app_state import AppState
from utils.image_helpers import draw_bounding_box
from views.resizeable_graphics_widget import ResizeableGraphicsWidget
import json
import os
import numpy as np
import logging


class ImageResultWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._appstate = AppState.get_instance()

        self._input_images = []
        self._result_jsons = []
        self._layer_visibility = {}

        self._file_select_combo = None
        self._layer_list = None
        self._middle_layout = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Initialize user interface layout and widgets

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
        # UI elements for file selection and layer visibility

        file_select_label = QLabel('Select file:')
        file_select = QComboBox()
        file_select.currentIndexChanged.connect(self.open_current_file)
        self._file_select_combo = file_select

        layer_select_label = QLabel('Select layers:')
        layer_list = QListWidget()
        layer_list.itemChanged.connect(self.toggle_layer)
        self._layer_list = layer_list

        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_layout.addWidget(file_select_label)
        left_layout.addWidget(file_select)
        left_layout.addWidget(layer_select_label)
        left_layout.addWidget(layer_list)

        return left_layout

    def input_image_ui(self, input_image: str) -> QWidget:
        # Create UI for displaying input images

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
        # Create UI for displaying result images with annotations

        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)

        scene = QGraphicsScene(container_widget)

        pixmap = QPixmap(input_image)
        base_image_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(base_image_item)

        with open(result_json, 'r') as file:
            results_data = json.load(file)

        self._layer_visibility = {}

        for index, result in enumerate(results_data['results']):
            # Drawing bounding boxes on the result image
            self.draw_bounding_box_on_layer(scene, result, pixmap.size(), index, results_data['classes'])

        view = ResizeableGraphicsWidget(scene, container_widget)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container_layout.addWidget(view)

        container_widget.setLayout(container_layout)
        return container_widget

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
        base_image_path = self._input_images[self._file_select_combo.currentIndex()]
        base_pixmap = QPixmap(base_image_path)
        canvas = QPixmap(base_pixmap.size())
        canvas.fill(Qt.GlobalColor.transparent)

        painter = QPainter(canvas)
        painter.drawPixmap(0, 0, base_pixmap)

        for (class_id, index), layer_info in self._layer_visibility.items():
            if layer_info['visible']:
                layer_item = layer_info['item']
                layer_pixmap = layer_info['initial_pixmap']
                pos = layer_item.pos()
                painter.drawPixmap(pos, layer_pixmap)

        painter.end()

        if self._appstate.config.image_format == 'png':
            file_name, selected_filter = QFileDialog.getSaveFileName(self, "Save PNG", "", "PNG (*.png)")
        else:
            file_name, selected_filter = QFileDialog.getSaveFileName(self, "Save JPEG", "", "JPEG (*.jpg)")
        if file_name:
            if selected_filter == "PNG (*.png)" and not file_name.lower().endswith('.png'):
                file_name += ".png"
            elif (selected_filter == "JPEG (*.jpg)" and not file_name.lower().endswith('.jpg')
                  and not file_name.lower().endswith('.jpeg')):
                file_name += ".jpg"
            if canvas.save(file_name):
                QMessageBox.information(self, "Success", "Image saved successfully!")
                logging.debug(f'Saved image to {file_name}')
            else:
                QMessageBox.critical(self, "Error", "An error occurred while saving the image.")
                logging.error(f'Could not save image to {file_name}')

    def save_json(self):
        file_name, selected_filter = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON (*.json)")
        if file_name:
            if not file_name.lower().endswith('.json'):
                file_name += ".json"
            if QFile.copy(self._result_jsons[self._file_select_combo.currentIndex()], file_name):
                QMessageBox.information(self, "Success", "JSON saved successfully!")
                logging.debug(f'Saved JSON to {file_name}')
            else:
                QMessageBox.critical(self, "Error", "An error occurred while saving the JSON.")
                logging.error(f'Could not save JSON to {file_name}')

    def add_input_and_result(self, input_image: str, result_json: str):
        self._input_images.append(input_image)
        self._result_jsons.append(result_json)
        self._file_select_combo.addItem(os.path.basename(input_image), result_json)

    def open_current_file(self):
        # Handler for opening and displaying the selected file and its results

        tab = QTabWidget()
        current_index = self._file_select_combo.currentIndex()

        tab.addTab(self.input_image_ui(self._input_images[current_index]), 'Input')
        tab.addTab(self.result_image_ui(self._input_images[current_index], self._result_jsons[current_index]), 'Result')
        tab.setCurrentIndex(1)

        if self._middle_layout.count() > 1:
            self._middle_layout.itemAt(1).widget().deleteLater()
        self._middle_layout.addWidget(tab, 1)

        self.populate_layer_list(self._result_jsons[current_index])

    def populate_layer_list(self, result_json):
        self._layer_list.clear()
        with open(result_json, 'r') as file:
            data = json.load(file)

        for index, result in enumerate(data['results']):
            item_text = f"{data['classes'][str(result['classid'])]} ({index}) : {round(result['confidence'] * 100, 2)}%"
            self.add_layer_list_item(result['classid'], index, item_text)

    def add_layer_list_item(self, class_id, index, text):
        item = QListWidgetItem(text)
        unique_key = (class_id, index)
        item.setData(Qt.ItemDataRole.UserRole, unique_key)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked)
        self._layer_list.addItem(item)

    def toggle_layer(self, item: QListWidgetItem):
        unique_key = item.data(Qt.ItemDataRole.UserRole)
        layer_info = self._layer_visibility.get(unique_key)
        if layer_info:
            layer_info['item'].setVisible(item.checkState() == Qt.CheckState.Checked)
            layer_info['visible'] = layer_info['item'].isVisible()
            layer_info['initial_pixmap'] = layer_info['item'].pixmap()

    def draw_bounding_box_on_layer(self, scene, result, img_size, index, classes):
        # Utility function for drawing bounding boxes

        config = self._appstate.config
        top_left = (int(result['x1']), int(result['y1']))
        bottom_right = (int(result['x2']), int(result['y2']))
        classname = classes[str(result['classid'])]
        confidence = result['confidence']

        layer = np.full((img_size.height(), img_size.width(), 4), 0, np.uint8)
        draw_bounding_box(layer, top_left, bottom_right, classname, confidence,
                          config.video_box_color, config.video_text_color,
                          config.video_box_thickness, config.video_text_size)

        q_img = QImage(layer.data, img_size.width(), img_size.height(), 4 * img_size.width(),
                       QImage.Format.Format_RGBA8888)
        layer_pixmap = QPixmap(q_img)
        layer_item = QGraphicsPixmapItem(layer_pixmap)
        scene.addItem(layer_item)

        # Update layer visibility mapping
        self._layer_visibility[(result['classid'], index)] = {
            'item': layer_item,
            'visible': True,
            'initial_pixmap': layer_pixmap
        }
