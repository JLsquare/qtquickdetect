from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QFileDialog, QProgressBar
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from views.image_result_view import ImageResultView
from views.other_source_view import OtherSourceView
from pipeline import img_detection, vid_detection
from views.video_result_view import VideoResultView
import logging


class StartView(QWidget):
    def __init__(self, add_new_tab):
        super().__init__()
        self.callback_count = 0
        self._add_new_tab = add_new_tab
        self._other_source_window = None
        self._progress_bar = None

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
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        # Middle Layout
        middle_layout = QHBoxLayout()
        middle_layout.addStretch(1)
        middle_layout.addWidget(self.input_ui())
        middle_layout.addWidget(self.functionality_ui())
        middle_layout.addWidget(self.model_ui())
        middle_layout.addWidget(self.run_ui())
        middle_layout.addStretch(1)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.addStretch()
        main_layout.addLayout(middle_layout)
        main_layout.addStretch()
        main_layout.addWidget(self.progress_bar_ui())
        self.setLayout(main_layout)

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
        input_layout.addStretch()

        input_widget = QWidget()
        input_widget.setLayout(input_layout)
        input_widget.setFixedSize(240, 240)
        return input_widget

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

        functionality_widget = QWidget()
        functionality_widget.setLayout(functionality_layout)
        functionality_widget.setFixedSize(240, 240)
        return functionality_widget

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

        model_widget = QWidget()
        model_widget.setLayout(model_layout)
        model_widget.setFixedSize(240, 240)
        return model_widget

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

        run_widget = QWidget()
        run_widget.setLayout(run_layout)
        run_widget.setFixedSize(240, 240)
        return run_widget

    def progress_bar_ui(self):
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(True)
        progress_bar.setFormat('%p%')
        progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._progress_bar = progress_bar
        return progress_bar

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

        if media_type == 'image' and task == 'detect':
            pipeline = img_detection.ImgDetectionPipeline(inputs, model_path)
            self.callback_count = 0
            self.update_progress_bar()

            def callback_ok(input_path, output_media_path, output_json_path):
                logging.info('Detection done for ' + input_path + ', output in ' + output_media_path)
                result_widget = ImageResultView(input_path, output_media_path)
                self._add_new_tab(result_widget, "Image detection", len(self._input_path) == 1)
                self.callback_count += 1
                self.update_progress_bar()

            def callback_err(input_media_path, exception):
                logging.error('Detection failed for ' + input_media_path + ' : ' + str(exception))

            pipeline.infer_each(callback_ok, callback_err)
        elif media_type == 'video' and task == 'detect':
            pipeline = vid_detection.VidDetectionPipeline(inputs, model_path)
            self.callback_count = 0
            self.update_progress_bar()
            
            def callback_progress(current_frame, total_frames):
                self.update_progress_bar(current_frame / total_frames)

            def callback_ok(input_path, output_media_path):
                logging.info('Detection done for ' + input_path + ', output in ' + output_media_path)
                result_widget = VideoResultView(input_path, output_media_path)
                self._add_new_tab(result_widget, "Video detection", len(self._input_path) == 1)
                self.callback_count += 1
                self.update_progress_bar()

            def callback_err(input_media_path, exception):
                logging.error('Detection failed for ' + input_media_path + ' : ' + str(exception))

            pipeline.infer_each(callback_progress, callback_ok, callback_err)

    def update_progress_bar(self, extra=0.0):
        base = self.callback_count / len(self._input_path)
        extra = extra / len(self._input_path)

        self._progress_bar.setValue(int((base + extra) * 100))

      

