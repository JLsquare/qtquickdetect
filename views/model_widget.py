import logging
from typing import Optional
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem
from models.project import Project
from models.app_state import AppState


class ModelWidget(QWidget):
    models_changed_signal = pyqtSignal()

    def __init__(self, project: Project):
        super().__init__()
        self._appstate = AppState.get_instance()

        # PyQT6 Components
        self._model_icon_layout: Optional[QHBoxLayout] = None
        self._model_icon: Optional[QLabel] = None
        self._model_tree: Optional[QListWidget] = None
        self._model_layout: Optional[QVBoxLayout] = None

        self._project = project
        self.models = self._project.config.current_models

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

        # Model Tree
        self._model_tree = QTreeWidget()
        self._model_tree.setHeaderHidden(True)
        self._model_tree.setColumnCount(1)

        self.populate_model_tree()

        self._model_tree.itemChanged.connect(self.check_model_selected)

        # Model Layout
        self._model_layout = QVBoxLayout()
        self._model_layout.addLayout(self._model_icon_layout)
        self._model_layout.addWidget(self._model_tree)
        self._model_layout.addStretch()

        self.setLayout(self._model_layout)
        self.setFixedSize(240, 240)

    def populate_model_tree(self):
        """Dynamically load models and weights from appstate.config"""
        for model_key, model_info in self._appstate.config.models.items():
            if self._project.config.current_task not in self._appstate.config.models[model_key]["tasks"]:
                continue

            parent_item = QTreeWidgetItem(self._model_tree, [model_key])
            has_children_checked = False

            for weight in model_info["weights"]:
                child_item = QTreeWidgetItem(parent_item, [weight])
                child_item.setFlags(child_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                if self.models and model_key in self.models and weight in self.models[model_key]:
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

        self.models = selected_models
        logging.debug('Models and weights selected: ' + str(selected_models))
        self._project.config.current_models = selected_models
        self._project.config.save()
        self.models_changed_signal.emit()

    def update_models(self):
        self._model_tree.clear()
        self.populate_model_tree()
        self.models_changed_signal.emit()