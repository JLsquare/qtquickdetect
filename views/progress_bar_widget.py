from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QProgressBar


class ProgressBarWidget(QProgressBar):
    def __init__(self):
        super().__init__()
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self.setRange(0, 100)
        self.setValue(0)
        self.setTextVisible(True)
        self.setFormat('%p%')
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    ##############################
    #         CONTROLLER         #
    ##############################

    def update_progress_bar(self, progress: int, total: int, extra: float):
        self.setValue(int(((progress + extra) / total) * 100))