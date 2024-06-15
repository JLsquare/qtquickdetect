import logging

from typing import Optional
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QListWidget, \
    QStackedWidget, QListWidgetItem, QSizePolicy

from .inference_stream_widget import InferenceStreamWidget
from ..utils import filepaths
from ..models.app_state import AppState
from ..views.about_widget import AboutWidget
from ..views.app_config_widget import AppConfigWidget
from ..views.collections_widget import CollectionsWidget
from ..views.inference_history_widget import InferenceHistoryWidget
from ..views.inference_widget import InferenceWidget
from ..views.models_widget import ModelsWidget
from ..views.presets_widget import PresetsWidget
from ..views.training_widget import TrainingWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # PyQT6 Components
        self._title_widget: Optional[QWidget] = None
        self._title_list_item: Optional[QListWidgetItem] = None
        self._sidebar_layout: Optional[QHBoxLayout] = None
        self._main_layout: Optional[QHBoxLayout] = None
        self._title_layout: Optional[QHBoxLayout] = None
        self._title_label: Optional[QLabel] = None
        self._title_icon: Optional[QLabel] = None
        self._side_menu: Optional[QListWidget] = None
        self._content_stack: Optional[QStackedWidget] = None

        self._appstate = AppState.get_instance()

        self.init_window()
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_window(self):
        self.setWindowTitle('QTQuickDetect')
        self.setGeometry(100, 100, 1524, 720)
        self.setMinimumSize(QSize(1524, 600))
        self.setStyleSheet(self._appstate.qss)
        self.setProperty('class', 'dark-bg')

    def init_ui(self):
        self._side_menu = QListWidget()
        self._content_stack = QStackedWidget()

        self._title_list_item = QListWidgetItem(self._side_menu)
        self._title_list_item.setSizeHint(QSize(100, 64))
        self._title_list_item.setFlags(self._title_list_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self._title_list_item.setFlags(self._title_list_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
        self._side_menu.setItemWidget(self._title_list_item, self.title_ui())
        self._content_stack.addWidget(QWidget())  # Empty widget for title

        self._side_menu.addItem('Models')
        self._content_stack.addWidget(ModelsWidget())
        self._side_menu.addItem('Presets')
        self._content_stack.addWidget(PresetsWidget())
        self._side_menu.addItem('Image Collections')
        self._content_stack.addWidget(CollectionsWidget('image'))
        self._side_menu.addItem('Video Collections')
        self._content_stack.addWidget(CollectionsWidget('video'))
        self._side_menu.addItem('Image Inference')
        self._content_stack.addWidget(InferenceWidget('image', self.open_last_inference))
        self._side_menu.addItem('Video Inference')
        self._content_stack.addWidget(InferenceWidget('video', self.open_last_inference))
        self._side_menu.addItem('Stream Inference')
        self._content_stack.addWidget(InferenceStreamWidget())
        self._side_menu.addItem('Inference History')
        self._content_stack.addWidget(InferenceHistoryWidget())
        self._side_menu.addItem('Training')
        self._content_stack.addWidget(TrainingWidget())
        self._side_menu.addItem('Settings')
        self._content_stack.addWidget(AppConfigWidget())
        self._side_menu.addItem('About')
        self._content_stack.addWidget(AboutWidget())

        self._side_menu.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._side_menu.setFixedWidth(210)
        self._side_menu.currentRowChanged.connect(self.change_row)

        self._main_layout = QHBoxLayout()
        self._main_layout.addWidget(self._side_menu)
        self._main_layout.addWidget(self._content_stack)

        self.change_row(5)

        self.setLayout(self._main_layout)

    def title_ui(self) -> QWidget:
        self._title_icon = QLabel()
        pixmap = (QPixmap(str(filepaths.get_app_dir() / 'resources' / 'images' / 'qtquickdetect_icon.png'))
                  .scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self._title_icon.setPixmap(pixmap)
        self._title_icon.setFixedWidth(32)
        self._title_label = QLabel('QTQuickDetect')

        self._title_layout = QHBoxLayout()
        self._title_layout.addWidget(self._title_icon)
        self._title_layout.addWidget(self._title_label)

        self._title_widget = QWidget()
        self._title_widget.setLayout(self._title_layout)
        return self._title_widget

    def change_row(self, row: int):
        logging.info(f'Change row {row}')
        self._side_menu.setCurrentRow(row)

        # Re-instantiate the InferenceWidget to update the collection / model / preset list (temp ?)
        if row == 5:  # Image Inference
            new_widget = InferenceWidget('image', self.open_last_inference)
            self._content_stack.insertWidget(row, new_widget)
            self._content_stack.removeWidget(self._content_stack.widget(row + 1))
        elif row == 6:  # Video Inference
            new_widget = InferenceWidget('video', self.open_last_inference)
            self._content_stack.insertWidget(row, new_widget)
            self._content_stack.removeWidget(self._content_stack.widget(row + 1))

        self._content_stack.setCurrentIndex(row)

    def open_last_inference(self):
        self.change_row(8)
        if isinstance(self._content_stack.currentWidget(), InferenceHistoryWidget):
            self._content_stack.currentWidget().open_last_inference()
