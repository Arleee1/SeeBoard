import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QGraphicsDropShadowEffect, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class TransparentKeyboard(QWidget):
    def __init__(self):
        super().__init__()

        # Track Caps Lock state (False = lowercase, True = uppercase)
        self.caps_lock_on = False

        # Make the window background transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Set up the layout for the keyboard buttons with reduced spacing
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(2)  # Decreased horizontal spacing

        # Generate the full keyboard layout
        self.generate_keyboard()

        # Set the layout to the window
        self.setLayout(self.layout)

    def button_style(self):
        """Returns the stylesheet for the buttons."""
        return """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.6);
                color: black;
                border: 2px solid black;
                border-radius: 8px;
                padding: 20px;  /* Adjust padding for larger keys */
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
        """Creates a QPushButton for a key."""
        button = QPushButton(key)
        button.setStyleSheet(self.button_style())
        button.setGraphicsEffect(self.create_shadow())
        button.setFont(QFont("Arial", 16, QFont.Bold))
        button.clicked.connect(self.handle_key_click)
        return button

    def generate_keyboard(self):
        """Generates a full keyboard layout."""
        # First row (Tilde, numbers, and symbols)
        row_1 = ['~', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace']
        for col, key in enumerate(row_1):
            button = self.create_key_button(key)
            span = 2 if key == 'Backspace' else 1
            self.layout.addWidget(button, 0, col, 1, span)

        # Second row (Tab, QWERTY, symbols)
        row_2 = ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\']
        for col, key in enumerate(row_2):
            button = self.create_key_button(key)
            span = 3 if key == 'Tab' else 1  # Increase Tab's span
            self.layout.addWidget(button, 1, col, 1, span)

        # Third row (Caps Lock, ASDF, Enter) + add offset
        row_3 = ['Caps Lock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', '\'', 'Enter']
        for col, key in enumerate(row_3):
            button = self.create_key_button(key)
            if key == 'Caps Lock':
                self.layout.addWidget(button, 2, col, 1, 2)  # Caps Lock spans 2 columns
                self.layout.addWidget(QLabel(''), 2, col + 2, 1, 1)  # Add empty space after Caps Lock
            elif key == 'Enter':
                self.layout.addWidget(button, 2, col + 1, 1, 2)  # Offset Enter slightly right
            else:
                self.layout.addWidget(button, 2, col + 1, 1, 1)

        # Fourth row (Shift, ZXCV, no right Shift)
        row_4 = ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/']
        for col, key in enumerate(row_4):
            button = self.create_key_button(key)
            if key == 'Shift':
                self.layout.addWidget(button, 3, col, 1, 3)  # Shift spans 3 columns and no right Shift
                self.layout.addWidget(QLabel(''), 3, col + 2, 1, 1)  # Add space after Shift
            else:
                self.layout.addWidget(button, 3, col + 3, 1, 1)  # Shift smaller keys to the right

        # Fifth row (Ctrl, Alt, Space)
        row_5 = ['Ctrl', 'Alt', 'Space']
        for col, key in enumerate(row_5):
            button = self.create_key_button(key)
            span = 9 if key == 'Space' else 1  # Adjust Space bar to take up more space
            self.layout.addWidget(button, 4, col, 1, span)

    def handle_key_click(self):
        button = self.sender()  # Get the clicked button
        key_value = button.text()  # Get the key's text
        print(f"Key pressed: {key_value}")  # Print the key (You can customize this)


# Main application code
app = QApplication(sys.argv)

# Create the main window (keyboard)
keyboard = TransparentKeyboard()
keyboard.setWindowTitle("Realistic Keyboard")
keyboard.resize(1500, 600)  # Larger window size to accommodate keys and spacing
keyboard.show()

# Execute the application
sys.exit(app.exec_())
