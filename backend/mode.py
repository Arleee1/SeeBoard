class Mode:
    def __init__(self):
        self.mode = "keyboard"

    def change_mode(self, new_mode):
        self.mode = new_mode
  
    def get_mode(self):
        return self.mode
    
    def swap_mode(self):
        if self.mode == "navigation":
            self.mode = "keyboard"
        elif self.mode == "keyboard":
            self.mode = "drawing"
        else:
            self.mode = "navigation"
        return self.mode
