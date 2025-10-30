import sys
import cv2
import time
import numpy as np
from PySide6.QtCore import (
    QTimer
)
from PySide6.QtGui import (
    QPainter,
    QPixmap,
    QImage,
)
from PySide6.QtWidgets import (
    QApplication,
    QLabel
)
from game import MonsterHunterWorld


class ImageWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__pixmap = None

        self.setFixedSize(512, 288)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.captureGame)
        self.update_timer.start(1)

    def captureGame(self):
        start_time = time.time()
        image = MonsterHunterWorld.Window.Screenshot(resize=(256, 144))
        print(f"\r{time.time() - start_time}", end="", flush=True)
        self.setImage(image)

    def setImage(self, image: np.ndarray = None):
        if image is None:
            self.__pixmap = None
        else:
            image = cv2.resize(
                image,
                (self.width(), self.height()),
                interpolation=cv2.INTER_NEAREST
            )
            height, width, channels = image.shape
            pixmap = QPixmap.fromImage(QImage(
                image.data,
                width, height,
                width * channels,
                QImage.Format.Format_RGB888
            ))
            self.__pixmap = pixmap
        self.update()

    def clearImage(self):
        self.setImage(None)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        if self.__pixmap is not None:
            painter.drawPixmap(0, 0, self.__pixmap)
        painter.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ImageWidget()
    w.show()
    sys.exit(app.exec())