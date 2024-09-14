import pyautogui
from mode import Mode

class GestureToAction:
    def __init__(self):
        self.mode = Mode()
        self.gestures_map = {
            'pinch': self.mouse_click,
            'rotate': self.swap_mode
        }
  
    def map_gesture(self, gesture_name):
        if gesture_name in self.gestures_map:
            return self.gestures_map[gesture_name]
        else:
            print("Gesture not found")

    def execute_gesture(self, function_name):
        if callable(function_name):
            function_name()
        else:
            print("Gesture not found")

    def handle_movement(self, position):
        screen_width, screen_height = pyautogui.size()
        x = int(position[0] * screen_width)
        y = int(position[1] * screen_height)
        pyautogui.moveTo(x, y)

    def mouse_click(self):
        pyautogui.click()

    def swap_mode(self):
        if self.mode.get_mode() == "navigation":
            self.mode.change_mode("keyboard")
        elif self.mode.get_mode() == "keyboard":
            self.mode.change_mode("drawing")
        else:
            self.mode.change_mode("navigation")
