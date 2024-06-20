from typing import Optional
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QSizePolicy, QRadioButton, \
    QButtonGroup, QHBoxLayout
from ..utils import filepaths
from ..models.app_state import AppState


class ModelsSelectionWidget(QWidget):
    """
    ModelsSelectionWidget is a QWidget that allows the user to select models and weights for the specified task.
    """
    models_changed_signal = pyqtSignal()

    def __init__(self, single_weight: bool = False):
        """
        Initializes the ModelsSelectionWidget.
        """
        super().__init__()
        self.app_state: AppState = AppState.get_instance()
        self.weights: dict[str, dict[str, list[str]]] = {}
        self.task: str = 'detect'
        self.single_weight = single_weight

        # PyQT6 Components
        self._model_icon_layout: Optional[QHBoxLayout] = None
        self._model_icon: Optional[QLabel] = None
        self._model_tree: Optional[QTreeWidget] = None
        self._model_layout: Optional[QVBoxLayout] = None
        self._model_description: Optional[QLabel] = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self) -> None:
        """
        Initializes the user interface components.
        """
        # Model icon
        self._model_icon_layout = QHBoxLayout()
        self._model_icon_layout.addStretch()
        self._model_icon = QLabel()
        image_name = f"{self.app_state.get_theme_file_prefix()}model.png"
        self._model_icon.setPixmap(
            QPixmap(str(filepaths.get_app_dir() / 'resources' / 'images' / image_name))
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
        self._model_description = QLabel(self.tr('Select the models weights'))
        self._model_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._model_description.setProperty('class', 'description')

        # Model Layout
        self._model_layout = QVBoxLayout()
        self._model_layout.addLayout(self._model_icon_layout)
        self._model_layout.addWidget(self._model_tree)
        self._model_layout.addWidget(self._model_description)

        self.setLayout(self._model_layout)
        self.setFixedHeight(360)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def populate_model_tree(self) -> None:
        """
        Dynamically load models and weights from appstate.config
        """
        radio_button_group = QButtonGroup(self)
        radio_button_group.setExclusive(True)

        for model_key, model_info in self.app_state.app_config.models.items():
            if self.task != self.app_state.app_config.models[model_key]["task"]:
                continue

            parent_item = QTreeWidgetItem(self._model_tree, [model_key])
            has_children_checked = False

            for model_builders, weights in model_info["model_builders"].items():
                child_item = QTreeWidgetItem(parent_item, [model_builders])

                """
                if self.single_weight:
                    radio_button = QRadioButton(model_builders)
                    # to fix the text cropping at the bottom (temp fix?)
                    radio_button.setMinimumHeight(30)
                    radio_button_group.addButton(radio_button)

                    layout = QHBoxLayout()
                    layout.addWidget(radio_button)

                    widget = QWidget()
                    widget.setLayout(layout)

                    layout.setContentsMargins(0, 0, 0, 0)
                    self._model_tree.setItemWidget(child_item, 0, widget)

                    radio_button.toggled.connect(lambda checked, k=model_key, w=model_builders: self.radio_toggled(checked, k, w))
                else:
                    child_item.setFlags(child_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    child_item.setCheckState(0, Qt.CheckState.Unchecked)
                """
                for weight in weights:
                    sub_child_item = QTreeWidgetItem(child_item, [weight])
                    if self.single_weight:
                        radio_button = QRadioButton(weight)
                        radio_button.setMinimumHeight(30)
                        radio_button_group.addButton(radio_button)

                        layout = QHBoxLayout()
                        layout.addWidget(radio_button)

                        widget = QWidget()
                        widget.setLayout(layout)

                        layout.setContentsMargins(0, 0, 0, 0)
                        self._model_tree.setItemWidget(sub_child_item, 0, widget)

                        radio_button.toggled.connect(
                            lambda checked, m=model_key, b=model_builders, w=weight: self.radio_toggled(checked, m, b, w)
                        )
                    else:
                        sub_child_item.setFlags(sub_child_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        sub_child_item.setCheckState(0, Qt.CheckState.Unchecked)

            if has_children_checked:
                parent_item.setExpanded(True)

    ##############################
    #         CONTROLLER         #
    ##############################

    def check_model_selected(self) -> None:
        """
        Checks if a model or weight is selected.
        """
        selected_weights = {}  # type: dict[str, dict[str, list[str]]]
        root = self._model_tree.invisibleRootItem()
        model_count = root.childCount()

        # Iterate over models
        for i in range(model_count):
            model_item = root.child(i)
            model_name = model_item.text(0)

            # Iterate over model builders
            for j in range(model_item.childCount()):
                model_builder_item = model_item.child(j)
                model_builder_name = model_builder_item.text(0)
                weights_selected = []

                # Iterate over weights
                for k in range(model_builder_item.childCount()):
                    weight_item = model_builder_item.child(k)
                    if weight_item.checkState(0) == Qt.CheckState.Checked:
                        weights_selected.append(weight_item.text(0))

                if weights_selected:
                    if model_name not in selected_weights:
                        selected_weights[model_name] = {}
                    selected_weights[model_name][model_builder_name] = weights_selected

        self.weights = selected_weights
        self.models_changed_signal.emit()

    def radio_toggled(self, checked: bool, model_key: str, model_builder: str, weight: str) -> None:
        """
        Handle radio button toggled event.
        """
        if checked:
            self.weights = {model_key: {model_builder: [weight]}}  # Only one weight can be selected at a time
            self.models_changed_signal.emit()

    def set_task(self, task: str) -> None:
        """
        Sets the task for the models selection widget.
        """
        self.task = task
        self._model_tree.clear()
        self.populate_model_tree()
        self.models_changed_signal.emit()
