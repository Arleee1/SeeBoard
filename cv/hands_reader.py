import math

import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
from queue import Queue
import constants


class ExponentialMovingAverage:
    def __init__(self, alpha=0.02):
        self.alpha = alpha
        self.ema = None  # Will be initialized with the first data point

    def apply(self, raw_data):
        if self.ema is None:
            self.ema = raw_data  # Initialize the EMA with the first value
        else:
            self.ema = self.alpha * raw_data + (1 - self.alpha) * self.ema
        return self.ema


left_x_dampener = ExponentialMovingAverage()
left_y_dampener = ExponentialMovingAverage()
right_x_dampener = ExponentialMovingAverage()
right_y_dampener = ExponentialMovingAverage()


class HandDetector:
    def __init__(self, mode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img):
        # imgRGB = img
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img)

        left_hand = {
            "exists": False,
            "is_open": False,
            "x": -1,
            "y": -1,
            "dampened_x": -1,
            "dampened_y": -1,
            "angle": -1
        }
        right_hand = {
            "exists": False,
            "is_open": False,
            "x": -1,
            "y": -1,
            "dampened_x": -1,
            "dampened_y": -1,
            "angle": -1
        }
        if self.results.multi_hand_landmarks:
            for i, handlms in enumerate(self.results.multi_hand_landmarks):
                if constants.draw_hands:
                    self.mpDraw.draw_landmarks(img, handlms, self.mpHands.HAND_CONNECTIONS)


                curr_dict = MessageToDict(self.results.multi_handedness[i])
                curr_side = curr_dict['classification'][0]["label"]
                hand_dict = MessageToDict(handlms)
                landmark_list = hand_dict["landmark"]

                img_width = len(img[0])
                img_height = len(img)
                other_inds = [0]
                avg_x = 0
                avg_y = 0
                for other in other_inds:
                    curr_finger_coords = landmark_list[other]
                    if constants.draw_hands:
                        img = cv2.circle(img, (
                            int(img_width * curr_finger_coords["x"]), int(img_height * curr_finger_coords["y"])), 20,
                                         (255, 0, 0), -1)
                    avg_x += curr_finger_coords["x"]
                    avg_y += curr_finger_coords["y"]

                avg_x /= 3
                avg_y /= 3

                if constants.draw_hands:
                    img = cv2.circle(img, (
                        int(img_width * avg_x), int(img_height * avg_y)), 20,
                                     (255, 0, 0), -1)

                    finger_tip_indices = [4, 8, 12, 16, 20]
                    for finger_tip_index in finger_tip_indices:
                        curr_finger_coords = landmark_list[finger_tip_index]
                        img = cv2.circle(img, (int(img_width * curr_finger_coords["x"]), int(img_height * curr_finger_coords["y"])), 20, (255, 255, 255), -1)

                    before_finger_tip_indices = [3, 7, 11, 15, 19]
                    for finger_tip_index in before_finger_tip_indices:
                        curr_finger_coords = landmark_list[finger_tip_index]
                        img = cv2.circle(img, (
                        int(img_width * curr_finger_coords["x"]), int(img_height * curr_finger_coords["y"])), 20,
                                         (0, 0, 0), -1)


                top_knuckle_coords = landmark_list[6]
                bot_knuckle_coords = landmark_list[2]

                diff_x = top_knuckle_coords["x"] - bot_knuckle_coords["x"]
                diff_y = (1 - top_knuckle_coords["y"]) - (1 - bot_knuckle_coords["y"])

                angle = math.degrees(math.atan2(diff_y, diff_x))

                thumb = landmark_list[4]
                middle = landmark_list[12]
                palm = landmark_list[0]


                dist = math.sqrt((thumb["x"] - middle["x"])**2 + (thumb["y"] - middle["y"])**2)

                curr_open = True
                if dist < 0.15:
                    curr_open = False

                if curr_side == "Left":
                    dampened_x = left_x_dampener.apply(palm["x"])
                    dampened_y = left_y_dampener.apply(palm["y"])
                    left_hand = {
                        "exists": True,
                        "is_open": curr_open,
                        "x": palm["x"],
                        "y": palm["y"],
                        "dampened_x": dampened_x,
                        "dampened_y": dampened_y,
                        "angle": angle
                    }
                else:
                    dampened_x = right_x_dampener.apply(palm["x"])
                    dampened_y = right_y_dampener.apply(palm["y"])
                    right_hand = {
                        "exists": True,
                        "is_open": curr_open,
                        "x": palm["x"],
                        "y": palm["y"],
                        "dampened_x": dampened_x,
                        "dampened_y": dampened_y,
                        "angle": angle
                    }

                if constants.draw_hands:
                    img = cv2.circle(img, (
                        int(img_width * dampened_x), int(img_height * dampened_y)), 20,
                                     (0, 0, 0), -1)

        if constants.print_hands:
            print("left")
            print(left_hand)
            print("right")
            print(right_hand)

        return img, left_hand, right_hand


def read_hands(hands_queue: Queue):
    detector = HandDetector()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, constants.FRAME_RATE)

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img_res, left_hand, right_hand = detector.findHands(img)

        hands_queue.put((left_hand, right_hand))

        if constants.draw_hands:
            cv2.imshow('Image', img_res)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
