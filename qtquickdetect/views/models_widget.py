from typing import Optional
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidgetItem, QTreeWidget
from ..models.app_state import AppState
from ..utils import filepaths


class ModelsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._tree_widget: Optional[QTreeWidget] = None
        self._appstate = AppState.get_instance()
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        layout = QVBoxLayout(self)
        self._tree_widget = QTreeWidget()
        self._tree_widget.setColumnCount(2)
        self._tree_widget.setHeaderLabels(['Model / Weights', 'Status / Info'])
        self.populate_tree()
        layout.addWidget(self._tree_widget)
        self.setLayout(layout)

    def populate_tree(self):
        models_config = self._appstate.app_config.models
        project_root = filepaths.get_app_dir()
        for model_name, model_details in models_config.items():
            parent_item = QTreeWidgetItem(self._tree_widget)
            parent_item.setText(0, model_name)
            parent_item.setText(1, f"Pipeline - {model_details['pipeline']}, Task - {model_details['task']}")
            for weight in model_details['weights']:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, weight)
                file_path = project_root / weight
                if file_path.exists():
                    child_item.setText(1, 'Downloaded')
                else:
                    child_item.setText(1, 'Not downloaded')

    ##############################
    #         CONTROLLER         #
    ##############################

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        self._tree_widget.resizeColumnToContents(0)
        self._tree_widget.resizeColumnToContents(1)
