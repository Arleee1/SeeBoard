import pyautogui
import openai


class keyboardControl:
    def __init__(self):
        self.cache = list()
        with open("../apikey.txt", "r") as f:
            openai.api_key = f.read()
        self.messages = list()
        self.messages.append({"role": "system", "content": "You're an autocompleter. All future messages will provide "
                                                           "an input string. Output 5 possible words that the user "
                                                           "might be trying to type if the last word is incomplete"
                                                           "as comma separated values, and order them by relevance. "
                                                           "If the last word is complete, attempt to predict the next "
                                                           "word."})

    def keyboardInput(self, s: str, interval: float = 0):
        pyautogui.typewrite([s], interval=interval)
        if s == 'backspace':
            self.cache.pop()
        else:
            self.cache.extend(list(s))

    def keyboardInputString(self, s: str, interval: float = 0):
        pyautogui.typewrite(s, interval=interval)
        self.cache.extend(list(s))

    # Walks backwards through the cache and removes all characters before the first whitespace
    def cleanCache(self):
        for i in range(len(self.cache) - 1, -1, -1):
            if self.cache[i] == 'space':
                self.cache = self.cache[i + 1:len(self.cache)]
                break

    def clickAt(self, x: float, y: float):
        size = pyautogui.size()
        x = int(x * size[0])
        y = int(y * size[1])
        pyautogui.click(x=x, y=y)

    def autocomplete(self):
        message = "".join(self.cache)
        print(f"Message: {message}")
        self.messages.append({"role": "user", "content": message})
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages
        )
        reply = chat.choices[0].message.content
        print(f"GPT: {reply}")
        self.messages.append({"role": "assistant", "content": reply})
        candidates = [x.strip() for x in reply.split(",")]
        print(candidates)


controller = keyboardControl()
controller.keyboardInputString("I absolutely love talking about Python")
controller.autocomplete()
