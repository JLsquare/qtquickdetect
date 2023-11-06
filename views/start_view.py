from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QSpacerItem, QSizePolicy, QFileDialog
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize
from views.other_source_view import OtherSourceView
from views.settings_view import SettingsView
import logging


class StartView(QWidget):
    def __init__(self):
        super().__init__()

        self._settings_window = None
        self._other_source_window = None

        self._input_path = None
        self._functionality_selected = None
        self._model_selected = None

        self._btn_import_image = None
        self._btn_import_video = None
        self._btn_other_source = None
        self._functionality_combo = None
        self._model_combo = None
        self._btn_run = None

        self._is_image = None
        self._is_video = None
        self._is_live = None

        self.init_variables()
        self.init_window()
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_window(self):
        self.setWindowTitle('QTQuickDetect')
        self.setGeometry(100, 100, 800, 480)
        with open('ressources/qss/stylesheet.qss', 'r') as file:
            self.setStyleSheet(file.read())

    def init_ui(self):
        # Middle Layout
        middle_layout = QHBoxLayout()
        middle_layout.addLayout(self.input_ui(), 1)
        middle_layout.addLayout(self.functionality_ui(), 1)
        middle_layout.addLayout(self.model_ui(), 1)
        middle_layout.addLayout(self.run_ui(), 1)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.top_ui())
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addLayout(middle_layout)
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.setLayout(main_layout)

    def top_ui(self):
        # Title Layout
        title_layout = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(
            QPixmap('ressources/images/qtquickdetect_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                                       Qt.TransformationMode.SmoothTransformation))
        title_icon.setFixedWidth(32)
        title_label = QLabel('QTQuickDetect')
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_label)

        # Settings icon
        btn_settings = QPushButton()
        btn_settings.setIcon(QIcon('ressources/images/settings_icon.png'))
        btn_settings.setIconSize(QSize(32, 32))
        btn_settings.setFixedWidth(32)
        btn_settings.setProperty('class', 'settings')
        btn_settings.clicked.connect(self.open_settings)

        # Top layout
        top_layout = QHBoxLayout()
        top_layout.addStretch(2)
        top_layout.addLayout(title_layout, 3)
        top_layout.addWidget(btn_settings, 1)

        return top_layout

    def input_ui(self):
        # Input icon
        input_icon_layout = QHBoxLayout()
        input_icon_layout.addStretch()
        input_icon = QLabel()
        input_icon.setPixmap(
            QPixmap('ressources/images/input_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                               Qt.TransformationMode.SmoothTransformation))
        input_icon_layout.addWidget(input_icon)
        input_icon_layout.addStretch()

        # Input buttons
        btn_import_image = QPushButton('Import Image')
        btn_import_image.setProperty('class', 'input')
        btn_import_image.clicked.connect(self.open_image)
        self._btn_import_image = btn_import_image
        btn_import_video = QPushButton('Import Video')
        btn_import_video.setProperty('class', 'input')
        btn_import_video.clicked.connect(self.open_video)
        self._btn_import_video = btn_import_video
        btn_other_source = QPushButton('Other Source')
        btn_other_source.setProperty('class', 'input')
        btn_other_source.clicked.connect(self.open_other_source)
        self._btn_other_source = btn_other_source

        # Input Layout
        input_layout = QVBoxLayout()
        input_layout.addLayout(input_icon_layout)
        input_layout.addWidget(btn_import_image)
        input_layout.addWidget(btn_import_video)
        input_layout.addWidget(btn_other_source)

        return input_layout

    def functionality_ui(self):
        # Functionality icon
        functionality_icon_layout = QHBoxLayout()
        functionality_icon_layout.addStretch()
        functionality_icon = QLabel()
        functionality_icon.setPixmap(
            QPixmap('ressources/images/functionality_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                                       Qt.TransformationMode.SmoothTransformation))
        functionality_icon_layout.addWidget(functionality_icon)
        functionality_icon_layout.addStretch()

        # Functionality Combo
        functionality_combo = QComboBox()
        functionality_combo.addItem('Functionality')
        functionality_combo.addItem('Detection', 'detect')
        functionality_combo.currentIndexChanged.connect(self.check_functionality_selected)
        self._functionality_combo = functionality_combo

        # Functionality Layout
        functionality_layout = QVBoxLayout()
        functionality_layout.addLayout(functionality_icon_layout)
        functionality_layout.addWidget(functionality_combo)
        functionality_layout.addStretch()

        return functionality_layout

    def model_ui(self):
        # Model icon
        model_icon_layout = QHBoxLayout()
        model_icon_layout.addStretch()
        model_icon = QLabel()
        model_icon.setPixmap(
            QPixmap('ressources/images/model_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                               Qt.TransformationMode.SmoothTransformation))
        model_icon_layout.addWidget(model_icon)
        model_icon_layout.addStretch()

        # Model Combo
        model_combo = QComboBox()
        model_combo.addItem('Model')
        model_combo.addItem('YOLOv8n', 'yolov8n.pt')
        model_combo.addItem('YOLOv8s', 'yolov8s.pt')
        model_combo.addItem('YOLOv8m', 'yolov8m.pt')
        model_combo.addItem('YOLOv8l', 'yolov8l.pt')
        model_combo.addItem('YOLOv8x', 'yolov8x.pt')
        model_combo.currentIndexChanged.connect(self.check_model_selected)
        self._model_combo = model_combo

        # Model Layout
        model_layout = QVBoxLayout()
        model_layout.addLayout(model_icon_layout)
        model_layout.addWidget(model_combo)
        model_layout.addStretch()

        return model_layout

    def run_ui(self):
        # Run icon
        run_icon_layout = QHBoxLayout()
        run_icon_layout.addStretch()
        run_icon = QLabel()
        run_icon.setPixmap(QPixmap('ressources/images/run_icon.png').scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                                                            Qt.TransformationMode.SmoothTransformation))
        run_icon_layout.addWidget(run_icon)
        run_icon_layout.addStretch()

        # Run button
        btn_run = QPushButton('Run')
        btn_run.setProperty('class', 'run')
        btn_run.setEnabled(False)
        btn_run.clicked.connect(self.run)
        self._btn_run = btn_run

        # Run Layout
        run_layout = QVBoxLayout()
        run_layout.addLayout(run_icon_layout)
        run_layout.addWidget(btn_run)
        run_layout.addStretch()

        return run_layout

    ##############################
    #         CONTROLLER         #
    ##############################

    def init_variables(self):
        self._model_selected = False
        self._functionality_selected = False
        self._input_path = ''
        self._is_live = False
        self._is_image = False
        self._is_video = False

    def open_image(self):
        file_name = QFileDialog.getOpenFileNames(self, 'Open Image', '/', 'Images (*.png *.jpg *.jpeg)')
        if len(file_name[0]) > 0:
            self._btn_import_image.setText(str(len(file_name[0])) + ' Images')
            self._btn_import_video.setText('Import Video')
            self._is_image = True
            self._is_video = False
            self._is_live = False
            self._input_path = file_name[0]
            logging.debug('Image(s) opened : ' + str(file_name[0]))
            self.check_enable_run()

    def open_video(self):
        file_name = QFileDialog.getOpenFileNames(self, 'Open Video', '/', 'Videos (*.mp4 *.avi *.mov)')
        if len(file_name[0]) > 0:
            self._btn_import_video.setText(str(len(file_name[0])) + ' Videos')
            self._btn_import_image.setText('Import Image')
            self._is_video = True
            self._is_image = False
            self._is_live = False
            self._input_path = file_name[0]
            logging.debug('Video(s) opened : ' + str(file_name[0]))
            self.check_enable_run()

    def open_other_source(self):
        self._other_source_window = OtherSourceView(self.callback_other_source)
        self._other_source_window.show()
        logging.debug('Window opened : Other Source')

    def callback_other_source(self, url, image, video, live):
        self._input_path = [url]
        self._is_image = image
        self._is_video = video
        self._is_live = live

        self._btn_import_video.setText('Import Video')
        self._btn_import_image.setText('Import Image')
        source_type = 'Image' if image else 'Video' if video else 'Live' if live else 'Unknown'
        self._btn_other_source.setText(f'Source : {source_type}')

        logging.debug(f'Other source opened: {url}, type: {source_type}')
        self.check_enable_run()

    def open_settings(self):
        self._settings_window = SettingsView()
        self._settings_window.show()
        logging.debug('Window opened : Settings')

    def check_functionality_selected(self, index):
        if index != 0:
            self._functionality_selected = True
        else:
            self._functionality_selected = False
        logging.debug('Functionality selected : ' + self._functionality_combo.currentData())
        self.check_enable_run()

    def check_model_selected(self, index):
        if index != 0:
            self._model_selected = True
        else:
            self._model_selected = False
        logging.debug('Model selected : ' + self._model_combo.currentData())
        self.check_enable_run()

    def check_enable_run(self):
        if (self._is_image or self._is_video or self._is_live) and self._model_selected and self._functionality_selected:
            self._btn_run.setEnabled(True)
        else:
            self._btn_run.setEnabled(False)
        logging.debug('Run enabled : ' + str(self._btn_run.isEnabled()))

    def run(self):
        inputs = self._input_path
        model_path = self._model_combo.currentData()
        task = self._functionality_combo.currentData()
        media_type = 'image' if self._is_image else 'video' if self._is_video else 'live'
        logging.info('Run with : ' + str(inputs) + ', ' + str(model_path) + ', ' + str(task) + ', ' + str(media_type))

