from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QRadioButton
from PyQt6.QtCore import Qt
from models.project_config import ProjectConfig
import torch
import logging


class GeneralProjectConfigWidget(QWidget):
    def __init__(self, config: ProjectConfig):
        super().__init__()

        # PyQT6 Components
        self.main_layout: Optional[QVBoxLayout] = None
        self.devices_label: Optional[QLabel] = None
        self.devices_combo: Optional[QComboBox] = None
        self.device_selection_layout: Optional[QVBoxLayout] = None
        self.half_precision_label: Optional[QLabel] = None
        self.half_precision_enabled: Optional[QRadioButton] = None
        self.half_precision_disabled: Optional[QRadioButton] = None
        self.half_precision_layout: Optional[QVBoxLayout] = None

        self._config = config
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.addLayout(self.device_selection_ui())
        self.main_layout.addLayout(self.half_precision_ui())
        self.setLayout(self.main_layout)

    def device_selection_ui(self):
        self.devices_label = QLabel('GPU Devices:')
        self.devices_combo = QComboBox()
        self.devices_combo.addItem('CPU')
        self.devices_combo.addItems(self.get_gpu_devices())
        self.devices_combo.setCurrentText(self.get_device())
        self.devices_combo.currentTextChanged.connect(self.set_device)

        self.device_selection_layout = QVBoxLayout()
        self.device_selection_layout.addWidget(self.devices_label)
        self.device_selection_layout.addWidget(self.devices_combo)
        return self.device_selection_layout
    
    def half_precision_ui(self):
        self.half_precision_label = QLabel('Half Precision (GPU):')
        self.half_precision_enabled = QRadioButton('Enabled')
        self.half_precision_disabled = QRadioButton('Disabled')

        if self.get_half_precision():
            self.half_precision_enabled.setChecked(True)
        else:
            self.half_precision_disabled.setChecked(True)

        self.half_precision_enabled.toggled.connect(lambda: self.set_half_precision(True))
        self.half_precision_disabled.toggled.connect(lambda: self.set_half_precision(False))

        self.half_precision_layout = QVBoxLayout()
        self.half_precision_layout.addWidget(self.half_precision_label)
        self.half_precision_layout.addWidget(self.half_precision_enabled)
        self.half_precision_layout.addWidget(self.half_precision_disabled)
        return self.half_precision_layout

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
        if self._config.device == 'cpu':
            return 'CPU'
        else:
            device_id = torch.cuda.current_device()
            return 'GPU-{} ({})'.format(device_id, torch.cuda.get_device_name(device_id))

    def set_device(self, value: str):
        if value == 'CPU':
            self._config.device = 'cpu'
        else:
            device_id = int(value.split('-')[1].split(' ')[0])
            self._config.device = 'cuda:{}'.format(device_id)
        logging.debug('Set device to {}'.format(value))

    def get_half_precision(self) -> bool:
        return self._config.half_precision
    
    def set_half_precision(self, value: bool):
        self._config.half_precision = value
