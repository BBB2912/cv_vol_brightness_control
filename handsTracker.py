import cv2 as cv
import mediapipe as mp


class HandsTracker:
    def __init__(self) -> None:
        self.mp_hands=mp.solutions.hands
        self.hands=self.mp_hands.Hands(static_image_mode=True,max_num_hands=1)
        self.mp_draw=mp.solutions.drawing_utils
        self.mp_draw_styles=mp.solutions.drawing_styles

    def getLandmarks(self,frame):
        landmarks=[]

        frame=cv.flip(frame,1)

        main_frame=frame.copy()
        main_frame=cv.cvtColor(main_frame,cv.COLOR_BGR2RGB)
        results=self.hands.process(main_frame)
        main_frame=cv.cvtColor(main_frame,cv.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(main_frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS, self.mp_draw_styles.get_default_hand_landmarks_style())
                landmarks.append(hand_landmarks.landmark)

        return main_frame,landmarks

if __name__=='__main__':

    cap=cv.VideoCapture(0)
    f1_x,f2_x=None,None
    handstracker=HandsTracker()
    while True:
        res,frame=cap.read()
        print(frame.shape)

        frame,landmarks=handstracker.getLandmarks(frame)
        if landmarks:
            # print(landmarks)
            f1_x=landmarks[0][4].x*frame.shape[1]
            f2_x=landmarks[0][20].x*frame.shape[1]
            if f1_x <= f2_x:
                print('Right')
            else:
                print('Left')
        else:
            print('no hands detected')

        cv.imshow('hands',frame)

        if cv.waitKey(5) & 0xFF==ord('d'):
                break
    cap.release()
    cv.destroyAllWindows()