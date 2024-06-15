import shutil

from pathlib import Path
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QListWidget, QHBoxLayout, QListWidgetItem, QLineEdit, QVBoxLayout, QSplitter, \
    QSizePolicy, QPushButton, QGraphicsScene, QGraphicsPixmapItem, QFileDialog
from ..models.app_state import AppState
from ..views.resizeable_graphics_widget import ResizeableGraphicsWidget


class CollectionsWidget(QWidget):
    def __init__(self, media_type: str):
        """
        Initializes the CollectionsWidget

        :param media_type: The type of media to display
        """
        super().__init__()
        self.media_type: str = media_type
        self.app_state: AppState = AppState.get_instance()

        # PyQT6 Components
        self._file_preview_container_widget: Optional[QWidget] = None
        self._file_preview_container_layout: Optional[QVBoxLayout] = None
        self._file_preview_scene: Optional[QGraphicsScene] = None
        self._file_preview_view: Optional[ResizeableGraphicsWidget] = None
        self._collection_list: Optional[QListWidget] = None
        self._add_collection_button: Optional[QPushButton] = None
        self._collection_list_layout: Optional[QVBoxLayout] = None
        self._collection_file_list: Optional[QListWidget] = None
        self._collection_button_layout: Optional[QVBoxLayout] = None
        self._delete_collection_button: Optional[QPushButton] = None
        self._delete_file_button: Optional[QPushButton] = None
        self._add_folder_button: Optional[QPushButton] = None
        self._add_file_button: Optional[QPushButton] = None
        self._v_files_widget: Optional[QWidget] = None
        self._v_files_layout: Optional[QVBoxLayout] = None
        self._h_files_layout: Optional[QSplitter] = None
        self._collection_name_field: Optional[QLineEdit] = None
        self._collection_layout: Optional[QVBoxLayout] = None
        self._main_layout: Optional[QHBoxLayout] = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self) -> None:
        """
        Initializes the UI
        """
        self._main_layout = QHBoxLayout()
        self._v_files_layout = QVBoxLayout()
        self._v_files_layout.addWidget(self.file_preview(''))
        self._v_files_layout.addLayout(self.collection_buttons())
        self._v_files_widget = QWidget()
        self._v_files_widget.setLayout(self._v_files_layout)
        self._h_files_layout = QSplitter(Qt.Orientation.Horizontal)
        self._h_files_layout.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._h_files_layout.addWidget(self.collection_file_list_ui())
        self._h_files_layout.addWidget(self._v_files_widget)
        self._h_files_layout.setSizes([int(self._h_files_layout.size().width() / 2)] * 2)
        self._collection_layout = QVBoxLayout()
        self._collection_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._collection_name_field = QLineEdit()
        self._collection_name_field.textChanged.connect(self.rename_collection)
        self._collection_layout.addWidget(self._collection_name_field)
        self._collection_layout.addWidget(self._h_files_layout)
        self._main_layout.addLayout(self.collection_list_ui())
        self._main_layout.addLayout(self._collection_layout, 1)
        self.setLayout(self._main_layout)

    def collection_list_ui(self) -> QVBoxLayout:
        """
        Creates the collection list UI

        :return: The collection list layout
        """
        self._collection_list_layout = QVBoxLayout()
        self._collection_list = QListWidget()
        for collection in self.app_state.collections.get_collections(self.media_type):
            item = QListWidgetItem(collection)
            item.setData(0, collection)
            self._collection_list.addItem(item)
        self._collection_list.itemClicked.connect(self.collection_selected)
        self._add_collection_button = QPushButton('Add Collection')
        self._add_collection_button.clicked.connect(self.add_collection)
        self._collection_list_layout.addWidget(self._collection_list)
        self._collection_list_layout.addWidget(self._add_collection_button)
        return self._collection_list_layout

    def collection_file_list_ui(self) -> QListWidget:
        """
        Creates the collection file list UI

        :return: The collection file list layout
        """
        self._collection_file_list = QListWidget()
        self._collection_file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._collection_file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._collection_file_list.itemClicked.connect(self.file_selected)
        return self._collection_file_list

    def file_preview(self, input_image: str) -> QWidget:
        """
        Creates the file preview UI

        :param input_image: The image to preview
        :return: The file preview layout
        """
        self._file_preview_container_widget = QWidget(self)
        self._file_preview_container_layout = QVBoxLayout(self._file_preview_container_widget)
        self._file_preview_scene = QGraphicsScene(self._file_preview_container_widget)
        base_image_pixmap = QPixmap(input_image)
        base_image_item = QGraphicsPixmapItem(base_image_pixmap)
        self._file_preview_scene.addItem(base_image_item)
        self._file_preview_view = ResizeableGraphicsWidget(self._file_preview_scene, self._file_preview_container_widget)
        self._file_preview_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._file_preview_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._file_preview_container_layout.addWidget(self._file_preview_view)
        self._file_preview_container_widget.setLayout(self._file_preview_container_layout)
        self._file_preview_container_widget.setProperty('class', 'border')
        return self._file_preview_container_widget

    def collection_buttons(self) -> QVBoxLayout:
        """
        Creates the collection buttons UI

        :return: The collection buttons layout
        """
        self._collection_button_layout = QVBoxLayout()
        self._add_file_button = QPushButton('Add File(s)')
        self._add_file_button.setProperty('class', 'blue')
        self._add_file_button.setEnabled(False)
        self._add_file_button.clicked.connect(self.add_files)
        self._add_folder_button = QPushButton('Add Folder(s)')
        self._add_folder_button.setProperty('class', 'blue')
        self._add_folder_button.setEnabled(False)
        self._add_folder_button.clicked.connect(self.add_folder)
        self._delete_file_button = QPushButton('Delete Selected File(s)')
        self._delete_file_button.setProperty('class', 'red')
        self._delete_file_button.setEnabled(False)
        self._delete_file_button.clicked.connect(self.delete_files)
        self._delete_collection_button = QPushButton('Delete Collection')
        self._delete_collection_button.setProperty('class', 'red')
        self._delete_collection_button.setEnabled(False)
        self._delete_collection_button.clicked.connect(self.delete_collection)
        self._collection_button_layout.addWidget(self._add_file_button)
        self._collection_button_layout.addWidget(self._add_folder_button)
        self._collection_button_layout.addWidget(self._delete_file_button)
        self._collection_button_layout.addWidget(self._delete_collection_button)
        return self._collection_button_layout

    ##############################
    #         CONTROLLER         #
    ##############################

    def collection_selected(self, item: QListWidgetItem) -> None:
        """
        Updates the collection file list and collection name field when a collection is selected

        :param item: The selected collection item
        """
        collection = item.data(0)
        self._collection_file_list.clear()
        files = self.app_state.collections.get_collection_file_paths(collection, self.media_type)
        for file in files:
            file_name = file.name
            list_item = QListWidgetItem(file_name)
            list_item.setData(1, file)
            self._collection_file_list.addItem(list_item)
        self._collection_name_field.setText(collection)
        self._add_file_button.setEnabled(True)
        self._add_folder_button.setEnabled(True)
        self._delete_file_button.setEnabled(True)
        self._delete_collection_button.setEnabled(True)

    def file_selected(self, item: QListWidgetItem) -> None:
        """
        Updates the file preview when a file is selected

        :param item: The selected file item
        """
        selected_file_path = item.data(1)
        self._file_preview_scene.clear()
        base_image_pixmap = QPixmap(str(selected_file_path))
        base_image_item = QGraphicsPixmapItem(base_image_pixmap)
        self._file_preview_scene.addItem(base_image_item)
        self._file_preview_view.resizeEvent(None)

    def add_collection(self) -> None:
        """
        Adds a new collection
        """
        collection_count = len(self.app_state.collections.get_collections(self.media_type))
        while f'New Collection {collection_count}' in self.app_state.collections.get_collections(self.media_type):
            collection_count += 1
        new_collection_name = f'New Collection {collection_count}'
        self.app_state.collections.create_collection(new_collection_name, self.media_type)
        new_item = QListWidgetItem(new_collection_name)
        self._collection_list.addItem(new_item)
        self._collection_list.setCurrentItem(new_item)
        self._collection_name_field.setText(new_collection_name)
        self._add_file_button.setEnabled(True)
        self._add_folder_button.setEnabled(True)
        self._delete_file_button.setEnabled(True)
        self._delete_collection_button.setEnabled(True)

    def rename_collection(self) -> None:
        """
        Renames the selected collection
        """
        if self._collection_list.currentItem() is None:
            return
        collection = self._collection_list.currentItem().data(0)
        new_name = self._collection_name_field.text()
        if new_name != collection and len(new_name) > 0 and new_name not in self.app_state.collections.get_collections(self.media_type):
            self.app_state.collections.change_collection_name(collection, new_name, self.media_type)
            self._collection_list.currentItem().setText(new_name)
            self._collection_list.currentItem().setData(0, new_name)

    def add_files(self):
        """
        Opens a file dialog to add files to the collection
        """
        dialog = QFileDialog(self, f"{self.tr('Select File(s)')}", "/")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        name_filter = ["Images (*.png *.jpg *.jpeg)"] if self.media_type == 'image' else ["Videos (*.mp4 *.avi *.mov *.webm)"]
        dialog.setNameFilters(name_filter)
        if dialog.exec():
            file_paths = [Path(file) for file in dialog.selectedFiles() if file != '']
            self.process_files(file_paths)

    def add_folder(self):
        """
        Opens a file dialog to add a folder to the collection
        """
        file_extensions = ('.png', '.jpg', '.jpeg') if self.media_type == 'image' else ('.mp4', '.avi', '.mov', '.webm')
        dialog = QFileDialog(self, self.tr("Select Folder(s)"), "/")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dialog.exec():
            folder_path = dialog.selectedFiles()[0]
            file_paths = [file for file in Path(folder_path).rglob('*') if file.suffix in file_extensions]
            self.process_files(file_paths)

    def process_files(self, file_paths: list[Path]):
        """
        Adds the files to the collection

        :param file_paths: The file paths to add
        """
        collection = self._collection_list.currentItem().data(0)
        collection_path = self.app_state.collections.get_collection_path(collection, self.media_type)
        for file_path in file_paths:
            file_name = file_path.name
            new_file_path = collection_path / file_name
            shutil.copyfile(file_path, new_file_path)
            list_item = QListWidgetItem(file_name)
            list_item.setData(1, new_file_path)
            self._collection_file_list.addItem(list_item)

    def delete_files(self):
        """
        Deletes the selected files from the collection
        """
        for item in self._collection_file_list.selectedItems():
            file_path = item.data(1)
            Path(file_path).unlink()
            self._collection_file_list.takeItem(self._collection_file_list.row(item))
        self._file_preview_scene.clear()

    def delete_collection(self):
        """
        Deletes the selected collection
        """
        collection = self._collection_list.currentItem().data(0)
        self.app_state.collections.delete_collection(collection, self.media_type)
        self._collection_list.takeItem(self._collection_list.currentRow())
        self._collection_name_field.setText('')
        self._add_file_button.setEnabled(False)
        self._add_folder_button.setEnabled(False)
        self._delete_file_button.setEnabled(False)
        self._delete_collection_button.setEnabled(False)
