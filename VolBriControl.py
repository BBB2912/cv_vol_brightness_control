import cv2 as cv
import mediapipe
import handsTracker
import pyautogui as gui
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import math
import numpy as np

class VolBriController:
    def __init__(self):
        # Initialize GUI and video capture
        self.w_x, self.w_h = gui.size()
        self.frame_width = self.w_x
        self.frame_height = self.w_h
        self.video = cv.VideoCapture(0)
        self.video.set(cv.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.video.set(cv.CAP_PROP_FRAME_HEIGHT, self.frame_height)

        cv.namedWindow("Volume & Brightness Control", cv.WINDOW_NORMAL)
        cv.resizeWindow("Volume & Brightness Control", self.frame_width, self.frame_height)

        # Initialize audio controls
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.volMin, self.volMax = self.volume.GetVolumeRange()[:2]

        # Initialize hands tracker
        self.hands = handsTracker.HandsTracker()

        # Define coordinates and colors
        self.volume_cords = [(100, 500), (130, 100)]
        self.bright_cords = [(1100, 500), (1130, 100)]
        self.Volume_label = (40, 550)
        self.bright_label = (1040, 550)
        self.colors = {
            'Red': (0, 0, 255),
            'Blue': (255, 0, 0),
            'Green': (0, 255, 0),
            'Yellow': (0, 255, 255),
            'White': (255, 255, 255),
            'Black': (0, 0, 0),
            'Purple': (255, 0, 255)
        }

    def dist(self, f1x, f1y, f2x, f2y):
        return math.sqrt((f2x - f1x) ** 2 + (f2y - f1y) ** 2)

    def get_volume(self, dist):
        volume = np.interp(dist, [15, 350], [self.volMin, self.volMax])
        volbar = np.interp(dist, [15, 350], [490, 110])
        volper = np.interp(dist, [15, 350], [0, 100])
        return volume, volbar, volper

    def get_brightness(self, dist):
        bright = np.interp(dist, [15, 300], [0, 100])
        bribar = np.interp(dist, [15, 300], [490, 110])
        briper = np.interp(dist, [15, 300], [0, 100])
        return bright, bribar, briper

    def index_down(self, f3y, f1y):
        return f3y >= f1y

    def process_frame(self, frame):
        frame, landmarks = self.hands.getLandmarks(frame)

        if landmarks:
            f1_x = int(landmarks[0][8].x * frame.shape[1])
            f1_y = int(landmarks[0][8].y * frame.shape[0])
            f2_x = int(landmarks[0][4].x * frame.shape[1])
            f2_y = int(landmarks[0][4].y * frame.shape[0])
            f3_y = int(landmarks[0][12].y * frame.shape[0])

            if self.index_down(f3_y, f1_y):
                if f1_x <= 500 and f2_x <= 500:
                    self.handle_brightness(frame, f1_x, f1_y, f2_x, f2_y)
                elif f1_x >= 800 and f2_x >= 800:
                    self.handle_volume(frame, f1_x, f1_y, f2_x, f2_y)
                else:
                    print('neutral')
        return frame

    def handle_brightness(self, frame, f1_x, f1_y, f2_x, f2_y):
        cv.putText(frame, 'Brightness', self.bright_label, cv.FONT_ITALIC, 1, self.colors['Black'], 2)
        cv.circle(frame, (f1_x, f1_y), 10, self.colors['Yellow'], -1)
        cv.circle(frame, (f2_x, f2_y), 10, self.colors['Yellow'], -1)
        cv.line(frame, (f1_x, f1_y), (f2_x, f2_y), self.colors['Red'], 5)
        cv.circle(frame, ((f1_x + f2_x) // 2, (f1_y + f2_y) // 2), 10, self.colors['Yellow'], -1)
        distance = self.dist(f1_x, f1_y, f2_x, f2_y)
        bright, bribar, briper = self.get_brightness(math.floor(distance))
        print(int(bright))
        sbc.set_brightness(bright, display=0)
        cv.rectangle(frame, self.bright_cords[0], self.bright_cords[1], self.colors['Purple'], 2)
        cv.rectangle(frame, ((self.bright_cords[0][0] + 5), 490), ((self.bright_cords[1][0] - 5), int(bribar)), self.colors['White'], -1)
        cv.putText(frame, f'{int(briper)}%', (self.bright_cords[1][0], self.bright_cords[1][1] - 30), cv.FONT_ITALIC, 1, self.colors['Black'], 2)
        print('Brightness')

    def handle_volume(self, frame, f1_x, f1_y, f2_x, f2_y):
        cv.putText(frame, 'Volume', self.Volume_label, cv.FONT_ITALIC, 1, (255, 255, 255), 1)
        cv.circle(frame, (f1_x, f1_y), 10, self.colors['Yellow'], -1)
        cv.circle(frame, (f2_x, f2_y), 10, self.colors['Yellow'], -1)
        cv.line(frame, (f1_x, f1_y), (f2_x, f2_y), self.colors['Red'], 5)
        cv.circle(frame, ((f1_x + f2_x) // 2, (f1_y + f2_y) // 2), 10, self.colors['Yellow'], -1)
        distance = self.dist(f1_x, f1_y, f2_x, f2_y)
        vol, volbar, volper = self.get_volume(math.floor(distance))
        print(int(vol))
        self.volume.SetMasterVolumeLevel(vol, None)
        cv.rectangle(frame, self.volume_cords[0], self.volume_cords[1], self.colors['Purple'], 2)
        cv.rectangle(frame, ((self.volume_cords[0][0] + 5), 490), ((self.volume_cords[1][0] - 5), int(volbar)), self.colors['White'], -1)
        cv.putText(frame, f'{int(volper)}%', (self.volume_cords[1][0], self.volume_cords[1][1] - 30), cv.FONT_ITALIC, 1, self.colors['Black'], 2)
        print('Volume')

    def run(self):
        while True:
            res, frame = self.video.read()
            if not res:
                break

            frame = self.process_frame(frame)
            cv.imshow('Volume & Brightness Control', frame)

            if cv.waitKey(5) & 0xFF == ord('d'):
                break

        self.video.release()
        cv.destroyAllWindows()

if __name__ == "__main__":
    app = VolBriController()
    app.run()
