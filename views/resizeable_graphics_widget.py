from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtWidgets import QGraphicsView, QGraphicsPixmapItem


class ResizeableGraphicsWidget(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self._initial_pixmaps = {}
        for item in self.scene().items():
            if isinstance(item, QGraphicsPixmapItem):
                self._initial_pixmaps[item] = item.pixmap()

    def resizeEvent(self, event):
        self.scene().setSceneRect(QRectF(self.viewport().rect()))
        for item in self.scene().items():
            if isinstance(item, QGraphicsPixmapItem):
                initial_pixmap = self._initial_pixmaps.get(item)
                if initial_pixmap:
                    item.setPixmap(initial_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                         Qt.TransformationMode.SmoothTransformation))
        QGraphicsView.resizeEvent(self, event)
