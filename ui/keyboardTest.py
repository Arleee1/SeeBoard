import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class TransparentKeyboard(QWidget):
    def __init__(self):
        super().__init__()
        
        # Make the window background transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Set up the layout for the keyboard buttons
        layout = QGridLayout()

        # List of keyboard keys to display
        keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['Space', 'Enter']
        ]
        
        # Add buttons to the layout in a grid
        for row, key_row in enumerate(keys):
            for col, key in enumerate(key_row):
                button = QPushButton(key)
                button.clicked.connect(self.handle_key_click)

                # Set buttons to transparent by default, but solid on hover
                button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 0);  /* Fully transparent */
                        color: black;
                        border: 2px solid black;
                        border-radius: 10px;
                        padding: 10px;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: white;  /* Solid on hover */
                    }
                """)
                layout.addWidget(button, row, col)

        # Set the layout to the window
        self.setLayout(layout)

    def handle_key_click(self):
        button = self.sender()  # Get the clicked button
        key_value = button.text()  # Get the key's text
        print(f"Key pressed: {key_value}")  # Print the key (You can customize this)


# Main application code
app = QApplication(sys.argv)

# Create the main window (keyboard)
keyboard = TransparentKeyboard()
keyboard.setWindowTitle("Transparent Keyboard")
keyboard.resize(600, 300)  # Set an initial size for the keyboard window
keyboard.show()

# Execute the application
sys.exit(app.exec_())
