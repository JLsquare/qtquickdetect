from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit

from ..views.stream_widget import StreamWidget
from ..utils import filepaths
from ..models.app_state import AppState
from ..models.preset import Preset
from ..pipeline.pipeline_manager import PipelineManager
from ..views.models_selection_widget import ModelsSelectionWidget
from ..views.task_selection_widget import TaskSelectionWidget
from ..views.preset_selection_widget import PresetSelectionWidget


class InferenceStreamWidget(QWidget):
    """
    InferenceStreamWidget is a QWidget that allows the user to run the pipeline on a stream.
    """
    def __init__(self):
        """
        Initializes the InferenceStreamWidget.
        """
        super().__init__()
        self.app_state: AppState = AppState.get_instance()
        self.pipeline_manager: Optional[PipelineManager] = None

        # PyQT6 Components
        self._main_layout: Optional[QHBoxLayout] = None
        self._url: Optional[QLineEdit] = None
        self._url_layout: Optional[QVBoxLayout] = None
        self._url_icon: Optional[QLabel] = None
        self._url_icon_layout: Optional[QHBoxLayout] = None
        self._url_widget: Optional[QWidget] = None
        self._preset: Optional[PresetSelectionWidget] = None
        self._task: Optional[TaskSelectionWidget] = None
        self._models: Optional[ModelsSelectionWidget] = None
        self._run_icon_layout: Optional[QHBoxLayout] = None
        self._run_icon: Optional[QLabel] = None
        self._run_layout: Optional[QVBoxLayout] = None
        self._run_widget: Optional[QWidget] = None
        self._run_description: Optional[QLabel] = None
        self._btn_run: Optional[QPushButton] = None
        self._btn_cancel: Optional[QPushButton] = None
        self._inference_layout: Optional[QVBoxLayout] = None
        self._h_inference_layout: Optional[QHBoxLayout] = None
        self._inference_widget: Optional[QWidget] = None
        self._stream_widget: Optional[StreamWidget] = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self) -> None:
        """
        Initializes the user interface components.
        """
        self._main_layout = QVBoxLayout()
        self._main_layout.addWidget(self.inference_ui())
        self.setLayout(self._main_layout)

    def inference_ui(self) -> QWidget:
        """
        Initializes the inference user interface components.

        :return: QWidget containing the inference user interface components.
        """
        self._inference_layout = QVBoxLayout()
        self._h_inference_layout = QHBoxLayout()
        self._h_inference_layout.addStretch()
        self._h_inference_layout.addWidget(self.task_ui())
        self._h_inference_layout.addWidget(self.models_ui())
        self._h_inference_layout.addWidget(self.preset_ui())
        self._h_inference_layout.addWidget(self.url_ui())
        self._h_inference_layout.addWidget(self.run_ui())
        self._h_inference_layout.addStretch()
        self._inference_layout.addStretch()
        self._inference_layout.addLayout(self._h_inference_layout)
        self._inference_layout.addStretch()
        self._inference_widget = QWidget()
        self._inference_widget.setLayout(self._inference_layout)
        return self._inference_widget

    def url_ui(self) -> QWidget:
        """
        Initializes the URL user interface components.

        :return: QWidget containing the URL user interface components.
        """
        self._url_icon_layout = QHBoxLayout()
        self._url_icon_layout.addStretch()
        self._url_icon = QLabel()
        self._url_icon.setPixmap(
            QPixmap(str(filepaths.get_app_dir() / 'resources' / 'images' / 'input_icon.png'))
            .scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )
        self._url_icon_layout.addWidget(self._url_icon)
        self._url_icon_layout.addStretch()

        self._url = QLineEdit()
        self._url.setPlaceholderText(self.tr('URL'))
        self._url.setProperty('class', 'url')
        self._url.setFixedWidth(240)
        self._url.textChanged.connect(self.check_run)

        self._url_layout = QVBoxLayout()
        self._url_layout.addLayout(self._url_icon_layout)
        self._url_layout.addWidget(self._url)
        self._url_layout.addStretch()

        self._url_widget = QWidget()
        self._url_widget.setLayout(self._url_layout)
        return self._url_widget

    def preset_ui(self) -> PresetSelectionWidget:
        """
        Initializes the preset user interface components.

        :return: PresetSelectionWidget containing the preset user interface components.
        """
        self._preset = PresetSelectionWidget()
        self._preset.preset_changed_signal.connect(self.check_run)
        return self._preset

    def task_ui(self) -> TaskSelectionWidget:
        """
        Task UI, contains only for now a radio button to select the task.
        (Detection, Segmentation, Classification, Pose)

        :return: TaskSelectionWidget containing the task user interface components.
        """
        self._task = TaskSelectionWidget()
        self._task.task_changed_signal.connect(self.update_models_task)
        return self._task

    def models_ui(self) -> ModelsSelectionWidget:
        """
        Initializes the models user interface components.

        :return: ModelsSelectionWidget containing the models user interface components.
        """
        self._models = ModelsSelectionWidget()
        self._models.models_changed_signal.connect(self.check_run)
        return self._models

    def run_ui(self) -> QWidget:
        """
        Initializes the run user interface components.

        :return: QWidget containing the run user interface components.
        """
        # Run icon
        self._run_icon_layout = QHBoxLayout()
        self._run_icon_layout.addStretch()
        self._run_icon = QLabel()
        self._run_icon.setPixmap(
            QPixmap(str(filepaths.get_app_dir() / 'resources' / 'images' / 'run_icon.png'))
            .scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )
        self._run_icon_layout.addWidget(self._run_icon)
        self._run_icon_layout.addStretch()

        # Run button
        self._btn_run = QPushButton(self.tr('Run'))
        self._btn_run.setProperty('class', 'green')
        self._btn_run.setEnabled(False)
        self._btn_run.clicked.connect(self.run)

        # Run description
        self._run_description = QLabel(self.tr('Run the pipeline'))
        self._run_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._run_description.setProperty('class', 'description')

        # Run Layout
        self._run_layout = QVBoxLayout()
        self._run_layout.addLayout(self._run_icon_layout)
        self._run_layout.addWidget(self._btn_run)
        self._run_layout.addWidget(self._btn_cancel)
        self._run_layout.addWidget(self._run_description)
        self._run_layout.addStretch()

        self._run_widget = QWidget()
        self._run_widget.setLayout(self._run_layout)
        self._run_widget.setFixedSize(240, 360)
        return self._run_widget

    ##############################
    #         CONTROLLER         #
    ##############################

    def update_models_task(self) -> None:
        """
        Updates the models task.
        """
        self._models.set_task(self._task.task)
        self.check_run()

    def check_run(self) -> None:
        """
        Checks if the run button should be enabled.
        """
        if self._url.text() and self._preset.preset and self._task.task and len(self._models.weights) == 1:
            self._btn_run.setEnabled(True)
        else:
            self._btn_run.setEnabled(False)

    def run(self) -> None:
        """
        Runs the pipeline.
        """
        preset = Preset(self._preset.preset)
        self._stream_widget = StreamWidget(self._url.text(), self._task.task, preset, self._models.weights,
                                           self.return_to_main_view)
        self._inference_widget.hide()
        self._main_layout.removeWidget(self._inference_widget)
        self._main_layout.addWidget(self._stream_widget)

    def return_to_main_view(self) -> None:
        """
        Returns to the main view.
        """
        self._stream_widget.hide()
        self._main_layout.removeWidget(self._stream_widget)
        self._inference_widget.show()
        self._main_layout.addWidget(self._inference_widget)
        self.check_run()
