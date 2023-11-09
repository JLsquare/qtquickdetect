from PyQt6.QtCore import QThread, pyqtSignal


class InferenceThread(QThread):
    progress_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(str, str)
    error_signal = pyqtSignal(str, Exception)

    def __init__(self, pipeline, parent=None):
        super().__init__(parent)
        self.pipeline = pipeline

    def run(self):
        try:
            self.pipeline.infer_each(self.progress_signal.emit, self.finished_signal.emit, self.error_signal.emit)
        except Exception as e:
            self.error_signal.emit('', e)
