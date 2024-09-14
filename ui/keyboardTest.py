import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGridLayout
from PyQt5.QtCore import Qt

class TransparentKeyboard(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(0.3) 
        
        layout = QGridLayout()
        
        keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['Space', 'Enter']
        ]
        
        for row, key_row in enumerate(keys):
            for col, key in enumerate(key_row):
                button = QPushButton(key)
                button.clicked.connect(self.handle_key_click)
                layout.addWidget(button, row, col)
        
        self.setLayout(layout)
        
    def handle_key_click(self):
        button = self.sender() 
        key_value = button.text() 
        print(f"Key pressed: {key_value}")  

app = QApplication(sys.argv)


keyboard = TransparentKeyboard()
keyboard.setWindowTitle("Transparent Keyboard")
keyboard.resize(400, 300) 
keyboard.show()

# Execute the application
sys.exit(app.exec_())
