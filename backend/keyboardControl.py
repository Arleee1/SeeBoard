import pyautogui
import time
class keyboardControl:
    def __init__(self):
        self.cache = list()

    def keyboardInput(self, s: str, interval: float = 0):
        pyautogui.typewrite([s], interval=interval)
        if s == 'backspace':
            self.cache.pop()
        else:
            self.cache.extend(list(s))
        self.cleanCache()

    # Walks backwards through the cache and removes all characters before the first whitespace
    def cleanCache(self):
        for i in range(len(self.cache)-1, -1, -1):
            if self.cache[i] == 'space':
                self.cache = self.cache[i+1:len(self.cache)]
                break

    def clickAt(self, x: float, y: float):
        size = pyautogui.size()
        x = int(x * size[0])
        y = int(y * size[1])
        pyautogui.click(x=x, y=y)


#controller = keyboardControl()
#controller.keyboardInput("testing the input")
#print(controller.cache)
#for key in pyautogui.KEYBOARD_KEYS:
#    print(key)



