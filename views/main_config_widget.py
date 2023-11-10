from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QSlider, QLineEdit
from PyQt6.QtCore import Qt
from models.app_state import AppState
import torch
import logging
import os


class MainConfig(QWidget):
    def __init__(self, appstate: AppState):
        super().__init__()
        self._appstate = appstate
        self._confidence_tresh_input = None
        self._confidence_tresh_slider = None
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(self.device_selection_ui())
        main_layout.addLayout(self.confidence_tresh_ui())
        main_layout.addLayout(self.clear_cache_ui())
        self.setLayout(main_layout)

    def device_selection_ui(self):
        devices_label = QLabel('GPU Devices:')
        devices_combo = QComboBox()
        devices_combo.addItem('CPU')
        devices_combo.addItems(self.get_gpu_devices())
        devices_combo.setCurrentText(self.get_device())
        devices_combo.currentTextChanged.connect(self.set_device)

        device_selection_layout = QVBoxLayout()
        device_selection_layout.addWidget(devices_label)
        device_selection_layout.addWidget(devices_combo)

        return device_selection_layout

    def confidence_tresh_ui(self):
        confidence_tresh_label = QLabel('Confidence Threshold:')
        confidence_tresh_slider = QSlider(Qt.Orientation.Horizontal)
        confidence_tresh_slider.setRange(0, 100)
        confidence_tresh_slider.setValue(self.get_thresh())
        confidence_tresh_slider.valueChanged.connect(self.set_thresh)
        self._confidence_tresh_slider = confidence_tresh_slider
        confidence_tresh_input = QLineEdit()
        confidence_tresh_input.setText("{:.2f}".format(self.get_thresh_float()))
        confidence_tresh_input.textChanged.connect(self.set_thresh_float)
        self._confidence_tresh_input = confidence_tresh_input

        confidence_tresh_layout = QVBoxLayout()
        confidence_tresh_layout.addWidget(confidence_tresh_label)
        confidence_tresh_layout.addWidget(confidence_tresh_slider)
        confidence_tresh_layout.addWidget(confidence_tresh_input)

        return confidence_tresh_layout

    def clear_cache_ui(self):
        clear_cache_label = QLabel('Clear cache:')
        clear_cache_button = QPushButton('Clear')
        clear_cache_button.clicked.connect(self.clear_cache)

        clear_cache_layout = QVBoxLayout()
        clear_cache_layout.addWidget(clear_cache_label)
        clear_cache_layout.addWidget(clear_cache_button)

        return clear_cache_layout

    ##############################
    #         CONTROLLER         #
    ##############################

    def get_gpu_devices(self) -> list[str]:
        if not torch.cuda.is_available():
            return []
        num_gpus = torch.cuda.device_count()
        gpu_devices = ['GPU-{} ({})'.format(i, torch.cuda.get_device_name(i)) for i in range(num_gpus)]
        logging.debug('Found {} GPU devices: {}'.format(num_gpus, gpu_devices))
        return gpu_devices

    def get_device(self) -> str:
        if self._appstate.config.device == 'cpu':
            return 'CPU'
        else:
            device_id = torch.cuda.current_device()
            return 'GPU-{} ({})'.format(device_id, torch.cuda.get_device_name(device_id))

    def set_device(self, value: str):
        if value == 'CPU':
            self._appstate.config.device = 'cpu'
        else:
            device_id = int(value.split('-')[1].split(' ')[0])
            self._appstate.config.device = 'cuda:{}'.format(device_id)
        logging.debug('Set device to {}'.format(value))

    def get_thresh(self) -> int:
        return int(self._appstate.config.confidence_threshold * 100)

    def set_thresh(self, value: int):
        self._appstate.config.confidence_threshold = value / 100.0
        self._confidence_tresh_input.setText("{:.2f}".format(value / 100.0))
        logging.debug('Set confidence threshold to {}'.format(value / 100.0))

    def get_thresh_float(self) -> float:
        return self._appstate.config.confidence_threshold

    def set_thresh_float(self, value: float):
        float_value = float(value)
        self._appstate.config.confidence_threshold = float_value
        self._confidence_tresh_slider.setValue(int(float_value * 100.0))
        logging.debug('Set confidence threshold to {}'.format(value))

    def clear_cache(self):
        for file in os.listdir('tmp'):
            os.remove(os.path.join('tmp', file))
        logging.debug('Cleared cache')
