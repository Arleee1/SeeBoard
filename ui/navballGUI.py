import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QPointF
from math import atan2, degrees


class NavballWidget(QWidget):
    def __init__(self, vel, parent=None):
        super().__init__(parent)
        self.vel = vel  # Velocity vector [vx, vy]
        self.initUI()

    def initUI(self):
        self.setMinimumSize(400, 400)
        self.setWindowTitle('Navball')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Add WindowStaysOnTopHint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Center point of the widget
        center = QPointF(self.width() / 2, self.height() / 2)

        # Radius of the navball
        radius = min(self.width(), self.height()) / 2 - 40

        # Draw the navball circle
        painter.setPen(QPen(Qt.black, 2))
        painter.drawEllipse(center, radius, radius)

        # Draw the velocity vector pointer
        vel_angle = self.calculate_velocity_angle(self.vel)
        self.draw_pointer(painter, center, radius, vel_angle, Qt.red)

        # Draw labels with formatted floats
        painter.setPen(Qt.black)
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(10, 20, f"Velocity: ({self.vel[0]:.2f}, {self.vel[1]:.2f})")

    def draw_pointer(self, painter, center, radius, angle, color):
        painter.save()
        painter.translate(center)
        painter.rotate(-angle)  # Rotate coordinate system
        painter.setPen(QPen(color, 3))

        # Draw pointer line
        painter.drawLine(0, 0, 0, int(-radius + 20))  # Cast radius to int

        # Draw arrowhead
        arrow_size = 10
        painter.drawLine(0, int(-radius + 20), int(-arrow_size / 2), int(-radius + 20 + arrow_size))
        painter.drawLine(0, int(-radius + 20), int(arrow_size / 2), int(-radius + 20 + arrow_size))

        painter.restore()

    def calculate_velocity_angle(self, vel):
        # Calculate angle based on velocity components
        dx = vel[0]
        dy = vel[1]
        angle = degrees(atan2(dy, dx))
        return angle