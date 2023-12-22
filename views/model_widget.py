import logging
from typing import Optional
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from models.project import Project


class ModelWidget(QWidget):
    models_changed_signal = pyqtSignal()

    def __init__(self, project: Project):
        super().__init__()

        # PyQT6 Components
        self._model_icon_layout: Optional[QHBoxLayout] = None
        self._model_icon: Optional[QLabel] = None
        self._model_list: Optional[QListWidget] = None
        self._model_layout: Optional[QVBoxLayout] = None

        self._project = project
        self.models = self._project.config.current_models
        self._model_names = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt']

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Model icon
        self._model_icon_layout = QHBoxLayout()
        self._model_icon_layout.addStretch()
        self._model_icon = QLabel()
        self._model_icon.setPixmap(
            QPixmap('ressources/images/model_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                               Qt.TransformationMode.SmoothTransformation))
        self._model_icon_layout.addWidget(self._model_icon)
        self._model_icon_layout.addStretch()

        # Model List
        def on_item_clicked(clicked_item):
            if clicked_item.checkState() == Qt.CheckState.Unchecked:
                new_state = Qt.CheckState.Checked
            else:
                new_state = Qt.CheckState.Unchecked
            clicked_item.setCheckState(new_state)

        self._model_list = QListWidget()
        for model_name in self._model_names:
            item = QListWidgetItem(model_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if self.models and model_name in self.models:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self._model_list.addItem(item)

        self._model_list.itemChanged.connect(self.check_model_selected)
        self._model_list.itemDoubleClicked.connect(on_item_clicked)

        # Model Layout
        self._model_layout = QVBoxLayout()
        self._model_layout.addLayout(self._model_icon_layout)
        self._model_layout.addWidget(self._model_list)
        self._model_layout.addStretch()

        self.setLayout(self._model_layout)
        self.setFixedSize(240, 240)

    ##############################
    #         CONTROLLER         #
    ##############################

    def check_model_selected(self):
        self.models = []
        for i in range(self._model_list.count()):
            if self._model_list.item(i).checkState() == Qt.CheckState.Checked:
                self.models.append(self._model_list.item(i).text())
        self._project.config.current_models = self.models
        self._project.save()
        logging.debug('Models selected: ' + ', '.join(self.models))
        self.models_changed_signal.emit()
