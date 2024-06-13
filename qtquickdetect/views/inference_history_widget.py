import json
import logging
import os

from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from ..models.app_state import AppState
from ..models.preset import Preset
from ..views.image_result_widget import ImageResultWidget
from ..views.video_result_widget import VideoResultWidget


class InferenceHistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._appstate = AppState.get_instance()
        self._row_folder = []

        # PyQT6 Components
        self._main_layout: Optional[QVBoxLayout] = None
        self._table: Optional[QTableWidget] = None
        self._current_widget: Optional[QWidget] = None

        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(['Media', 'Collection', 'Preset', 'Task', 'Date', 'Weights'])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setShowGrid(False)
        self._table.setProperty('class', 'border')
        self.populate_table()
        self._main_layout.addWidget(self._table)
        self.setLayout(self._main_layout)
        self._table.itemDoubleClicked.connect(self.open_result)

    def populate_table(self):
        self._table.setRowCount(0)
        history = self.get_history()
        self._table.setRowCount(len(history))
        for i, item in enumerate(history):
            media_item = QTableWidgetItem(item['media'])
            collection_item = QTableWidgetItem(item['collection'])
            preset_item = QTableWidgetItem(item['preset'])
            task_item = QTableWidgetItem(item['task'])
            date_item = QTableWidgetItem(item['date'])
            weights_item = QTableWidgetItem(item['weights'])
            self._table.setItem(i, 0, media_item)
            self._table.setItem(i, 1, collection_item)
            self._table.setItem(i, 2, preset_item)
            self._table.setItem(i, 3, task_item)
            self._table.setItem(i, 4, date_item)
            self._table.setItem(i, 5, weights_item)
        self._table.resizeColumnsToContents()
        for i in range(6):
            self._table.setColumnWidth(i, self._table.columnWidth(i) + 16)

    ##############################
    #         CONTROLLER         #
    ##############################

    def open_last_inference(self):
        """
        Open the last inference result
        """
        self.return_to_main_view()
        self.populate_table()
        self.open_result(self._table.item(0, 0))

    def get_history(self) -> list[dict]:
        """
        Get the history of the inference results

        :return: List of dictionaries containing the history of the inference results
        """
        if not os.path.exists('./history'):
            return []

        folders = os.listdir('./history')
        history = []
        row_folder = []

        for folder in folders:
            with open(f'./history/{folder}/info.json') as f:
                info = json.load(f)
                info['weights'] = ', '.join(info['weights'])
                row_folder.append(folder)
                history.append(info)

        # Sort the history by date and the row folder list accordingly
        paired = list(zip(history, row_folder))
        paired.sort(key=lambda x: x[0]['date'], reverse=True)
        sorted_history, self._row_folder = zip(*paired)

        return list(sorted_history)

    def open_result(self, item: QTableWidgetItem):
        """
        Open the result of the inference

        :param item: The item that was double-clicked
        """
        row = item.row()
        media_type = self._table.item(row, 0).text()
        collection_name = self._table.item(row, 1).text()
        preset_name = self._table.item(row, 2).text()
        result_folder = self._row_folder[row]
        result_path = f'./history/{result_folder}'
        preset = Preset(preset_name)
        logging.debug(f'Opening result {media_type} {collection_name} {preset_name} {result_folder}')

        if media_type == 'image':
            widget = ImageResultWidget(preset, result_path)
            self._process_image_results(widget, result_path, collection_name)
        elif media_type == 'video':
            widget = VideoResultWidget(result_path)
            self._process_video_results(widget, result_path, collection_name)
        else:
            raise ValueError('Unknown media type')

        widget.return_signal.connect(self.return_to_main_view)
        self._main_layout.removeWidget(self._table)
        self._table.hide()
        self._main_layout.addWidget(widget)
        self._current_widget = widget

    def _process_image_results(self, widget: ImageResultWidget, result_path: str, collection_name: str):
        """
        Process the image results

        :param widget: The widget to add the results to
        :param result_path: The path to the results
        :param collection_name: The name of the collection
        """
        result_path = Path(result_path)
        if not result_path.is_dir():
            logging.error(f"Result path {result_path} is not a directory")
            return

        # Get the image names from the collection
        collection_images = self._appstate.collections.get_collection_file_paths(collection_name, 'image')
        collection_images_stem = {Path(image).stem: image for image in collection_images}

        # For each weight directory in the result path
        for weight_dir in result_path.iterdir():
            if weight_dir.name == 'info.json' or not weight_dir.is_dir():
                continue

            # Get the image names from the weight directory
            dir_images = {Path(image).stem for image in weight_dir.iterdir() if image.is_file()}

            # For each image name in the collection
            for image_stem, image in collection_images_stem.items():
                # Check if the image name from the collection is in the weight directory
                if image_stem in dir_images:
                    result_json = weight_dir / f'{image_stem}.json'
                    if result_json.exists():
                        widget.add_input_and_result(image, str(result_json))
                    else:
                        logging.warning(f'Expected JSON result file {result_json} does not exist')

    def _process_video_results(self, widget: VideoResultWidget, result_path: str, collection_name: str):
        """
        Process the video results

        :param widget: The widget to add the results to
        :param result_path: The path to the results
        :param collection_name: The name of the collection
        """
        result_path = Path(result_path)
        if not result_path.is_dir():
            logging.error(f"Result path {result_path} is not a directory")
            return

        # Get the video names from the collection
        collection_videos = self._appstate.collections.get_collection_file_paths(collection_name, 'video')
        collection_videos_stem = {Path(video).stem: video for video in collection_videos}

        # For each weight directory in the result path
        for weight_dir in result_path.iterdir():
            if weight_dir.name == 'info.json' or not weight_dir.is_dir():
                continue

            # Get the video names from the weight directory
            result_files = list(weight_dir.iterdir())
            result_files_stem = {f.stem: f for f in result_files if
                                 f.is_file() and f.suffix in ['.mp4', '.avi'] and not f.name.endswith('.json')}

            # For each video name in the collection
            for video_stem, video in collection_videos_stem.items():
                result_video = result_files_stem.get(video_stem)

                # Check if the video name from the collection is in the weight directory
                if result_video:
                    result_json = weight_dir / f'{video_stem}.json'
                    if result_json.exists():
                        widget.add_input_and_result(video, str(result_video), str(result_json))
                    else:
                        logging.warning(f'Expected JSON result file {result_json} does not exist')

    def return_to_main_view(self):
        """
        Return to the main view
        """
        if self._current_widget is not None:
            self._main_layout.removeWidget(self._current_widget)
            self._current_widget.deleteLater()
            self._current_widget = None
        self._main_layout.addWidget(self._table)
        self._table.show()
