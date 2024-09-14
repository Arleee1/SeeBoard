import pyautogui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from backend.mode import Mode

class GestureProcessor:
    def __init__(self, pyqt_gui):
        self.mode = Mode()
        self.pyqt_gui = pyqt_gui
        self.screen_width, self.screen_height = pyautogui.size()
        self.window_x, self.window_y = 0, 0

    def process_gesture(self, hand):
        print("Processing gesture")
        self.handle_movement((hand['x'], hand['y']))

        if not hand['is_open']:
            self.mouse_click()

        if hand['angle'] > 120:
            self.swap_mode()

    def handle_movement(self, position):
        print("Mouse move")
        x = int(position[0] * self.screen_width)
        y = int(position[1] * self.screen_height)
        
        if self.mode.get_mode() == "keyboard" and self.pyqt_gui:
            x = max(self.window_x, min(x, self.window_x + self.screen_width))
            y = max(self.window_y, min(y, self.window_y + self.screen_height))
        
        pyautogui.moveTo(x, y)

    def mouse_click(self):
        print("Mouse click")
        if self.mode.get_mode() == "navigation":
            pyautogui.click()
        elif self.mode.get_mode() == "keyboard":
            pyautogui.click()
        else:
            pass

    def swap_mode(self):
        print("Swapping mode")
        cur_mode = self.mode.swap_mode()
        if cur_mode == "keyboard" and self.pyqt_gui:
            window_geometry = self.pyqt_gui.geometry()
            self.screen_width, self.screen_height = window_geometry.width(), window_geometry.height()
            self.window_x, self.window_y = window_geometry.x(), window_geometry.y()
        else:
            self.screen_width, self.screen_height = pyautogui.size()
            self.window_x = 0
            self.window_y = 0