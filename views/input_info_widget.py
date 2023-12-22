from typing import Optional
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal
from PyQt6.QtGui import QFileSystemModel, QPixmap, QImage
from PyQt6.QtWidgets import QTreeView, QWidget, QVBoxLayout, QGraphicsScene, QStyledItemDelegate, QStyleOptionViewItem
from views.resizeable_graphics_widget import ResizeableGraphicsWidget
from pipeline.realtime_detection import MediaFetcher
import os
import cv2


class NoCheckBoxDelegate(QStyledItemDelegate):
    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(option, index)
        if self.parent() and isinstance(self.parent(), QTreeView):
            if self.parent().model().isDir(index):
                option.features &= ~QStyleOptionViewItem.ViewItemFeature.HasCheckIndicator


class CheckableFileSystemModel(QFileSystemModel):
    selection_changed_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.checks = {}
        self.setData(self.index(self.rootPath()), Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)

    def data(self, index: QModelIndex, role: int = None):
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            if self.isDir(index):
                return -1
            else:
                return self.checks.get(index, 2)
        if role == Qt.ItemDataRole.DecorationRole:
            return QPixmap()
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


class InputInfoWidget(QWidget):
    def __init__(self, file_dir: str):
        super().__init__()

        # PyQT6 Components
        self._qtree_view: Optional[QTreeView] = None
        self._no_checkbox_delegate: Optional[NoCheckBoxDelegate] = None
        self._scene: Optional[QGraphicsScene] = None
        self._preview_view: Optional[ResizeableGraphicsWidget] = None
        self._preview_container: Optional[QWidget] = None
        self._preview_layout: Optional[QVBoxLayout] = None
        self._layout: Optional[QVBoxLayout] = None

        self._file_dir = file_dir
        self.model = CheckableFileSystemModel()
        self.model.setRootPath(self._file_dir)
        self._media_fetcher = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self._qtree_view = QTreeView()
        self._qtree_view.setRootIsDecorated(False)
        self._qtree_view.setModel(self.model)
        self._qtree_view.setRootIndex(self.model.index(self._file_dir))
        self._qtree_view.selectionModel().selectionChanged.connect(self.update_preview)
        self._no_checkbox_delegate = NoCheckBoxDelegate(self._qtree_view)
        self._qtree_view.setItemDelegateForColumn(0, self._no_checkbox_delegate)
        self._qtree_view.doubleClicked.connect(self.on_item_clicked)
        for i in range(1, self.model.columnCount()):
            self._qtree_view.hideColumn(i)
        self._qtree_view.setHeaderHidden(True)

        self._scene = QGraphicsScene(self)
        self._preview_view = ResizeableGraphicsWidget(self._scene, self)
        self._preview_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._preview_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._preview_container = QWidget()
        self._preview_layout = QVBoxLayout()
        self._preview_layout.addWidget(self._preview_view)
        self._preview_container.setLayout(self._preview_layout)
        self._preview_container.setProperty('class', 'border')

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._qtree_view, 1)
        self._layout.addWidget(self._preview_container, 1)
        self.setLayout(self._layout)

    ##############################
    #         CONTROLLER         #
    ##############################

    def get_selected_files(self, input_dir: str):
        self.collapse_all()
        self._qtree_view.expand(self.model.index(f'{self._file_dir}/{input_dir}'))
        selected_files = []
        self._get_selected_files_recursive(self.model.index(f'{self._file_dir}/{input_dir}'), selected_files)
        return selected_files

    def collapse_all(self):
        self._qtree_view.collapseAll()

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
            return

        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            self.set_image_preview(file_path)
        elif file_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            self.set_video_preview(file_path)

    def set_image_preview(self, file_path):
        if self._media_fetcher is not None:
            self._media_fetcher.request_cancel()
            self._media_fetcher.wait()
            self._media_fetcher = None
        pixmap = QPixmap(file_path)
        self._scene.clear()
        self._scene.addPixmap(pixmap.scaled(self._preview_view.size(), Qt.AspectRatioMode.KeepAspectRatio))

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
            self._scene.clear()
            self._scene.addPixmap(pixmap.scaled(self._preview_view.size(), Qt.AspectRatioMode.KeepAspectRatio))
        cap.release()

    def set_live_preview(self, live_url):
        if self._media_fetcher is not None and self._media_fetcher.url == live_url:
            return
        if self._media_fetcher is not None:
            self._media_fetcher.request_cancel()
            self._media_fetcher.wait()
            self._media_fetcher = None
        self._media_fetcher = MediaFetcher(live_url, 60)

        def update_frame(frame, frame_available):
            if frame_available:
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
                pixmap = QPixmap.fromImage(q_img)
                self._scene.clear()
                self._scene.addPixmap(pixmap.scaled(self._preview_view.size(), Qt.AspectRatioMode.KeepAspectRatio))

        self._media_fetcher.frame_signal.connect(update_frame)
        self._media_fetcher.start()

    def on_item_double_clicked(self, index):
        if not self.model.isDir(index):
            current_state = self.model.data(index, Qt.ItemDataRole.CheckStateRole)
            new_state = Qt.CheckState.Unchecked if current_state == Qt.CheckState.Checked else Qt.CheckState.Checked
            self.model.setData(index, new_state, Qt.ItemDataRole.CheckStateRole)

    def on_item_clicked(self, index):
        if not self.model.isDir(index):
            current_state = self.model.data(index, Qt.ItemDataRole.CheckStateRole)
            new_state = Qt.CheckState.Unchecked if current_state == Qt.CheckState.Checked else Qt.CheckState.Checked
            self.model.setData(index, new_state, Qt.ItemDataRole.CheckStateRole)
