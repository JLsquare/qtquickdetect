from typing import Optional
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidgetItem, QTreeWidget
from ..models.app_state import AppState
from ..utils import filepaths


class ModelsWidget(QWidget):
    """
    ModelsWidget is a QWidget that displays the models and weights available, and if they have been downloaded.
    """
    def __init__(self):
        """
        Initializes the ModelsWidget.
        """
        super().__init__()
        self._tree_widget: Optional[QTreeWidget] = None
        self._appstate: AppState = AppState.get_instance()
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self) -> None:
        """
        Initializes the user interface components.
        """
        layout = QVBoxLayout(self)
        self._tree_widget = QTreeWidget()
        self._tree_widget.setColumnCount(2)
        self._tree_widget.setHeaderLabels([self.tr('Model / Weights'), self.tr('Status / Info')])
        self.populate_tree()
        layout.addWidget(self._tree_widget)
        self.setLayout(layout)

    def populate_tree(self) -> None:
        """
        Populate the tree with the models and weights available.
        """
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
                    child_item.setText(1, self.tr('Downloaded'))
                else:
                    child_item.setText(1, self.tr('Not downloaded'))

    ##############################
    #         CONTROLLER         #
    ##############################

    def showEvent(self, event: QShowEvent) -> None:
        """
        Override the showEvent method to resize the columns to fit the content.

        :param event: The QShowEvent
        """
        super().showEvent(event)
        self._tree_widget.resizeColumnToContents(0)
        self._tree_widget.resizeColumnToContents(1)
