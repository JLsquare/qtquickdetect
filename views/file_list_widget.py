import os
import cv2
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QFileSystemModel, QPixmap, QImage
from PyQt6.QtWidgets import QTreeView, QLabel, QWidget, QVBoxLayout
import logging


class CheckableFileSystemModel(QFileSystemModel):
    def __init__(self):
        super().__init__()
        self.checks = {}

    def data(self, index: QModelIndex, role: int = None):
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            return self.checks.get(index, Qt.CheckState.Unchecked)
        return super().data(index, role)

    def setData(self, index: QModelIndex, value, role: int = None):
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            self.checks[index] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return super().setData(index, value, role)

    def flags(self, index):
        return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable


class FileListWidget(QWidget):

    def __init__(self, file_dir: str):
        super().__init__()

        self._file_dir = file_dir
        self._preview_label = QLabel("Select a file to see its preview.")
        self._preview_label.setWordWrap(True)
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logging.debug('FileListWidget: ' + self._file_dir)
        self._model = CheckableFileSystemModel()
        self._model.setRootPath(self._file_dir)
        self._qtree_view = QTreeView()
        self._qtree_view.setModel(self._model)
        self._qtree_view.setRootIndex(self._model.index(self._file_dir))
        self._qtree_view.selectionModel().selectionChanged.connect(self.update_preview)

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        for i in range(1, self._model.columnCount()):
            self._qtree_view.hideColumn(i)
        self._qtree_view.setHeaderHidden(True)

        layout = QVBoxLayout()
        layout.addWidget(self._qtree_view, 1)
        layout.addWidget(self._preview_label, 1)
        self.setLayout(layout)

    ##############################
    #         CONTROLLER         #
    ##############################

    def get_selected_files(self):
        selected_files = []
        self._get_selected_files_recursive(self._model.index(self._file_dir), selected_files)
        logging.debug('FileListWidget: ' + str(selected_files))
        return selected_files

    def _get_selected_files_recursive(self, index, selected_files):
        if self._model.data(index, Qt.ItemDataRole.CheckStateRole) == 2:
            selected_files.append(self._model.filePath(index))

        if self._model.hasChildren(index):
            for row in range(self._model.rowCount(index)):
                child_index = self._model.index(row, 0, index)
                self._get_selected_files_recursive(child_index, selected_files)

    def update_preview(self, selected):
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            file_path = self._model.filePath(index)

            if os.path.isfile(file_path):
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    pixmap = QPixmap(file_path)
                    self._preview_label.setPixmap(
                        pixmap.scaled(self._preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
                elif file_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):  # Add other video formats as needed
                    cap = cv2.VideoCapture(file_path)
                    success, frame = cap.read()
                    if success:
                        height, width, channel = frame.shape
                        bytes_per_line = 3 * width
                        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
                        pixmap = QPixmap.fromImage(q_img)
                        self._preview_label.setPixmap(
                            pixmap.scaled(self._preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
                    else:
                        self._preview_label.setText("Cannot preview video.")
                    cap.release()
                else:
                    self._preview_label.setText("Cannot preview this file type.")
            else:
                self._preview_label.setText("This is a directory.")
