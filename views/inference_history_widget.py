import json
import os
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem

from models.app_state import AppState
from models.preset import Preset
from views.image_result_widget import ImageResultWidget
from views.video_result_widget import VideoResultWidget


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

    ##############################
    #         CONTROLLER         #
    ##############################

    def get_history(self) -> list[dict]:
        if not os.path.exists('./history'):
            return []
        folders = os.listdir('./history')
        history = []
        for folder in folders:
            with open(f'./history/{folder}/info.json') as f:
                info = json.load(f)
                info['weights'] = ', '.join(info['weights'])
                self._row_folder.append(folder)
                history.append(info)
        return history

    def open_result(self, item: QTableWidgetItem):
        row = item.row()
        media_type = self._table.item(row, 0).text()
        collection_name = self._table.item(row, 1).text()
        preset_name = self._table.item(row, 2).text()
        result_folder = self._row_folder[row]
        result_path = f'./history/{result_folder}'
        preset = Preset(preset_name)

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

    def _process_image_results(self, widget: ImageResultWidget, result_path, collection_name):
        for weight_dir in os.listdir(result_path):
            if weight_dir == 'info.json':
                continue
            weight_path = os.path.join(result_path, weight_dir)
            for image in self._appstate.collections.get_collection_file_paths(collection_name, 'image'):
                image_name = os.path.basename(image)
                if image_name in os.listdir(weight_path):
                    image_basename = Path(image).stem
                    result_json = os.path.join(weight_path, f'{image_basename}.json')
                    widget.add_input_and_result(image, result_json)

    def _process_video_results(self, widget: VideoResultWidget, result_path, collection_name):
        for weight_dir in os.listdir(result_path):
            if weight_dir == 'info.json':
                continue
            weight_path = os.path.join(result_path, weight_dir)
            for video in self._appstate.collections.get_collection_file_paths(collection_name, 'video'):
                video_name = os.path.basename(video)
                video_basename = Path(video).stem
                result_files = os.listdir(weight_path)

                result_video = next((f for f in result_files
                                     if f.startswith(video_basename)
                                     and f != video_name
                                     and not f.endswith('.json')
                                     and (f.endswith('.mp4') or f.endswith('.avi'))), None)

                if result_video:
                    result_video_path = os.path.join(weight_path, result_video)
                    result_json = os.path.join(weight_path, f'{video_basename}.json')
                    widget.add_input_and_result(video, result_video_path, result_json)

    def return_to_main_view(self):
        self._main_layout.removeWidget(self._current_widget)
        self._current_widget.deleteLater()
        self._current_widget = None
        self._main_layout.addWidget(self._table)
        self._table.show()
