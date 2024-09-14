import mouse
import pyautogui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from backend.mode import Mode
import mouse

class GestureProcessor:
    def __init__(self, pyqt_gui):
        self.mode = Mode()
        self.pyqt_gui = pyqt_gui
        self.screen_width, self.screen_height = pyautogui.size()
        self.window_x, self.window_y = 0, 0
        self.hasClicked = False
        self.hasChangedMode = False

    def process_gesture(self, hand):
        self.handle_movement((hand['x'], hand['y']))

        if not hand['is_open'] and not self.hasClicked:
            self.mouse_click()
            self.hasClicked = True
        else:
            if hand['is_open']:
                self.hasClicked = False
        
        if hand['angle'] > 120 and not self.hasChangedMode:
            self.swap_mode()
            self.hasChangedMode = True
        else:
            if hand['angle'] < 120:
                self.hasChangedMode = False

    def handle_movement(self, position):
        x = int(position[0] * self.screen_width)
        y = int(position[1] * self.screen_height)
        
        if self.mode.get_mode() == "keyboard" and self.pyqt_gui:
            x = max(self.window_x, min(x, self.window_x + self.screen_width))
            y = max(self.window_y, min(y + self.window_y, self.window_y + self.screen_height))
        
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