import cv2
import mediapipe as mp
import threading
import math

def get_angle(line1, line2):
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2

    # Calculate direction vectors
    v1 = (x2 - x1, y2 - y1)
    v2 = (x4 - x3, y4 - y3)

    angle1 = math.atan2(v1[1], v1[0])
    angle2 = math.atan2(v2[1], v2[0])

    # Calculate signed angle difference in degrees
    angle_degrees = math.degrees(angle2 - angle1)
    angle_degrees%=180
    if angle_degrees<0: angle_degrees +=360
    if angle_degrees > 360: angle_degrees=360-angle_degrees
    return angle_degrees


def to_screen(l, i, w,h):
    return int(l[i].x*w), int(l[i].y*h)


def angle_with_horizontal(line1, line2):
    (x1, y1) = line1
    (x2, y2) = line2
    dx = x1=x2
    dy = y1-y2

    angle_radians = math.atan2(dy, dx)  # atan2 handles the quadrant correctly
    angle_degrees = math.degrees(angle_radians)
    return angle_degrees


class HandTracker:
    def __init__(self):
        self.state = {
            'zoom': 0.0,
            'strafe_lr': 0.0,
            'strafe_ud': 0.0,
        }
        self._stop = False
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop = True
        self.thread.join()

    def _run(self):


        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
        mp_draw = mp.solutions.drawing_utils
        cap = cv2.VideoCapture(0)

        w, h = 800,600 

        while not self._stop:
            success, frame = cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            h, w, _ = frame.shape
            left_hand = None
            right_hand = None

            if result.multi_hand_landmarks and result.multi_handedness:
                if len(result.multi_hand_landmarks)==2:

                    for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                        hand_label = handedness.classification[0].label

                        if hand_label=="Left":
                            left_hand = hand_landmarks.landmark
                        elif hand_label=="Right":
                            right_hand = hand_landmarks.landmark
                        
                        if left_hand:

                            index_ratio = math.dist((to_screen(left_hand, 0, w, h)), (to_screen(left_hand, 8, w, h))) / math.dist((to_screen(left_hand, 0, w, h)), (to_screen(left_hand, 5, w, h)))

                            thumb_ratio = math.dist((to_screen(left_hand, 0, w, h)), (to_screen(left_hand, 4, w, h))) / math.dist((to_screen(left_hand, 0, w, h)), (to_screen(left_hand, 2, w, h)))
                            
                            if thumb_ratio > 1.5:
                                thumb_angle = angle_with_horizontal(to_screen(left_hand, 2, w, h), to_screen(left_hand, 4, w, h))
                                print(thumb_angle)
                                if thumb_angle >-3 and thumb_angle < 3:
                                    self.state['strafe_lr'] = 0.01
                                elif thumb_angle >15 and thumb_angle < 23:
                                    self.state['strafe_ud'] = 0.01
                                elif thumb_angle >30 and thumb_angle < 65:
                                    self.state['strafe_lr'] = -0.01
                            elif index_ratio >1:
                                a = angle_with_horizontal(to_screen(left_hand, 5, w, h), to_screen(left_hand, 8, w, h))
                                #print(a)
                                if a <15 and a > -15:
                                    self.state['starfe_lr'] = 0.01
                                if a <50 and a > 15:
                                     self.state['strafe_ud'] = 0.01
                                if a >-40 and a <-20:
                                     self.state['strafe_ud'] = -0.01
                            else:
                                self.state = {
                                    'zoom': 0.0,
                                    'strafe_lr': 0.0,
                                    'strafe_ud': 0.0,
                                }

                        if right_hand:
                            b = get_angle((to_screen(right_hand, 0, w, h), to_screen(right_hand, 4, w, h)), (to_screen(right_hand, 0, w, h), to_screen(right_hand, 8, w, h)))
                            #print(b)
                            self.state['zoom'] = (round(b/5) * 5) /4 # round to nearest multiple of 5 then divide by factor



            if cv2.waitKey(1) == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
