from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QGraphicsView


class ResizeableGraphicsWidget(QGraphicsView):
    """
    ResizeableGraphicsWidget is a QGraphicsView that resizes the scene to fit the view.
    """
    def __init__(self, scene, parent=None):
        """
        Initializes the ResizeableGraphicsWidget.

        :param scene: The QGraphicsScene to display.
        :param parent: The parent widget.
        """
        super().__init__(scene, parent)
        self.init_ui()

    ##############################
    #           VIEW             #
    ##############################

    def init_ui(self) -> None:
        """
        Initializes the user interface components.
        """
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    ##############################
    #         CONTROLLER         #
    ##############################

    def resizeEvent(self, event) -> None:
        """
        Resize the scene to fit the view.

        :param event: The resize event.
        """
        super().resizeEvent(event)
        self.fitInView(self.scene().itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
