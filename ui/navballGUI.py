import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QPointF, QTimer
from math import atan2, degrees, sqrt


class NavballWidget(QWidget):
    def __init__(self, vel=None, parent=None):
        super().__init__(parent)
        self.vel = vel if vel is not None else [0, 0]  # Default velocity vector [vx, vy]
        self.magnitude = sqrt(self.vel[0]**2 + self.vel[1]**2)
        self.angle = self.calculate_velocity_angle(self.vel)
        self.initUI()

    def initUI(self):
        self.setMinimumSize(400, 400)
        self.setWindowTitle('Navball')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Timer to update the widget periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)  # Update every 100 ms

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

        # Draw the velocity vector dot
        self.draw_dot(painter, center, radius, self.vel, self.magnitude, Qt.red)

    def draw_dot(self, painter, center, radius, vel, magnitude, color):
        painter.save()
        painter.setPen(QPen(color, 3))
        painter.setBrush(QBrush(color, Qt.SolidPattern))

        # Calculate the position of the dot based on velocity and magnitude
        dot_radius = 10  # Radius of the dot
        vel_magnitude = sqrt(vel[0]**2 + vel[1]**2)
        
        if vel_magnitude == 0:
            scale = 0
        elif magnitude > 1000:
            scale = radius / vel_magnitude
        else:
            scale = (radius / 1000) * magnitude / vel_magnitude

        dot_x = center.x() + vel[0] * scale  # Invert x
        dot_y = center.y() + vel[1] * scale  # Invert y

        # Draw the dot
        painter.drawEllipse(QPointF(dot_x, dot_y), dot_radius, dot_radius)

        painter.restore()

    def calculate_velocity_angle(self, vel):
        # Calculate angle based on velocity components
        dx = -vel[1]  # Swap x and y, and negate
        dy = -vel[0]  # Swap x and y, and negate
        angle = degrees(atan2(dy, dx))
        return angle

    def update_navball(self, vel, magnitude):
        self.vel = vel  # Use the velocity as is
        self.magnitude = magnitude
        self.angle = self.calculate_velocity_angle(vel)
        self.update()  # Trigger a repaint


if __name__ == '__main__':
    app = QApplication(sys.argv)
    navball = NavballWidget([1, 1])
    screen_geometry = app.desktop().availableGeometry()
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()
    navball.move(0, screen_height - navball.height())
    navball.show()
    sys.exit(app.exec_())