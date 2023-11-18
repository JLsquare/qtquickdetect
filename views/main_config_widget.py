from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QRadioButton
from PyQt6.QtCore import Qt
from models.config_file import ConfigFile
import torch
import logging


class MainConfigWidget(QWidget):
    def __init__(self, config: ConfigFile):
        super().__init__()
        self._config = config
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(self.device_selection_ui())
        main_layout.addLayout(self.half_precision_ui())
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
    
    def half_precision_ui(self):
        half_precision_label = QLabel('Half Precision (GPU):')
        half_precision_enabled = QRadioButton('Enabled')
        half_precision_disabled = QRadioButton('Disabled')

        if self.get_half_precision():
            half_precision_enabled.setChecked(True)
        else:
            half_precision_disabled.setChecked(True)

        half_precision_enabled.toggled.connect(lambda: self.set_half_precision(True))
        half_precision_disabled.toggled.connect(lambda: self.set_half_precision(False))

        half_precision_layout = QVBoxLayout()
        half_precision_layout.addWidget(half_precision_label)
        half_precision_layout.addWidget(half_precision_enabled)
        half_precision_layout.addWidget(half_precision_disabled)
    
        return half_precision_layout

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
