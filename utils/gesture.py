class Gesture:
    def __init__(self, hand, exists, is_pinch, angle, position):
        self.hand = hand
        self.exists = exists
        self.is_pinch = is_pinch
        self.angle = angle
        self.position = position

    def check_pinch(self):
        if self.exists:
            return self.is_pinch
    
    def get_angle(self):
        if self.exists:
            return self.angle

    def get_position(self):
        if self.exists:
            return self.position
