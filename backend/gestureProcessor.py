import mouse
import pyautogui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from backend.mode import Mode
import mouse

left_bound_x, right_bound_x = .2, .8
top_bound_y, bottom_bound_y = .2, .8


class GestureProcessor:
    def __init__(self, pyqt_gui):
        self.mode = Mode()
        self.pyqt_gui = pyqt_gui
        self.screen_width, self.screen_height = pyautogui.size()
        self.window_x, self.window_y = 0, 0
        self.hasClosedFor = 0
        self.tilt_ct = 0
        self.has_changed_mode = True
        self.has_clicked = True

    def process_gesture(self, hand):
        self.handle_movement((hand['dampened_x'], hand['dampened_y']))

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
            self.hasClosedFor += 1
            self.mouse_click()

        if self.tilt_ct == 5 and not self.has_changed_mode:
            self.swap_mode()
            self.has_changed_mode = True

    def reset_hand_close(self):
        self.hasClosedFor = 0

    def handle_movement(self, position):
        # x = int(position[0] * self.screen_width)
        # y = int(position[1] * self.screen_height)
        x = (position[0] - left_bound_x) / (right_bound_x - left_bound_x) * self.screen_width
        y = (position[1] - top_bound_y) / (bottom_bound_y - top_bound_y) * self.screen_height
        margin = 10
        if self.mode.get_mode() == "keyboard" and self.pyqt_gui:
            x = max(self.window_x + margin, min(x, self.window_x + self.screen_width) - margin)
            y = max(self.window_y + margin, min(y + self.window_y, self.window_y + self.screen_height) - margin)
        
        mouse.move(x, y)

    def mouse_click(self):
        if self.mode.get_mode() == "navigation":
            mouse.click('left')
        elif self.mode.get_mode() == "keyboard":
            mouse.click('left')
        else:
            pass

    def swap_mode(self):
        cur_mode = self.mode.swap_mode()
        if cur_mode == "keyboard" and self.pyqt_gui:
            window_geometry = self.pyqt_gui.geometry()
            self.screen_width, self.screen_height = window_geometry.width(), window_geometry.height()
            self.window_x, self.window_y = window_geometry.x(), window_geometry.y()
        else:
            self.screen_width, self.screen_height = pyautogui.size()
            self.window_x = 0
            self.window_y = 0
        print("Mode swapped to", cur_mode)