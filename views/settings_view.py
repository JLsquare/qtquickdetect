from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QGridLayout, QPushButton, QLabel, QComboBox, QSlider, QLineEdit
from PyQt6.QtCore import Qt
import torch
import logging


class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    ##############################
    #            VIEW            #
    ##############################

    def initUI(self):
        self.setWindowTitle('QTQuickDetect Settings')
        self.setGeometry(100, 100, 480, 480)
        with open('ressources/qss/stylesheet.qss', 'r') as file:
            self.setStyleSheet(file.read())

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        tab = QTabWidget(self)

        tab.addTab(self.general_page_ui(), "General")
        tab.addTab(self.image_page_ui(), "Image")
        tab.addTab(self.video_page_ui(), "Video")
        tab.addTab(self.live_page_ui(), "Live")

        main_layout.addWidget(tab, 0, 0, 2, 1)
        main_layout.addWidget(self.cancel_button_ui(), 2, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.save_button_ui(), 2, 0, alignment=Qt.AlignmentFlag.AlignRight)

    def general_page_ui(self):
        general_page = QWidget(self)
        general_layout = QVBoxLayout()
        general_page.setLayout(general_layout)
        general_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        devices_label = QLabel('GPU Devices:')
        devices_combo = QComboBox()
        devices_combo.addItem('CPU')
        devices_combo.addItems(self.get_gpu_devices())

        confidence_tresh_label = QLabel('Confidence Threshold:')
        confidence_tresh_slider = QSlider(Qt.Orientation.Horizontal)
        confidence_tresh_slider.setRange(0, 100)

        confidence_tresh_input = QLineEdit()

        general_layout.addWidget(devices_label)
        general_layout.addWidget(devices_combo)
        general_layout.addWidget(confidence_tresh_label)
        general_layout.addWidget(confidence_tresh_slider)
        general_layout.addWidget(confidence_tresh_input)

        return general_page

    def image_page_ui(self):
        image_page = QWidget(self)
        image_layout = QVBoxLayout()
        image_page.setLayout(image_layout)

        return image_page

    def video_page_ui(self):
        video_page = QWidget(self)
        video_layout = QVBoxLayout()
        video_page.setLayout(video_layout)

        return video_page

    def live_page_ui(self):
        live_page = QWidget(self)
        live_layout = QVBoxLayout()
        live_page.setLayout(live_layout)

        return live_page

    def cancel_button_ui(self):
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.cancel_settings)

        return cancel_button

    def save_button_ui(self):
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_settings)

        return save_button

    ##############################
    #         CONTROLLER         #
    ##############################

    def save_settings(self):
        logging.debug('Saved settings')
        self.close()

    def cancel_settings(self):
        logging.debug('Canceled settings')
        self.close()

    def get_gpu_devices(self):
        if not torch.cuda.is_available():
            return []
        num_gpus = torch.cuda.device_count()
        gpu_devices = ['GPU-{} ({})'.format(i, torch.cuda.get_device_name(i)) for i in range(num_gpus)]
        logging.debug('Found {} GPU devices: {}'.format(num_gpus, gpu_devices))

        return gpu_devices