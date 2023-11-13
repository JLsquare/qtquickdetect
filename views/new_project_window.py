from PyQt6.QtWidgets import QWidget


class NewProjectWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    ##############################
    #            VIEW            #
    ##############################

    def init_ui(self):
        self.setWindowTitle('QTQuickDetect New Project')
        self.setGeometry(100, 100, 480, 240)

        with open('ressources/qss/stylesheet.qss', 'r') as file:
            self.setStyleSheet(file.read())