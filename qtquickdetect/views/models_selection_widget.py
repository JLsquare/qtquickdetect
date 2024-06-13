from typing import Optional
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QTreeWidget, QTreeWidgetItem, \
    QSizePolicy
from ..utils import filepaths
from ..models.app_state import AppState


class ModelsSelectionWidget(QWidget):
    models_changed_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.appstate = AppState.get_instance()
        self.weights = {}
        self.task = 'detect'

        # PyQT6 Components
        self._model_icon_layout: Optional[QHBoxLayout] = None
        self._model_icon: Optional[QLabel] = None
        self._model_tree: Optional[QListWidget] = None
        self._model_layout: Optional[QVBoxLayout] = None

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
            QPixmap(str(filepaths.get_app_dir() / 'ressources' / 'images' / 'model_icon.png'))
            .scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )
        self._model_icon_layout.addWidget(self._model_icon)
        self._model_icon_layout.addStretch()

        # Model Tree
        self._model_tree = QTreeWidget()
        self._model_tree.setHeaderHidden(True)
        self._model_tree.setColumnCount(1)
        self.populate_model_tree()
        self._model_tree.itemChanged.connect(self.check_model_selected)

        # Description
        self._description = QLabel('Select the models weights')
        self._description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._description.setProperty('class', 'description')

        # Model Layout
        self._model_layout = QVBoxLayout()
        self._model_layout.addLayout(self._model_icon_layout)
        self._model_layout.addWidget(self._model_tree)
        self._model_layout.addWidget(self._description)

        self.setLayout(self._model_layout)
        self.setFixedSize(240, 360)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def populate_model_tree(self):
        """Dynamically load models and weights from appstate.config"""
        for model_key, model_info in self.appstate.app_config.models.items():
            if self.task != self.appstate.app_config.models[model_key]["task"]:
                continue

            parent_item = QTreeWidgetItem(self._model_tree, [model_key])
            has_children_checked = False

            for weight in model_info["weights"]:
                child_item = QTreeWidgetItem(parent_item, [weight["name"]])
                child_item.setFlags(child_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                if model_key in self.weights and weight["name"] in self.weights[model_key]:
                    child_item.setCheckState(0, Qt.CheckState.Checked)
                    has_children_checked = True
                else:
                    child_item.setCheckState(0, Qt.CheckState.Unchecked)

            if has_children_checked:
                parent_item.setExpanded(True)

    ##############################
    #         CONTROLLER         #
    ##############################

    def check_model_selected(self):
        selected_models = {}
        root = self._model_tree.invisibleRootItem()
        model_count = root.childCount()

        # Iterate over models
        for i in range(model_count):
            model_item = root.child(i)
            model_name = model_item.text(0)
            weights_selected = []

            # Iterate over weights
            for j in range(model_item.childCount()):
                weight_item = model_item.child(j)
                if weight_item.checkState(0) == Qt.CheckState.Checked:
                    weights_selected.append(weight_item.text(0))

            if weights_selected:
                selected_models[model_name] = weights_selected

        self.weights = selected_models
        self.models_changed_signal.emit()

    def set_task(self, task: str):
        self.task = task
        self._model_tree.clear()
        self.populate_model_tree()
        self.models_changed_signal.emit()

