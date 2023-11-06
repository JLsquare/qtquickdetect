from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize


class StartView(QWidget):
    def __init__(self):
        super().__init__()
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
        btn_import_video = QPushButton('Import Video')
        btn_import_video.setProperty('class', 'input')
        btn_other_source = QPushButton('Other Source')
        btn_other_source.setProperty('class', 'input')

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

        # Run Layout
        run_layout = QVBoxLayout()
        run_layout.addLayout(run_icon_layout)
        run_layout.addWidget(btn_run)
        run_layout.addStretch()

        return run_layout
