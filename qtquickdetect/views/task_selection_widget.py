import logging

from typing import Optional
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QRadioButton, QLabel


class TaskSelectionWidget(QWidget):
    task_changed_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.task = 'detect'

        # PyQT6 Components
        self._task_icon_layout: Optional[QHBoxLayout] = None
        self._task_icon: Optional[QLabel] = None
        self._task_radio_layout: Optional[QVBoxLayout] = None
        self._task_radio_detection: Optional[QRadioButton] = None
        self._task_radio_segmentation: Optional[QRadioButton] = None
        self._task_radio_classification: Optional[QRadioButton] = None
        self._task_radio_posing: Optional[QRadioButton] = None
        self._task_radio_widget: Optional[QWidget] = None
        self._task_layout: Optional[QVBoxLayout] = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Task icon
        self._task_icon_layout = QHBoxLayout()
        self._task_icon_layout.addStretch()
        self._task_icon = QLabel()
        self._task_icon.setPixmap(
            QPixmap('ressources/images/task_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                              Qt.TransformationMode.SmoothTransformation))
        self._task_icon_layout.addWidget(self._task_icon)
        self._task_icon_layout.addStretch()

        # Task Radio Buttons
        self._task_radio_layout = QVBoxLayout()
        self._task_radio_detection = QRadioButton(self.tr('Detect'))
        self._task_radio_segmentation = QRadioButton(self.tr('Segment'))
        self._task_radio_classification = QRadioButton(self.tr('Classify'))
        self._task_radio_posing = QRadioButton(self.tr('Pose'))

        self._task_radio_detection.setObjectName('detect')
        self._task_radio_segmentation.setObjectName('segment')
        self._task_radio_classification.setObjectName('classify')
        self._task_radio_posing.setObjectName('pose')

        self._task_radio_detection.toggled.connect(self._check_task_selected)
        self._task_radio_segmentation.toggled.connect(self._check_task_selected)
        self._task_radio_classification.toggled.connect(self._check_task_selected)
        self._task_radio_posing.toggled.connect(self._check_task_selected)

        if self.task == 'detect':
            self._task_radio_detection.setChecked(True)
        elif self.task == 'segment':
            self._task_radio_segmentation.setChecked(True)
        elif self.task == 'classify':
            self._task_radio_classification.setChecked(True)
        elif self.task == 'pose':
            self._task_radio_posing.setChecked(True)

        self._task_radio_layout.addWidget(self._task_radio_detection)
        self._task_radio_layout.addWidget(self._task_radio_segmentation)
        self._task_radio_layout.addWidget(self._task_radio_classification)
        self._task_radio_layout.addWidget(self._task_radio_posing)
        self._task_radio_layout.addStretch()
        self._task_radio_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._task_radio_widget = QWidget()
        self._task_radio_widget.setLayout(self._task_radio_layout)
        self._task_radio_widget.setProperty('class', 'border')

        # Description
        self._description = QLabel(self.tr('Select a task, <a href="https://docs.ultralytics.com/tasks/">more</a>'))
        self._description.setOpenExternalLinks(True)
        self._description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._description.setProperty('class', 'description')

        # Task Layout
        self._task_layout = QVBoxLayout()
        self._task_layout.addLayout(self._task_icon_layout)
        self._task_layout.addWidget(self._task_radio_widget)
        self._task_layout.addWidget(self._description)

        self.setLayout(self._task_layout)
        self.setFixedSize(240, 360)

    ##############################
    #         CONTROLLER         #
    ##############################

    def _check_task_selected(self):
        if self._task_radio_detection.isChecked():
            self.task = 'detect'
        elif self._task_radio_segmentation.isChecked():
            self.task = 'segment'
        elif self._task_radio_classification.isChecked():
            self.task = 'classify'
        elif self._task_radio_posing.isChecked():
            self.task = 'pose'
        logging.debug('Task selected: ' + self.task)
        self.task_changed_signal.emit()
