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

w_x,w_h=gui.size()
print(w_x,w_h)

frame_width = w_x
frame_height = w_h
video = cv.VideoCapture(0)
video.set(cv.CAP_PROP_FRAME_WIDTH, frame_width)
video.set(cv.CAP_PROP_FRAME_HEIGHT, frame_height)

cv.namedWindow("AIR CANVAS", cv.WINDOW_NORMAL)
cv.resizeWindow("AIR CANVAS", frame_width, frame_height)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


volMin,volMax=volume.GetVolumeRange()[:2]
hands=handsTracker.HandsTracker()

volume_cords=[(100,500),(130,100)]
bright_cords=[(1100,500),(1130,100)]

Volume_label=(40,550)
bright_label=(1040,550)

colors = {
       'Red': (0, 0, 255),
       'Blue': (255, 0, 0),
       'Green': (0, 255, 0),
       'Yellow': (0, 255, 255),
       'White': (255, 255, 255),
       'Black': (0, 0, 0),
       'purple':(255,0,255)
}
   

def dist(f1x,f1y,f2x,f2y):
    return math.sqrt((f2x-f1x)**2+(f2y-f1y)**2)

def get_volume(dist):
    volume=np.interp(dist,[15,350],[volMin,volMax])
    volbar=np.interp(dist,[15,350],[490,110])
    volper=np.interp(dist,[15,350],[0,100])
    return (volume,volbar,volper)

def get_brightness(dist):
    bright=np.interp(dist,[15,300],[0,100])
    bribar=np.interp(dist,[15,300],[490,110])
    briper=np.interp(dist,[15,300],[0,100])
    return (bright,bribar,briper)

def indexDown(f3y,f1y):
    if f3y< f1_y:
        return False
    return True

while True:
    res,frame=video.read()
    print(frame.shape)

    frame,landmarks=hands.getLandmarks(frame)

    if landmarks:
        f1_x=int(landmarks[0][8].x*frame.shape[1])
        f1_y=int(landmarks[0][8].y*frame.shape[0])
        f2_x=int(landmarks[0][4].x*frame.shape[1])
        f2_y=int(landmarks[0][4].y*frame.shape[0])
        f3_y=int(landmarks[0][12].y*frame.shape[0])

        if indexDown(f3_y,f1_y):

            if f1_x<=500 and f2_x<=500:

                cv.putText(frame,'Brightness',bright_label,cv.FONT_ITALIC,1,colors['Black'],2)
                cv.circle(frame,(f1_x,f1_y),10,colors['Yellow'],-1)
                cv.circle(frame,(f2_x,f2_y),10,colors['Yellow'],-1)
                cv.line(frame,(f1_x,f1_y),(f2_x,f2_y),colors['Red'],5)
                cv.circle(frame,((f1_x+f2_x)//2,(f1_y+f2_y)//2),10,colors['Yellow'],-1)
                distance=dist(f1_x,f1_y,f2_x,f2_y)
                bright,bribar,briper=get_brightness(math.floor(distance))
                print(int(bright))
                sbc.set_brightness(bright, display=0)
                cv.rectangle(frame,bright_cords[0],bright_cords[1],colors['purple'],2)
                cv.rectangle(frame,((bright_cords[0][0]+5),490),((bright_cords[1][0]-5),int(bribar)),colors['White'],-1)
                cv.putText(frame,f'{int(briper)}%',(bright_cords[1][0],bright_cords[1][1]-30),cv.FONT_ITALIC,1,colors['Black'],2)
                print('Brightness')
            elif f1_x>=800 and f2_x>=800:
                cv.putText(frame,'Volume',Volume_label,cv.FONT_ITALIC,1,(255,255,255),1)
                cv.circle(frame,(f1_x,f1_y),10,colors['Yellow'],-1)
                cv.circle(frame,(f2_x,f2_y),10,colors['Yellow'],-1)
                cv.line(frame,(f1_x,f1_y),(f2_x,f2_y),colors['Red'],5)
                cv.circle(frame,((f1_x+f2_x)//2,(f1_y+f2_y)//2),10,colors['Yellow'],-1)
                distance=dist(f1_x,f1_y,f2_x,f2_y)
                vol,volbar,volper=get_volume(math.floor(distance))
                print(int(vol))
                volume.SetMasterVolumeLevel(vol,None)
                cv.rectangle(frame,volume_cords[0],volume_cords[1],colors['purple'],2)
                cv.rectangle(frame,((volume_cords[0][0]+5),490),((volume_cords[1][0]-5),int(volbar)),colors['White'],-1)
                cv.putText(frame,f'{int(volper)}%',(volume_cords[1][0],volume_cords[1][1]-30),cv.FONT_ITALIC,1,colors['Black'],2)
                print('Volume')
            else:
                print('neutral')
    cv.imshow('AIR CANVAS',frame)

    if cv.waitKey(5) & 0xFF == ord('d'):
        break

video.release()
cv.destroyAllWindows() 


