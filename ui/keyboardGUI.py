import ctypes
import sys
import os
from queue import Queue

from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QGraphicsDropShadowEffect, QDesktopWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import QTimer
import threading

from backend.keyboardControl import keyboardControl

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cv.hands_reader import read_hands
import constants

from backend.gestureProcessor import GestureProcessor
from ui.navballGUI import NavballWidget

GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOPMOST = 0x00000008

hands_queue = Queue()
scale_factor = constants.global_gui_scale


class TransparentKeyboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setCursor(Qt.BlankCursor)  # Hide the cursor

        # Track Caps Lock state (False = lowercase, True = uppercase)
        self.caps_lock_on = False
        self.shift_on = False
        self.running = True  # Control flag for the thread

        self.view = False

        # Make the window background transparent and always stay on top
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Add WindowStaysOnTopHint
        self.set_no_activate()

        # Set up the layout for the keyboard buttons with reduced spacing
        self.layout = QGridLayout()

        # Reduce horizontal and vertical gaps between buttons
        self.layout.setHorizontalSpacing(0)  # Reduced horizontal spacing
        self.layout.setVerticalSpacing(0)    # Reduced vertical spacing

        # Optionally, you can reduce the margins around the grid
        self.layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins around the grid
        self.layout.setSpacing(5)

        # Generate the full keyboard layout
        self.generate_keyboard()

        # Set the layout to the window
        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start(int(1000*(1./constants.FRAME_RATE)) - 5)  # Call every 100 milliseconds
        self.processor = GestureProcessor(pyqt_gui=self)
        self.mode = self.processor.mode.mode

        self.navball = NavballWidget([0, 0])
        self.navball.setWindowTitle("Navball")
        self.navball.setGeometry(100, 100, 400, 400)

    def set_no_activate(self):
        # Get window handle (HWND)
        hWnd = self.winId()

        if not isinstance(hWnd, int):
            hWnd = int(hWnd)

        # Load user32.dll
        user32 = ctypes.windll.user32

        # Get current extended style
        exStyle = user32.GetWindowLongPtrW(hWnd, GWL_EXSTYLE)

        # Add WS_EX_NOACTIVATE and WS_EX_TOPMOST flags
        newExStyle = exStyle | WS_EX_NOACTIVATE | WS_EX_TOPMOST

        # Apply new extended window style
        user32.SetWindowLongPtrW(hWnd, GWL_EXSTYLE, newExStyle)

    def on_timeout(self):
        self.processor.set_frame_geometry(self.geometry())
        if not hands_queue.empty():
            left_hand, right_hand = hands_queue.get()
            if right_hand['exists']:
                res = self.processor.process_gesture(right_hand)
                if res is not None:
                    velocity, distance = res
                    self.update_navball(velocity, distance)
            elif left_hand['exists']:
                res = self.processor.process_gesture(left_hand)
                if res is not None:
                    velocity, distance = res
                    self.update_navball(velocity, distance)

        if self.processor.mode.mode != 'keyboard':
            self.hide_keyboard_show_navball()
        else:
            self.show_keyboard_hide_navball()
            if self.processor.lastNonKeyboardClick[1] > 0.5:
                self.moveToTop()
            elif self.processor.lastNonKeyboardClick[1] >= 0:
                self.moveToBottom()

    def update_navball(self, velocity, distance):
        self.navball.update_navball(velocity, distance)
    
    def hide_keyboard_show_navball(self):
        self.navball.show()
        self.hide()
    
    def show_keyboard_hide_navball(self):
        self.navball.hide()
        self.show()

    def moveToBottom(self):
        screen_geometry = QDesktopWidget().availableGeometry()
        window_width = int(1600 * scale_factor)
        window_height = int(600 * scale_factor)
        x_position = (screen_geometry.width() - window_width) // 2
        y_position = screen_geometry.height() - window_height
        self.setGeometry(x_position, y_position, window_width, window_height)

        self.view = True
        self.processor.updateGeometry()

    def moveToTop(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        window_width = int(1600 * scale_factor)
        window_height = int(600 * scale_factor)
        x_position = (screen_geometry.width() - window_width) // 2
        y_position = 0
        self.setGeometry(x_position, y_position, window_width, window_height)

        self.view = False
        self.processor.updateGeometry()

    def button_style(self):
        return """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.6);
                color: black;
                border: 2px solid black;
                border-radius: 8px;
                font-size: 18px;  /* Increase font size */
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: white;
            }
            QPushButton:pressed {
                background-color: lightgray;
            }
        """

    def create_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(3)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 150))
        return shadow

    def create_key_button(self, key):
        button = QPushButton(key)
        button.setStyleSheet(self.button_style())
        button.setGraphicsEffect(self.create_shadow())
        button.setFont(QFont("Arial", 16, QFont.Bold))

        # Set different sizes based on the key type
        if key == 'Space':
            button.setFixedSize(int(620 * scale_factor), int(110 * scale_factor))  # Large space key
        elif key == 'Tab' or key == 'Caps Lock' or key == 'Shift' or key == 'Backspace' or key == 'Enter':
            button.setFixedSize(int(250 * scale_factor), int(110 * scale_factor))  # Larger modifier keys
        else:
            button.setFixedSize(int(120 * scale_factor), int(110 * scale_factor))  # Regular size for other keys

        button.clicked.connect(self.handle_key_click)
        return button

    def generate_keyboard(self):
        if self.shift_on:
            row_1 = ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', 'Backspace']
        else:
            row_1 = ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace']
        for col, key in enumerate(row_1[:-1]):
            button = self.create_key_button(key)
            self.layout.addWidget(button, 0, col, 1, 1)
        # Larger Backspace
        backspace_button = self.create_key_button('Backspace')
        self.layout.addWidget(backspace_button, 0, len(row_1) - 1, 1, 2)  # Span 2 columns

        # Second row (Tab, QWERTY, symbols)
        if self.shift_on:
            row_2 = ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '|']
        elif self.caps_lock_on:
            row_2 = ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\']
        else:
            row_2 = ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\']
        for col, key in enumerate(row_2):
            button = self.create_key_button(key)
            if key == 'Tab':
                self.layout.addWidget(button, 1, col, 1, 2)  # Tab spans 2 columns
            elif key == '\\':
                self.layout.addWidget(button, 1, 14, 1, 1)
            else:
                self.layout.addWidget(button, 1, col + 1, 1, 1)

        # Third row (Caps Lock, ASDF, Enter)
        if self.shift_on:
            row_3 = ['Caps Lock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"', 'Enter']
        elif self.caps_lock_on:
            row_3 = ['Caps Lock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'', 'Enter']
        else:
            row_3 = ['Caps Lock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'Enter']
        for col, key in enumerate(row_3[:-1]):
            button = self.create_key_button(key)
            if key == 'Caps Lock':
                self.layout.addWidget(button, 2, col, 1, 2)
            else:
                self.layout.addWidget(button, 2, col + 1, 1, 1)
        enter_button = self.create_key_button('Enter')
        self.layout.addWidget(enter_button, 2, len(row_3), 1, 2) 

        if self.shift_on:
            row_4 = ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', 'Up', 'Shift']
        elif self.caps_lock_on:
            row_4 = ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Up', 'Shift']
        else: 
            row_4 = ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Up', 'Shift']
        first_shift_flag = True
        # take into account column offset for the shift key
        for col, key in enumerate(row_4):
            button = self.create_key_button(key)
            if key == 'Shift':
                if first_shift_flag:
                    self.layout.addWidget(button, 3, col, 1, 2)
                    first_shift_flag = False
                else:
                    self.layout.addWidget(button, 3, col + 1, 1, 2)
            else:
                self.layout.addWidget(button, 3, col + 1, 1, 1)

        row_5 = ['Exit', 'Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Ctrl', 'Left', 'Down', 'Right', 'View']
        # space key should take up the remaining space
        space_flag = False

        for col, key in enumerate(row_5):
            button = self.create_key_button(key)
            if key == 'Space':
                self.layout.addWidget(button, 4, col, 1, 7)
                space_flag = True
            else:
                if space_flag:
                    self.layout.addWidget(button, 4, col + 4, 1, 1)
                else:
                    self.layout.addWidget(button, 4, col, 1, 1)

    def handle_key_click(self):
        button = self.sender()  # Get the clicked button
        key_value = button.text()  # Get the key's text
        if key_value == 'Caps Lock':
            self.caps_lock_on = not self.caps_lock_on
            self.clear_layout()
            self.generate_keyboard()
        elif key_value == 'Shift':
            self.shift_on = not self.shift_on
            self.clear_layout()
            self.generate_keyboard()
        elif key_value == 'Exit':
            self.running = False 
            os._exit(0)
        elif key_value == 'View':
            # put the keyboard at the top/bottom of screen
            if not self.view:
                self.moveToBottom()
            else:
                self.moveToTop()
            self.processor.lastNonKeyboardClick = (-1, -1)
            
        print(f"Key pressed: {key_value}")  # Print the key (You can customize this)
        controller = keyboardControl()
        controller.keyboardInput(key_value)

    def clear_layout(self):
        """Clears the layout by removing all widgets."""
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


app = QApplication(sys.argv)
keyboard = TransparentKeyboard()
keyboard.setWindowTitle("Realistic Keyboard")

screen_geometry = QDesktopWidget().screenGeometry()

window_width = int(1600 * scale_factor)
window_height = int(600 * scale_factor)

x_position = (screen_geometry.width() - window_width) // 2
y_position = 0

keyboard.setGeometry(x_position, y_position, window_width, window_height)

threading.Thread(target=read_hands, args=(hands_queue,)).start()
keyboard.show()
sys.exit(app.exec_())
