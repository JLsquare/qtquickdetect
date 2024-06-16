from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QProgressBar


class ProgressBarWidget(QProgressBar):
    """
    ProgressBarWidget is a QProgressBar that displays the progress of a task.
    """
    def __init__(self):
        """
        Initializes the ProgressBarWidget.
        """
        super().__init__()
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self) -> None:
        """
        Initializes the user interface components.
        """
        self.setRange(0, 100)
        self.setValue(0)
        self.setTextVisible(True)
        self.setFormat('%p%')
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    ##############################
    #         CONTROLLER         #
    ##############################

    def update_progress_bar(self, progress: int, total: int, extra: float, file_name: str) -> None:
        """
        Updates the progress bar with the current progress.

        :param progress: The current progress.
        :param total: The total progress.
        :param extra: The extra progress.
        :param file_name: The name of the file.
        """
        self.setValue(int(((progress + extra) / total) * 100))
        self.setFormat(f'{file_name} - %p%')
