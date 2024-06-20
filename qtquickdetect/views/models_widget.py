from typing import Optional
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidgetItem, QTreeWidget,
                             QHBoxLayout, QFileDialog, QMessageBox, QPushButton)
from ..models.app_state import AppState
from ..utils import filepaths
import shutil
import os


class ModelsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.app_state: AppState = AppState.get_instance()

        self._layout: Optional[QVBoxLayout] = None
        self._tree_widget: Optional[QTreeWidget] = None
        self._delete_button: Optional[QPushButton] = None
        self._open_config_button: Optional[QPushButton] = None

        self.init_ui()

    def init_ui(self) -> None:
        self._layout = QVBoxLayout(self)
        self._tree_widget = QTreeWidget()
        self._tree_widget.setColumnCount(2)
        self._tree_widget.setHeaderLabels(
            [self.tr('Model / Model builder / Weight'), self.tr('Pipeline / Task / Info')])
        self.populate_tree()
        self._tree_widget.itemClicked.connect(self.on_item_clicked)
        self._tree_widget.itemSelectionChanged.connect(self.update_delete_button_state)
        self._layout.addWidget(self._tree_widget)

        button_layout = QHBoxLayout()

        self._open_config_button = QPushButton("Open App Config")
        self._open_config_button.clicked.connect(self.open_app_config)
        button_layout.addWidget(self._open_config_button)

        self._delete_button = QPushButton("Delete Selected Weight")
        self._delete_button.setEnabled(False)
        self._delete_button.clicked.connect(self.delete_selected_weight)
        self._delete_button.setProperty("class", "red")
        button_layout.addWidget(self._delete_button)

        self._layout.addLayout(button_layout)
        self.setLayout(self._layout)

    def populate_tree(self) -> None:
        models_config = self.app_state.app_config.models
        for model_name, model_details in models_config.items():
            parent_item = QTreeWidgetItem(self._tree_widget)
            parent_item.setText(0, model_name)
            parent_item.setText(1, f"Pipeline - {model_details['pipeline']}, Task - {model_details['task']}")
            for model_builders, weights in model_details['model_builders'].items():
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, model_builders)
                for weight in weights:
                    sub_child_item = QTreeWidgetItem(child_item)
                    sub_child_item.setText(0, weight)
                add_weight_item = QTreeWidgetItem(child_item)
                add_weight_item.setText(0, 'Add weight')
                add_weight_item.setText(1, 'Click to add a weight')

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._tree_widget.resizeColumnToContents(0)
        self._tree_widget.resizeColumnToContents(1)

    def on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        if item.text(0) == 'Add weight' and item.text(1) == 'Click to add a weight':
            model_name = item.parent().parent().text(0)
            model_builder = item.parent().text(0)

            weights_path = filepaths.get_base_data_dir() / 'weights'

            # Open file selection dialog
            file_dialog = QFileDialog(self)
            file_dialog.setNameFilter("Weight files (*.pt *.pth)")
            if file_dialog.exec():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    source_path = selected_files[0]
                    file_name = os.path.basename(source_path)
                    destination_path = weights_path / file_name

                    try:
                        shutil.copy2(source_path, destination_path)
                        self.app_state.app_config.models[model_name]['model_builders'][model_builder].append(file_name)
                        self.app_state.save()

                        new_weight_item = QTreeWidgetItem(item.parent())
                        new_weight_item.setText(0, file_name)

                        QMessageBox.information(self, "Success", f"Weight file '{file_name}' added successfully.")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to add weight file: {str(e)}")

    def update_delete_button_state(self) -> None:
        selected_items = self._tree_widget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            # Enable delete button only if a weight is selected
            self._delete_button.setEnabled(selected_item.parent() is not None and
                                           selected_item.parent().parent() is not None and
                                           selected_item.text(0) != 'Add weight')
        else:
            self._delete_button.setEnabled(False)

    def delete_selected_weight(self) -> None:
        selected_items = self._tree_widget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            weight_name = selected_item.text(0)
            model_builder = selected_item.parent().text(0)
            model_name = selected_item.parent().parent().text(0)

            reply = QMessageBox.question(self, 'Delete Weight',
                                         f"Are you sure you want to delete the weight '{weight_name}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # Remove the weight file
                    weights_path = filepaths.get_base_data_dir() / 'weights'
                    weight_file_path = weights_path / weight_name
                    if os.path.exists(weight_file_path):
                        os.remove(weight_file_path)

                    self.app_state.app_config.models[model_name]['model_builders'][model_builder].remove(weight_name)
                    self.app_state.save()

                    selected_item.parent().removeChild(selected_item)

                    QMessageBox.information(self, "Success", f"Weight file '{weight_name}' deleted successfully.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete weight file: {str(e)}")

    def open_app_config(self) -> None:
        try:
            self.app_state.app_config.open_config()
            QMessageBox.information(self, "Success", "App config JSON opened successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open app config: {str(e)}")
