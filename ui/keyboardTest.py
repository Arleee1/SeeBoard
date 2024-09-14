import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class TransparentKeyboard(QWidget):
    def __init__(self):
        super().__init__()

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
        self.layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins around the 
        self.layout.setSpacing(5)

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
        """Creates a QPushButton for a key with uniform size."""
        button = QPushButton(key)
        button.setStyleSheet(self.button_style())
        button.setGraphicsEffect(self.create_shadow())
        button.setFont(QFont("Arial", 16, QFont.Bold))

        # Set uniform size for most buttons
        button.setFixedSize(120, 100)  # Set same size for all buttons except larger keys

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
                self.layout.addWidget(button, 2, col, 1, 2)  # Caps Lock spans 2 columns
            else:
                self.layout.addWidget(button, 2, col + 1, 1, 1)
        # Larger Enter
        enter_button = self.create_key_button('Enter')
        self.layout.addWidget(enter_button, 2, len(row_3) - 1, 1, 2)  # Span 2 columns

        # Fourth row (Shift, ZXCV, etc.)
        row_4 = ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/']
        for col, key in enumerate(row_4[:-1]):
            button = self.create_key_button(key)
            if key == 'Shift':
                self.layout.addWidget(button, 3, col, 1, 2)  # Shift spans 2 columns
            else:
                self.layout.addWidget(button, 3, col + 1, 1, 1)
        # Add last key normally
        last_button = self.create_key_button(row_4[-1])
        self.layout.addWidget(last_button, 3, len(row_4), 1, 1)

        # Fifth row (Ctrl, Alt, Space, etc.)
        row_5 = ['Ctrl', 'Alt', 'Space']
        for col, key in enumerate(row_5):
            button = self.create_key_button(key)
            if key == 'Space':
                self.layout.addWidget(button, 4, col, 1, 7)  # Space spans 7 columns
            else:
                self.layout.addWidget(button, 4, col, 1, 1)

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
