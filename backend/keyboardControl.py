import keyboard
import openai


class keyboardControl:
    def __init__(self):
        self.cache = list()
        # with open("../apikey.txt", "r") as f:
        #     openai.api_key = f.read()
        self.messages = list()
        self.messages.append({"role": "system", "content": "You're an autocompleter. All future messages will provide "
                                                           "an input string. Output 5 possible words that the user "
                                                           "might be trying to type if the last word is incomplete"
                                                           "as comma separated values, and order them by relevance. "
                                                           "If the last word is complete, attempt to predict the next "
                                                           "word."})

    def keyboardInput(self, s: str):
        if s == 'Backspace':
            keyboard.send('backspace')
            if (len(self.cache) > 0):
                self.cache.pop()
        elif s == 'Shift':
            pass
        elif s == 'Space':
            keyboard.send('space')
            s = ' '
        elif s == 'Enter':
            keyboard.send('enter')
            s = ' '
        elif s == 'Tab':
            keyboard.send('tab')
            s = ' '
        elif s == 'Caps Lock':
            pass
        elif s == 'Ctrl':
            pass
        elif s == 'Win':
            keyboard.send('win')
            s = ' '
        else:
            keyboard.write(s)
            self.cache.extend(list(s))

    # def keyboardInputString(self, s: str, interval: float = 0):
    #     pyautogui.typewrite(s, interval=interval)
    #     self.cache.extend(list(s))

    # Walks backwards through the cache and removes all characters before the first whitespace
    def clearCache(self):
        self.cache = list()

    def autocomplete(self):
        message = "".join(self.cache)
        self.messages.append({"role": "user", "content": message})
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages
        )
        reply = chat.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})
        candidates = [x.strip() for x in reply.split(",")]
        return candidates


# controller = keyboardControl()
# controller.keyboardInput("I absolutely love talking about Python")
# controller.keyboardInput('backspace')
# controller.autocomplete()
