import mouse
import numpy
import pyautogui
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QCursor
from backend.mode import Mode
import mouse
from numpy.linalg import norm

left_bound_x, right_bound_x = .2, .8
top_bound_y, bottom_bound_y = .4, .8
velocity_x_scale, velocity_y_scale = .7, .7

class GestureProcessor:
    def __init__(self, pyqt_gui):
        self.mode = Mode()
        self.pyqt_gui = pyqt_gui
        self.screen_width, self.screen_height = pyautogui.size()
        self.window_x, self.window_y = 0, 0
        self.hasClosedFor = 0
        self.tilt_ct = 0
        self.has_changed_mode = True
        self.lastNonKeyboardClick = (0, 0)
        self.isMousePressed = False
        self.has_clicked = True
        self.mouse_home_x = 0.5
        self.mouse_home_y = 0.5
        self.last_mouse_pos = (0.5, 0.5)
        self.qt_left_x = -1
        self.qt_width = -1
        self.qt_top_y = -1
        self.qt_height = -1

        self.velocity = [0, 0]
        self.pos_x = 0
        self.pos_y = 0


    def process_gesture(self, hand):
        res = None
        if self.mode.get_mode() == "navigation":
            res = self.handle_navigation_movement((hand['x'], hand['y']))
        else:
            self.handle_keyboard_movement((hand['dampened_x'], hand['dampened_y']))

        is_tilted = hand["angle"] > 135 or hand["angle"] < -135

        if is_tilted and not self.has_changed_mode:
            self.tilt_ct += 1

        if not is_tilted:
            self.tilt_ct = 0
            self.has_changed_mode = False

        is_closed = not hand['is_open']

        if is_closed and not self.has_clicked:
            self.hasClosedFor += 1

        if not is_closed:
            self.hasClosedFor = 0
            self.has_clicked = False

        if self.hasClosedFor == 5 and not self.has_clicked:
            self.mouse_click()
            if self.mode.mode != "keyboard":
                self.lastNonKeyboardClick = (hand['dampened_x'], hand['dampened_y'])
            print(self.lastNonKeyboardClick)
        else:
            if hand['is_open']:
                self.hasClosedFor = 0
                if self.isMousePressed:
                    mouse.release('left')
                    self.isMousePressed = False
            else:
                self.hasClosedFor += 1

        if self.tilt_ct == 5 and not self.has_changed_mode:
            self.swap_mode()
            self.has_changed_mode = True
        
        return res

    def set_frame_geometry(self, geometry: QRect):
        self.qt_left_x = geometry.left()
        self.qt_width = geometry.width()
        self.qt_top_y = geometry.top()
        self.qt_height = geometry.height()

    def reset_hand_close(self):
        self.hasClosedFor = 0
        self.has_clicked = True

    def handle_navigation_movement(self, position):
        x = (position[0] - left_bound_x) / (right_bound_x - left_bound_x) * self.screen_width
        y = (position[1] - top_bound_y) / (bottom_bound_y - top_bound_y) * self.screen_height

        mouse_home = numpy.array([self.mouse_home_x, self.mouse_home_y], dtype=float)
        controller_coords = numpy.array([x, y])

        diff = controller_coords - mouse_home
        dist = norm(diff)
        controller_coords_unit_vec = diff / dist if dist != 0 else numpy.array([0, 0])

        zero_dist = 300

        if dist < zero_dist:
            velocity = numpy.array([0, 0])
        else:
            velocity = (0.03 * (dist - zero_dist)) * controller_coords_unit_vec

        velocity_magnitude = norm(velocity)
        if velocity_magnitude != 0:
            velocity = velocity / velocity_magnitude

        res = velocity

        velocity = velocity * numpy.sqrt(dist)

        max_velocity = 10
        if velocity_magnitude > max_velocity:
            velocity = res * max_velocity

        self.pos_x += velocity[0] * velocity_x_scale
        self.pos_y += velocity[1] * velocity_y_scale

        self.pos_x = max(0, min(self.pos_x, self.screen_width))
        self.pos_y = max(0, min(self.pos_y, self.screen_height))

        mouse.move(self.pos_x, self.pos_y)

        return (res, dist)

    def handle_keyboard_movement(self, position):
        # print(position, end="")
        x = (position[0] - left_bound_x) / (right_bound_x - left_bound_x)
        y = (position[1] - top_bound_y) / (bottom_bound_y - top_bound_y)

        # print(f"norm: {x, y}", end="")
        self.last_mouse_pos = x * self.screen_width, y * self.screen_height
    
        # x = max(self.window_x + margin, min(x, self.window_x + self.screen_width) - margin)
        # y = max(self.window_y + margin, min(y + self.window_y, self.window_y + self.screen_height) - margin)
        # print(f", w: {self.qt_width}, l: {self.qt_left_x}, h: {self.qt_height}, t: {self.qt_top_y}", end="")
        x = x * self.qt_width + self.qt_left_x
        y = y * self.qt_height + self.qt_top_y
        # print("2: ", x, y)
        # print(f", xl,y: {x, y}")

        margin = 15
        if x < self.qt_left_x + margin:
            x = self.qt_left_x + margin
        if x > self.qt_left_x + self.qt_width - margin:
            x = self.qt_left_x + self.qt_width - margin

        if y < self.qt_top_y + margin:
            y = self.qt_top_y + margin
        if y > self.qt_top_y + self.qt_height - margin:
            y = self.qt_top_y + self.qt_height - margin

        mouse.move(x, y)

    def mouse_click(self):
        mouse.click('left')
        self.isMousePressed = True
        self.has_clicked = True

    def swap_mode(self):
        cur_mode = self.mode.swap_mode()
        self.reset_hand_close()
        if cur_mode == "keyboard" and self.pyqt_gui:
            self.updateGeometry()
        else:
            self.screen_width, self.screen_height = pyautogui.size()
            self.window_x = 0
            self.window_y = 0

        if cur_mode == "navigation":
            self.mouse_home_x, self.mouse_home_y = self.last_mouse_pos
            self.pos_x, self.pos_y = self.mouse_home_x, self.mouse_home_y

    def updateGeometry(self):
        window_geometry = self.pyqt_gui.geometry()
        self.screen_width, self.screen_height = window_geometry.width(), window_geometry.height()
        self.window_x, self.window_y = window_geometry.x(), window_geometry.y()
