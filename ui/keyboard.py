import sys
import os
from queue import Queue

from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import QTimer
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cv.hands_reader import read_hands
import constants

from backend.gestureProcessor import GestureProcessor

hands_queue = Queue()
class TransparentKeyboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setCursor(Qt.BlankCursor)  # Hide the cursor

        # Track Caps Lock state (False = lowercase, True = uppercase)
        self.caps_lock_on = False

        # Make the window background transparent and always stay on top
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Add WindowStaysOnTopHint

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

    def on_timeout(self):
        if not hands_queue.empty():
            left_hand, right_hand = hands_queue.get()
            if right_hand['exists']:
                self.processor.process_gesture(right_hand)
            elif left_hand['exists']:
                self.processor.process_gesture(left_hand)
            # else:
                # print("No hands detected")

    def button_style(self):
        """Returns the stylesheet for the buttons."""
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
        """Creates and returns a shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(3)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 150))
        return shadow

    def create_key_button(self, key):
        """Creates a QPushButton for a key with variable size based on the key type."""
        button = QPushButton(key)
        button.setStyleSheet(self.button_style())
        button.setGraphicsEffect(self.create_shadow())
        button.setFont(QFont("Arial", 16, QFont.Bold))

        # Set different sizes based on the key type
        if key == 'Space':
            button.setFixedSize(620, 110)  # Large space key
        elif key == 'Tab' or key == 'Caps Lock' or key == 'Shift' or key == 'Backspace' or key == 'Enter':
            button.setFixedSize(250, 110)  # Larger modifier keys
        else:
            button.setFixedSize(120, 110)  # Regular size for other keys

        button.clicked.connect(self.handle_key_click)
        return button

    def generate_keyboard(self):
        """Generates a full keyboard layout with larger keys where necessary."""
        # First row (Tilde, numbers, and symbols)
        row_1 = ['~', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace']
        for col, key in enumerate(row_1[:-1]):
            button = self.create_key_button(key)
            self.layout.addWidget(button, 0, col, 1, 1)
        # Larger Backspace
        backspace_button = self.create_key_button('Backspace')
        self.layout.addWidget(backspace_button, 0, len(row_1) - 1, 1, 2)  # Span 2 columns

        # Second row (Tab, QWERTY, symbols)
        row_2 = ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\']
        for col, key in enumerate(row_2):
            button = self.create_key_button(key)
            if key == 'Tab':
                self.layout.addWidget(button, 1, col, 1, 2)  # Tab spans 2 columns
            else:
                self.layout.addWidget(button, 1, col + 1, 1, 1)

        # Third row (Caps Lock, ASDF, Enter)
        row_3 = ['Caps Lock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'', 'Enter']
        for col, key in enumerate(row_3[:-1]):
            button = self.create_key_button(key)
            if key == 'Caps Lock':
                self.layout.addWidget(button, 2, col, 1, 2)
            else:
                self.layout.addWidget(button, 2, col + 1, 1, 1)
        enter_button = self.create_key_button('Enter')
        self.layout.addWidget(enter_button, 2, len(row_3), 1, 2) 

        row_4 = ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Up', 'Shift']
        for col, key in enumerate(row_4[:-1]):
            button = self.create_key_button(key)
            if key == 'Shift':
                self.layout.addWidget(button, 3, col, 1, 2) 
            else:
                self.layout.addWidget(button, 3, col + 1, 1, 1)
        # Add last key normally
        last_button = self.create_key_button(row_4[-1])
        self.layout.addWidget(last_button, 3, len(row_4), 1, 1)

        # Fifth row (Ctrl, Alt, Space, etc.)
        spaceExists = False
        row_5 = ['Ctrl', 'Fn', 'Win', 'Alt', 'Space', 'Alt', 'Ctrl', 'Left', 'Down', 'Right']
        for col, key in enumerate(row_5):
            button = self.create_key_button(key)
            if key == 'Space':
                self.layout.addWidget(button, 4, 4, 1, 7)  # Space spans 7 columns
                spaceExists = True
            else:
                if spaceExists:
                    self.layout.addWidget(button, 4, col + 4, 1, 1)  # Shift the keys after Space
                else:
                    self.layout.addWidget(button, 4, col, 1, 1)  # Ctrl and Alt keys don't overlap

    def handle_key_click(self):
        button = self.sender()  # Get the clicked button
        key_value = button.text()  # Get the key's text
        print(f"Key pressed: {key_value}")  # Print the key (You can customize this)


# Main application code
app = QApplication(sys.argv)
# Create the main window (keyboard)
keyboard = TransparentKeyboard()
keyboard.setWindowTitle("Realistic Keyboard")
keyboard.resize(1600, 600)  # Larger window size to accommodate keys and spacing
threading.Thread(target=read_hands, args=(hands_queue,)).start()
keyboard.show()

# Execute the application
sys.exit(app.exec_())
