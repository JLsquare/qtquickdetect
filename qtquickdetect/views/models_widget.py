import logging
import shutil

from pathlib import Path
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QShowEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidgetItem, QTreeWidget, QFileDialog
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
        self._tree_widget.setHeaderLabels(['Model / Weights', 'Status / Info', 'Action'])
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
                child_item.setText(0, weight['name'])
                file_path = project_root / weight['name']
                if file_path.exists():
                    if weight['type'] == 'custom':
                        child_item.setText(1, 'Custom')
                    else:
                        child_item.setText(1, 'Downloaded')
                else:
                    child_item.setText(1, 'Not downloaded')
                    child_item.setIcon(2, QIcon('ressources/images/download_icon.png'))
            child_item = QTreeWidgetItem(parent_item)
            child_item.setText(0, 'Add new weights')
            child_item.setIcon(2, QIcon('ressources/images/add_icon.png'))
        self._tree_widget.itemClicked.connect(self.handle_item_clicked)

    ##############################
    #         CONTROLLER         #
    ##############################

    def handle_item_clicked(self, item: QTreeWidgetItem, column: int):
        if column == 2:
            model_name = item.parent().text(0) if item.parent() else item.text(0)
            if item.text(0) == "Add new weights":
                self.add_new_weights(model_name)
            else:
                weight_file = item.text(0)
                self.download_weights(model_name, weight_file)

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        self._tree_widget.resizeColumnToContents(0)
        self._tree_widget.resizeColumnToContents(1)

    @staticmethod
    def download_weights(model_name: str, weight_file: str):
        logging.info(f"Downloading weights for model {model_name} - {weight_file}")
        pass

    def add_new_weights(self, model_name: str):
        logging.info(f"Adding new weights for model {model_name}")

        file_name, _ = QFileDialog.getOpenFileName(self, "Select Weight File", "",
                                                   "Pytorch (*.pt);;All Files (*)",
                                                   options=QFileDialog.Option.DontUseNativeDialog)
        if file_name:
            project_root = filepaths.get_app_dir()
            shutil.copyfile(file_name, project_root / Path(file_name).name)
            if model_name in self._appstate.app_config.weights:
                model_details = self._appstate.app_config.weights[model_name]
                if Path(file_name).name not in model_details['weights']:
                    new_weight = {
                        'name': Path(file_name).name,
                        'type': 'custom',
                        'enabled': 'true'
                    }
                    model_details['weights'].append(new_weight)
                    self._appstate.app_config.save()
                    parent_item = self._tree_widget.findItems(model_name, Qt.MatchFlag.MatchExactly, 0)[0]
                    child_item = QTreeWidgetItem()
                    child_item.setText(0, new_weight['name'])
                    child_item.setText(1, 'Custom')
                    parent_item.insertChild(parent_item.childCount() - 1, child_item)
                else:
                    logging.info("Weight file already exists in the list.")
            else:
                logging.warning(f"Model {model_name} not found in configuration.")
