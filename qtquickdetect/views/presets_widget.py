import torch

from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QListWidget, QHBoxLayout, QListWidgetItem, QLineEdit, QVBoxLayout, \
    QPushButton, QLabel, QComboBox, QSlider, QColorDialog, QScrollArea, QCheckBox
from ..models.app_state import AppState
from ..models.preset import Preset


class PresetsWidget(QWidget):
    def __init__(self):
        """
        Initializes the PresetWidget
        """
        super().__init__()
        self.app_state: AppState = AppState.get_instance()
        self.current_preset: Optional[Preset] = None

        # PyQT6 Components
        self._preset_list: Optional[QListWidget] = None
        self._add_preset_button: Optional[QPushButton] = None
        self._preset_list_layout: Optional[QVBoxLayout] = None
        self._preset_name_field: Optional[QLineEdit] = None
        self._preset_layout: Optional[QVBoxLayout] = None
        self._main_layout: Optional[QHBoxLayout] = None
        self._device_combo: Optional[QComboBox] = None
        self._half_precision_checkbox: Optional[QCheckBox] = None
        self._iou_slider: Optional[QSlider] = None
        self._image_format_combo: Optional[QComboBox] = None
        self._video_format_combo: Optional[QComboBox] = None
        self._box_color_button: Optional[QPushButton] = None
        self._box_color_by_class_checkbox: Optional[QCheckBox] = None
        self._segment_color_button: Optional[QPushButton] = None
        self._segment_color_by_class_checkbox: Optional[QCheckBox] = None
        self._text_color_button: Optional[QPushButton] = None
        self._box_thickness_slider: Optional[QSlider] = None
        self._segment_thickness_slider: Optional[QSlider] = None
        self._text_size_slider: Optional[QSlider] = None
        self._pose_head_color_button: Optional[QPushButton] = None
        self._pose_chest_color_button: Optional[QPushButton] = None
        self._pose_leg_color_button: Optional[QPushButton] = None
        self._pose_arm_color_button: Optional[QPushButton] = None
        self._pose_point_size_slider: Optional[QSlider] = None
        self._pose_line_thickness_slider: Optional[QSlider] = None
        self._preset_widget: Optional[QWidget] = None
        self._scroll_area: Optional[QScrollArea] = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self) -> None:
        """
        Initializes the UI
        """
        self._main_layout = QHBoxLayout()
        self._preset_layout = QVBoxLayout()
        self._preset_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Preset name configuration
        self._preset_name_field = QLineEdit()
        self._preset_name_field.textChanged.connect(self.rename_preset)
        self._preset_layout.addWidget(QLabel("Preset Name:"))
        self._preset_layout.addWidget(self._preset_name_field)

        # Device selection
        self._device_combo = QComboBox()
        self._device_combo.addItem("CPU")
        self._device_combo.addItems(self.get_gpu_devices())
        self._device_combo.currentTextChanged.connect(self.set_device)
        self._preset_layout.addWidget(QLabel("Device:"))
        self._preset_layout.addWidget(self._device_combo)

        # Half precision toggle
        self._half_precision_checkbox = QCheckBox("Enable Half Precision (FP16)")
        self._half_precision_checkbox.toggled.connect(self.set_half_precision)
        self._preset_layout.addWidget(QLabel("Half Precision:"))
        self._preset_layout.addWidget(self._half_precision_checkbox)

        # IOU Slider
        self._iou_slider = QSlider(Qt.Orientation.Horizontal)
        self._iou_slider.setRange(0, 100)
        self._iou_slider.valueChanged.connect(self.set_iou_threshold)
        self._preset_layout.addWidget(QLabel("IOU Threshold:"))
        self._preset_layout.addWidget(self._iou_slider)

        # Image format selection
        self._image_format_combo = QComboBox()
        self._image_format_combo.addItems(["png", "jpg"])
        self._image_format_combo.currentTextChanged.connect(self.set_image_format)
        self._preset_layout.addWidget(QLabel("Image Format:"))
        self._preset_layout.addWidget(self._image_format_combo)

        # Video format selection
        self._video_format_combo = QComboBox()
        self._video_format_combo.addItems(["mp4", "avi"])
        self._video_format_combo.currentTextChanged.connect(self.set_video_format)
        self._preset_layout.addWidget(QLabel("Video Format:"))
        self._preset_layout.addWidget(self._video_format_combo)

        # Box color picker
        self._box_color_button = QPushButton("Set Box Color")
        self._box_color_button.clicked.connect(self.set_box_color)
        self._preset_layout.addWidget(QLabel("Box Color:"))
        self._preset_layout.addWidget(self._box_color_button)

        # Box color by class
        self._box_color_by_class_checkbox = QCheckBox("Random Box Color by Class")
        self._box_color_by_class_checkbox.toggled.connect(self.set_box_color_by_class)
        self._preset_layout.addWidget(self._box_color_by_class_checkbox)

        # Segment color picker
        self._segment_color_button = QPushButton("Set Segment Color")
        self._segment_color_button.clicked.connect(self.set_segment_color)
        self._preset_layout.addWidget(QLabel("Segment Color:"))
        self._preset_layout.addWidget(self._segment_color_button)

        # Segment color by class
        self._segment_color_by_class_checkbox = QCheckBox("Random Segment Color by Class")
        self._segment_color_by_class_checkbox.toggled.connect(self.set_segment_color_by_class)
        self._preset_layout.addWidget(self._segment_color_by_class_checkbox)

        # Text color picker
        self._text_color_button = QPushButton("Set Text Color")
        self._text_color_button.clicked.connect(self.set_text_color)
        self._preset_layout.addWidget(QLabel("Text Color:"))
        self._preset_layout.addWidget(self._text_color_button)

        # Box thickness
        self._box_thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self._box_thickness_slider.setRange(1, 10)
        self._box_thickness_slider.valueChanged.connect(self.set_box_thickness)
        self._preset_layout.addWidget(QLabel("Box Thickness:"))
        self._preset_layout.addWidget(self._box_thickness_slider)

        # Segment thickness
        self._segment_thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self._segment_thickness_slider.setRange(1, 10)
        self._segment_thickness_slider.valueChanged.connect(self.set_segment_thickness)
        self._preset_layout.addWidget(QLabel("Segment Thickness:"))
        self._preset_layout.addWidget(self._segment_thickness_slider)

        # Text size
        self._text_size_slider = QSlider(Qt.Orientation.Horizontal)
        self._text_size_slider.setRange(1, 30)
        self._text_size_slider.valueChanged.connect(self.set_text_size)
        self._preset_layout.addWidget(QLabel("Text Size:"))
        self._preset_layout.addWidget(self._text_size_slider)

        # Pose head color picker
        self._pose_head_color_button = QPushButton("Set Pose Head Color")
        self._pose_head_color_button.clicked.connect(lambda: self.set_color('pose_head_color'))
        self._preset_layout.addWidget(QLabel("Pose Head Color:"))
        self._preset_layout.addWidget(self._pose_head_color_button)

        # Pose chest color picker
        self._pose_chest_color_button = QPushButton("Set Pose Chest Color")
        self._pose_chest_color_button.clicked.connect(lambda: self.set_color('pose_chest_color'))
        self._preset_layout.addWidget(QLabel("Pose Chest Color:"))
        self._preset_layout.addWidget(self._pose_chest_color_button)

        # Pose leg color picker
        self._pose_leg_color_button = QPushButton("Set Pose Leg Color")
        self._pose_leg_color_button.clicked.connect(lambda: self.set_color('pose_leg_color'))
        self._preset_layout.addWidget(QLabel("Pose Leg Color:"))
        self._preset_layout.addWidget(self._pose_leg_color_button)

        # Pose arm color picker
        self._pose_arm_color_button = QPushButton("Set Pose Arm Color")
        self._pose_arm_color_button.clicked.connect(lambda: self.set_color('pose_arm_color'))
        self._preset_layout.addWidget(QLabel("Pose Arm Color:"))
        self._preset_layout.addWidget(self._pose_arm_color_button)

        # Pose point size
        self._pose_point_size_slider = QSlider(Qt.Orientation.Horizontal)
        self._pose_point_size_slider.setRange(1, 10)
        self._pose_point_size_slider.valueChanged.connect(self.set_pose_point_size)
        self._preset_layout.addWidget(QLabel("Pose Point Size:"))
        self._preset_layout.addWidget(self._pose_point_size_slider)

        # Pose line thickness
        self._pose_line_thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self._pose_line_thickness_slider.setRange(1, 10)
        self._pose_line_thickness_slider.valueChanged.connect(self.set_pose_line_thickness)
        self._preset_layout.addWidget(QLabel("Pose Line Thickness:"))
        self._preset_layout.addWidget(self._pose_line_thickness_slider)

        self._preset_widget = QWidget()
        self._preset_widget.setLayout(self._preset_layout)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setWidget(self._preset_widget)
        self._scroll_area.hide()

        self._main_layout.addLayout(self.preset_list_ui())
        self._main_layout.addWidget(self._scroll_area, 1)
        self.setLayout(self._main_layout)

    def preset_list_ui(self) -> QVBoxLayout:
        """
        Creates the preset list UI

        :return: The preset list layout
        """
        self._preset_list_layout = QVBoxLayout()
        self._preset_list = QListWidget()
        for preset in self.app_state.presets.get_presets():
            item = QListWidgetItem(preset)
            item.setData(0, preset)
            self._preset_list.addItem(item)
        self._preset_list.itemClicked.connect(self.preset_selected)
        self._add_preset_button = QPushButton('Add Preset')
        self._add_preset_button.clicked.connect(self.add_preset)
        self._preset_list_layout.addWidget(self._preset_list)
        self._preset_list_layout.addWidget(self._add_preset_button)
        return self._preset_list_layout

    ##############################
    #         CONTROLLER         #
    ##############################

    def preset_selected(self, item: QListWidgetItem) -> None:
        """
        Handles the selection of a preset

        :param item: The selected item
        """
        preset = item.data(0)
        self.update_preset(preset)

    def add_preset(self) -> None:
        """
        Adds a new preset
        """
        preset_count = len(self.app_state.presets.get_presets())
        while f'New Preset {preset_count}.json' in self.app_state.presets.get_presets():
            preset_count += 1
        new_preset_name = f'New Preset {preset_count}.json'
        self.app_state.presets.create_preset(new_preset_name)
        new_item = QListWidgetItem(new_preset_name)
        self._preset_list.addItem(new_item)
        self._preset_list.setCurrentItem(new_item)
        self.update_preset(new_preset_name)

    def update_preset(self, preset: str) -> None:
        self.current_preset = self.app_state.presets.get_preset(preset)
        self._preset_name_field.setText(preset)
        self._device_combo.setCurrentText(self.get_device())
        self._half_precision_checkbox.setChecked(self.current_preset.half_precision)
        self._iou_slider.setValue(int(self.current_preset.iou_threshold * 100))
        self._image_format_combo.setCurrentText(self.current_preset.image_format)
        self._video_format_combo.setCurrentText(self.current_preset.video_format)
        self._box_thickness_slider.setValue(self.current_preset.box_thickness)
        self._segment_thickness_slider.setValue(self.current_preset.segment_thickness)
        self._text_size_slider.setValue(int(self.current_preset.text_size * 10.0))
        box_color = self.current_preset.box_color
        segment_color = self.current_preset.segment_color
        text_color = self.current_preset.text_color
        self._box_color_button.setStyleSheet(f'background-color: rgb({box_color[0]}, {box_color[1]}, {box_color[2]});')
        self._segment_color_button.setStyleSheet(f'background-color: rgb({segment_color[0]}, {segment_color[1]}, {segment_color[2]});')
        self._text_color_button.setStyleSheet(f'background-color: rgb({text_color[0]}, {text_color[1]}, {text_color[2]});')
        self._box_color_by_class_checkbox.setChecked(self.current_preset.box_color_per_class)
        self._segment_color_by_class_checkbox.setChecked(self.current_preset.segment_color_per_class)
        self._pose_head_color_button.setStyleSheet(f'background-color: rgb({self.current_preset.pose_head_color[0]}, {self.current_preset.pose_head_color[1]}, {self.current_preset.pose_head_color[2]});')
        self._pose_chest_color_button.setStyleSheet(f'background-color: rgb({self.current_preset.pose_chest_color[0]}, {self.current_preset.pose_chest_color[1]}, {self.current_preset.pose_chest_color[2]});')
        self._pose_leg_color_button.setStyleSheet(f'background-color: rgb({self.current_preset.pose_leg_color[0]}, {self.current_preset.pose_leg_color[1]}, {self.current_preset.pose_leg_color[2]});')
        self._pose_arm_color_button.setStyleSheet(f'background-color: rgb({self.current_preset.pose_arm_color[0]}, {self.current_preset.pose_arm_color[1]}, {self.current_preset.pose_arm_color[2]});')
        self._pose_point_size_slider.setValue(self.current_preset.pose_point_size)
        self._pose_line_thickness_slider.setValue(self.current_preset.pose_line_thickness)
        self._scroll_area.show()

    def rename_preset(self) -> None:
        """
        Renames the selected preset
        """
        if self._preset_list.currentItem() is None:
            return
        preset = self._preset_list.currentItem().data(0)
        new_name = self._preset_name_field.text()
        if new_name != preset and len(new_name) > 0 and new_name not in self.app_state.presets.get_presets():
            self.app_state.presets.change_preset_name(preset, new_name)
            self._preset_list.currentItem().setText(new_name)
            self._preset_list.currentItem().setData(0, new_name)
        self.current_preset = self.app_state.presets.get_preset(new_name)

    def delete_preset(self):
        """
        Deletes the selected preset
        """
        preset = self._preset_list.currentItem().data(0)
        self.app_state.presets.delete_preset(preset)
        self._preset_list.takeItem(self._preset_list.currentRow())
        self._preset_name_field.setText('')
        self.current_preset = None
        self._scroll_area.hide()

    @staticmethod
    def get_gpu_devices() -> list[str]:
        if not torch.cuda.is_available():
            return []
        num_gpus = torch.cuda.device_count()
        gpu_devices = ['GPU-{} ({})'.format(i, torch.cuda.get_device_name(i)) for i in range(num_gpus)]
        return gpu_devices

    def get_device(self) -> str:
        if self.current_preset.device == 'cpu':
            return 'CPU'
        else:
            device_id = torch.cuda.current_device()
            return f"GPU-{device_id} ({torch.cuda.get_device_name(device_id)})"

    def set_device(self, value):
        if value == 'CPU':
            self.current_preset.device = 'cpu'
        else:
            device_id = int(value.split('-')[1].split(' ')[0])
            self.current_preset.device = f"cuda:{device_id}"
        self.current_preset.save()

    def set_half_precision(self, enabled):
        self.current_preset.half_precision = enabled
        self.current_preset.save()

    def set_iou_threshold(self, value):
        self.current_preset.iou_threshold = value / 100.0
        self.current_preset.save()

    def set_image_format(self, image_format):
        self.current_preset.image_format = image_format
        self.current_preset.save()

    def set_video_format(self, video_format):
        self.current_preset.video_format = video_format
        self.current_preset.save()

    def set_color(self, color_attribute):
        color = getattr(self.current_preset, color_attribute)
        color_picker = QColorDialog()
        color_picker.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel)
        color_picker.setCurrentColor(QColor(*color))
        if color_picker.exec() == QColorDialog.DialogCode.Accepted:
            new_color = color_picker.currentColor()
            new_color_tuple = (new_color.red(), new_color.green(), new_color.blue(), new_color.alpha())
            setattr(self.current_preset, color_attribute, new_color_tuple)
            self.current_preset.save()

    def set_box_color(self):
        self.set_color('box_color')

    def set_segment_color(self):
        self.set_color('segment_color')

    def set_text_color(self):
        self.set_color('text_color')

    def set_box_color_by_class(self, value):
        self.current_preset.box_color_per_class = value
        self.current_preset.save()

    def set_segment_color_by_class(self, value):
        self.current_preset.segment_color_per_class = value
        self.current_preset.save()

    def set_box_thickness(self, value):
        self.current_preset.box_thickness = value
        self.current_preset.save()

    def set_segment_thickness(self, value):
        self.current_preset.segment_thickness = value
        self.current_preset.save()

    def set_text_size(self, value):
        self.current_preset.text_size = value / 10.0
        self.current_preset.save()

    def set_pose_point_size(self, value):
        self.current_preset.pose_point_size = value
        self.current_preset.save()

    def set_pose_line_thickness(self, value):
        self.current_preset.pose_line_thickness = value
        self.current_preset.save()
