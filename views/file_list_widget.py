from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal
from PyQt6.QtGui import QFileSystemModel, QPixmap, QImage
from PyQt6.QtWidgets import QTreeView, QLabel, QWidget, QVBoxLayout
from pipeline.realtime_detection import MediaFetcher
import logging
import os
import cv2


class CheckableFileSystemModel(QFileSystemModel):
    selection_changed_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.checks = {}

    def data(self, index: QModelIndex, role: int = None):
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            if self.isDir(index):
                return -1
            else:
                return self.checks.get(index, 2)
        return super().data(index, role)

    def setData(self, index: QModelIndex, value, role: int = None):
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            self.checks[index] = value
            self.dataChanged.emit(index, index, [role])
            self.selection_changed_signal.emit()
            return True
        return super().setData(index, value, role)

    def flags(self, index):
        return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable


class FileListWidget(QWidget):
    def __init__(self, file_dir: str):
        super().__init__()

        self._preview_label = None
        self._file_dir = file_dir
        logging.debug('FileListWidget: ' + self._file_dir)

        self.model = CheckableFileSystemModel()
        self.model.setRootPath(self._file_dir)

        self._qtree_view = QTreeView()
        self._qtree_view.setModel(self.model)
        self._qtree_view.setRootIndex(self.model.index(self._file_dir))
        self._qtree_view.selectionModel().selectionChanged.connect(self.update_preview)

        self._media_fetcher = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        for i in range(1, self.model.columnCount()):
            self._qtree_view.hideColumn(i)
        self._qtree_view.setHeaderHidden(True)

        preview_label = QLabel("Select a file to see its preview.")
        preview_label.setWordWrap(True)
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label = preview_label

        layout = QVBoxLayout()
        layout.addWidget(self._qtree_view, 1)
        layout.addWidget(self._preview_label, 1)
        self.setLayout(layout)

    ##############################
    #         CONTROLLER         #
    ##############################

    def get_selected_files(self):
        selected_files = []
        self._get_selected_files_recursive(self.model.index(self._file_dir), selected_files)
        logging.debug('FileListWidget: ' + str(selected_files))
        return selected_files

    def _get_selected_files_recursive(self, index, selected_files):
        if self.model.data(index, Qt.ItemDataRole.CheckStateRole) == 2:
            selected_files.append(self.model.filePath(index))

        if self.model.hasChildren(index):
            for row in range(self.model.rowCount(index)):
                child_index = self.model.index(row, 0, index)
                self._get_selected_files_recursive(child_index, selected_files)

    def update_preview(self, selected):
        indexes = selected.indexes()
        if not indexes:
            return

        file_path = self.model.filePath(indexes[0])
        if not os.path.isfile(file_path):
            self._preview_label.setText("This is a directory.")
            return

        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            self.set_image_preview(file_path)
        elif file_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            self.set_video_preview(file_path)
        else:
            self._preview_label.setText("Cannot preview this file type.")

    def set_image_preview(self, file_path):
        if self._media_fetcher is not None:
            self._media_fetcher.request_cancel()
            self._media_fetcher.wait()
            self._media_fetcher = None
        pixmap = QPixmap(file_path)
        self._preview_label.setPixmap(pixmap.scaled(self._preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def set_video_preview(self, file_path):
        if self._media_fetcher is not None:
            self._media_fetcher.request_cancel()
            self._media_fetcher.wait()
            self._media_fetcher = None
        cap = cv2.VideoCapture(file_path)
        success, frame = cap.read()
        if success:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(q_img)
            self._preview_label.setPixmap(pixmap.scaled(self._preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self._preview_label.setText("Cannot preview video.")
        cap.release()

    def set_live_preview(self, live_url):
        self._media_fetcher = MediaFetcher(live_url, 1)

        def update_frame(frame, frame_available):
            if frame_available:
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
                pixmap = QPixmap.fromImage(q_img)
                self._preview_label.setPixmap(pixmap.scaled(self._preview_label.size(),
                                                            Qt.AspectRatioMode.KeepAspectRatio))

        self._media_fetcher.frame_signal.connect(update_frame)
        self._media_fetcher.start()
