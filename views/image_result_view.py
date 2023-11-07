from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel, QHBoxLayout, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QFile
import logging


class ImageResultView(QWidget):
    def __init__(self, input_image, result_image):
        super().__init__()
        self._input_image = input_image
        self._result_image = result_image
        self.initUI()

    ##############################
    #            VIEW            #
    ##############################

    def initUI(self):
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

    def input_image_ui(self):
        input_image = QLabel(self)
        input_image.setPixmap(QPixmap(self._input_image).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        input_image.setScaledContents(True)
        return input_image

    def result_image_ui(self):
        result_image = QLabel(self)
        result_image.setPixmap(QPixmap(self._result_image).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        result_image.setScaledContents(True)
        return result_image

    def save_json_button_ui(self):
        save_json_button = QPushButton('Save JSON')
        return save_json_button

    def save_image_button_ui(self):
        save_image_button = QPushButton('Save Image')
        save_image_button.clicked.connect(self.save_image)
        return save_image_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def save_image(self):
        if self._result_image.lower().endswith('.jpg') or self._result_image.lower().endswith('.jpeg'):
            format_filter = 'JPEG (*.jpg, *.jpeg)'
        else:
            format_filter = 'PNG (*.png)'
        file_name, selected_filter = QFileDialog.getSaveFileName(self, "Save Image", "", format_filter)
        if file_name:
            if selected_filter == 'JPEG (*.jpg, *.jpeg)' and not file_name.lower().endswith('.jpg'):
                file_name += ".jpg"
            if selected_filter == 'PNG (*.png)' and not file_name.lower().endswith('.png'):
                file_name += ".png"
            if QFile.copy(self._result_image, file_name):
                QMessageBox.information(self, "Success", "Image saved successfully!")
                logging.debug(f'Saved image to {file_name}')
            else:
                QMessageBox.critical(self, "Error", "An error occurred while saving the image.")
                logging.error(f'Could not save image to {file_name}')
