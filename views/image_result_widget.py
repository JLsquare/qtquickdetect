from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsPixmapItem, QGraphicsScene, \
    QComboBox, QLabel, QListWidget, QListWidgetItem, QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtCore import Qt, QFile
from models.project import Project
from utils.file_explorer import open_file_explorer
from utils.image_helpers import draw_bounding_box
from views.resizeable_graphics_widget import ResizeableGraphicsWidget
import json
import os
import numpy as np


class ImageResultWidget(QWidget):
    def __init__(self, project: Project, result_path: str):
        super().__init__()
        self._project = project
        self._result_path = result_path

        self._input_images = []
        self._result_jsons = {}
        self._layer_visibility = {}

        self._file_select_combo = None
        self._model_select_combo = None
        self._layer_list = None
        self._middle_layout = None
        self._current_scene = None

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
        bottom_layout.addWidget(self.open_result_folder_button_ui())
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
        file_select.currentIndexChanged.connect(self.change_current_file)
        self._file_select_combo = file_select

        model_select_label = QLabel('Select model:')
        model_select = QComboBox()
        model_select.currentIndexChanged.connect(self.change_current_model)
        self._model_select_combo = model_select

        layer_select_label = QLabel('Select layers:')
        layer_list = QListWidget()
        layer_list.itemChanged.connect(self.toggle_layer)
        self._layer_list = layer_list

        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_layout.addWidget(file_select_label)
        left_layout.addWidget(file_select)
        left_layout.addWidget(model_select_label)
        left_layout.addWidget(model_select)
        left_layout.addWidget(layer_select_label)
        left_layout.addWidget(layer_list)

        return left_layout

    def image_ui(self, input_image: str) -> QWidget:
        # Create UI for displaying input images

        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)

        scene = QGraphicsScene(container_widget)
        self._current_scene = scene

        pixmap = QPixmap(input_image)
        base_image_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(base_image_item)

        view = ResizeableGraphicsWidget(scene, container_widget)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container_layout.addWidget(view)

        container_widget.setLayout(container_layout)
        container_widget.setProperty('class', 'border')
        return container_widget

    def open_result_folder_button_ui(self) -> QPushButton:
        open_result_folder_button = QPushButton('Open Result Folder')
        open_result_folder_button.clicked.connect(self.open_result_folder)
        return open_result_folder_button

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

    def open_result_folder(self):
        try:
            open_file_explorer(self._result_path)
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def save_image(self):
        input_image = self._file_select_combo.currentData()
        result_json = self._model_select_combo.currentData()

        if not input_image:
            QMessageBox.critical(self, "Error", "No image selected.")
            return
        if not result_json:
            QMessageBox.critical(self, "Error", "No model selected.")
            return

        # Use QPainter to draw all layers on top of the input image
        img_size = QPixmap(input_image).size()
        img = QImage(img_size.width(), img_size.height(), QImage.Format.Format_RGBA8888)
        img.fill(Qt.GlobalColor.transparent)
        painter = QPainter(img)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, img_size.width(), img_size.height(), QPixmap(input_image))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        for item_text, layer_info in self._layer_visibility.items():
            if layer_info['visible']:
                painter.drawPixmap(0, 0, img_size.width(), img_size.height(), layer_info['initial_pixmap'])
        painter.end()

        # Save the image
        if self._project.config.image_format == 'png':
            format_filter = 'PNG (*.png)'
        else:
            format_filter = 'JPEG (*.jpg)'
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", format_filter)
        if file_name:
            if not file_name.lower().endswith('.png') and format_filter == 'PNG (*.png)':
                file_name += ".png"
            elif not file_name.lower().endswith('.jpg') and format_filter == 'JPEG (*.jpg)':
                file_name += ".jpg"
            if img.save(file_name):
                QMessageBox.information(self, "Success", "Image saved successfully!")
            else:
                QMessageBox.critical(self, "Error", "An error occurred while saving the image.")

    def save_json(self):
        result_json = self._model_select_combo.currentData()

        if result_json is None:
            QMessageBox.critical(self, "Error", "No model selected.")
            return

        # Save the JSON
        file_name, selected_filter = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON (*.json)")
        if file_name:
            if not file_name.lower().endswith('.json'):
                file_name += ".json"
            if QFile.copy(result_json, file_name):
                QMessageBox.information(self, "Success", "JSON saved successfully!")
            else:
                QMessageBox.critical(self, "Error", "An error occurred while saving the JSON.")

    def change_current_file(self):
        index = self._file_select_combo.currentIndex()

        # Update the image
        input_image = self._input_images[index]
        image_widget = self.image_ui(input_image)
        if self._middle_layout.count() > 1:
            self._middle_layout.itemAt(1).widget().deleteLater()
        self._middle_layout.addWidget(image_widget, 1)

        # Update the model selection
        self._model_select_combo.clear()
        self._model_select_combo.addItem('None')
        for result_json in self._result_jsons[input_image]:
            with open(result_json, 'r') as file:
                data = json.load(file)
            self._model_select_combo.addItem(data['model_name'], result_json)

    def change_current_model(self):
        index = self._model_select_combo.currentIndex()

        # Reset everything and re-add the input image
        self._layer_list.clear()
        self._current_scene.clear()
        self._layer_visibility.clear()
        input_image = self._file_select_combo.currentData()
        self._current_scene.addPixmap(QPixmap(input_image))

        if index < 1:
            return

        result_json = self._result_jsons[input_image][index - 1]
        img_size = QPixmap(input_image).size()

        with open(result_json, 'r') as file:
            data = json.load(file)

        # Add each layer to the list and scene
        for index, result in enumerate(data['results']):
            # Add the layer to the list
            class_name = data['classes'][str(result['classid'])]
            confidence = round(result['confidence'], 2)
            item_text = f"{class_name} ({index}) : {confidence}%"
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self._layer_list.addItem(item)

            # Add the layer to the scene
            top_left = (int(result['x1']), int(result['y1']))
            bottom_right = (int(result['x2']), int(result['y2']))
            layer = np.full((img_size.height(), img_size.width(), 4), 0, np.uint8)
            draw_bounding_box(
                layer, top_left, bottom_right, class_name, confidence,
                self._project.config.image_box_color, self._project.config.image_text_color,
                self._project.config.image_box_thickness, self._project.config.image_text_size
            )
            q_img = QImage(layer.data, img_size.width(), img_size.height(), 4 * img_size.width(),
                           QImage.Format.Format_RGBA8888)
            layer_pixmap = QPixmap(q_img)
            layer_item = QGraphicsPixmapItem(layer_pixmap)
            self._current_scene.addItem(layer_item)

            # Store the layer info
            self._layer_visibility[item_text] = {
                'item': layer_item,
                'visible': True,
                'initial_pixmap': layer_pixmap
            }

    def add_input_and_result(self, input_image: str, result_json: str):
        # Add the input if it's not already there
        if input_image not in self._input_images:
            self._input_images.append(input_image)
            self._result_jsons[input_image] = []
            self._file_select_combo.addItem(os.path.basename(input_image), input_image)

        # Add the result to the list of results for the input image
        self._result_jsons[input_image].append(result_json)

        # Update the UI if the current file is the one that was just added
        if self._file_select_combo.currentIndex() == self._file_select_combo.count() - 1:
            self.change_current_file()

    def toggle_layer(self, item: QListWidgetItem):
        # Toggle the visibility of the layer
        layer_info = self._layer_visibility.get(item.text())
        if layer_info:
            layer_info['item'].setVisible(item.checkState() == Qt.CheckState.Checked)
            layer_info['visible'] = layer_info['item'].isVisible()
            layer_info['initial_pixmap'] = layer_info['item'].pixmap()
