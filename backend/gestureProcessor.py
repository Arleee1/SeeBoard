import mouse
import numpy
import pyautogui
from backend.mode import Mode
import mouse
from constants import left_bound_x, right_bound_x, top_bound_y, bottom_bound_y, margin

velocity_x_scale = .1
velocity_y_scale = .1

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
        self.pos_x, self.pos_y = 0, 0

    def process_gesture(self, hand):
        if self.mode.get_mode() == "navigation":
            # self.handle_navigation_movement((hand['velocity_x'], hand['velocity_y']))
            pass
        else:
            self.handle_keyboard_movement((hand['dampened_x'], hand['dampened_y']))

        is_tilted = hand["angle"] > 135 or hand["angle"] < -135

        if is_tilted and not self.has_changed_mode:
            self.tilt_ct += 1

        if not is_tilted:
            self.tilt_ct = 0
            self.has_changed_mode = False

        if self.tilt_ct == 5 and not self.has_changed_mode:
            self.swap_mode()
            self.has_changed_mode = True

        is_closed = not hand['is_open']

        if is_closed and not self.has_clicked:
            self.hasClosedFor += 1

        if not is_closed:
            self.hasClosedFor = 0
            self.has_clicked = False

        if self.hasClosedFor == 5 and not self.has_clicked:
            self.mouse_click()
        else:
            if hand['is_open']:
                self.hasClosedFor = 0
            else:
                self.hasClosedFor += 1

    def reset_hand_close(self):
        self.hasClosedFor = 0
        self.has_clicked = True

    def handle_navigation_movement(self, velocity):
        self.pos_x += velocity[0] * velocity_x_scale
        self.pos_y += velocity[1] * velocity_y_scale

        self.pos_x = max(0, min(self.pos_x, self.screen_width))
        self.pos_y = max(0, min(self.pos_y, self.screen_height))

        mouse.move(self.pos_x, self.pos_y)

    def handle_keyboard_movement(self, position):
        x = (position[0] - left_bound_x) / (right_bound_x - left_bound_x) * self.screen_width
        y = (position[1] - top_bound_y) / (bottom_bound_y - top_bound_y) * self.screen_height

        self.last_mouse_pos = x, y

        x = max(self.window_x + margin, min(x, self.window_x + self.screen_width) - margin)
        y = max(self.window_y + margin, min(y, self.window_y + self.screen_height) - margin)
        
        mouse.move(x, y)

    def mouse_click(self):
        mouse.click('left')

    def swap_mode(self):
        cur_mode = self.mode.swap_mode()
        self.reset_hand_close()
        if cur_mode == "keyboard" and self.pyqt_gui:
            window_geometry = self.pyqt_gui.geometry()
            self.screen_width, self.screen_height = window_geometry.width(), window_geometry.height()
            self.window_x, self.window_y = window_geometry.x(), window_geometry.y()
        else:
            self.screen_width, self.screen_height = pyautogui.size()
            self.window_x = 0
            self.window_y = 0

        if cur_mode == "navigation":
            self.mouse_home_x, self.mouse_home_y = self.last_mouse_pos

        print("Mode swapped to", cur_mode)
