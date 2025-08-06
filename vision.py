import cv2
import mediapipe as mp
from cv2 import text
import math

# Setup MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Setup camera
cap = cv2.VideoCapture(0)

wrist2middle = 0

last_state = None
middle_pos = [0,0]


two_index_dist = 0

zoom = 0
strafe_lr = 0
strafe_ud = 0

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
    """
    Calculate the angle (in degrees) between a line and the horizontal axis.

    Parameters:
    dx (float): Horizontal difference (x2 - x1)
    dy (float): Vertical difference (y2 - y1)

    Returns:
    float: Angle in degrees
    """
    angle_radians = math.atan2(dy, dx)  # atan2 handles the quadrant correctly
    angle_degrees = math.degrees(angle_radians)
    return angle_degrees


while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)  # Mirror view
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    h, w, _ = frame.shape

    left_hand = None
    right_hand = None

    tips = [4,8,12,16,20]

    if result.multi_hand_landmarks and result.multi_handedness:
        if len(result.multi_hand_landmarks)==2:

            for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                hand_label = handedness.classification[0].label

                if hand_label=="Left":
                    left_hand = hand_landmarks.landmark
                elif hand_label=="Right":
                    right_hand = hand_landmarks.landmark
                

                if left_hand:
                    #index for up, down, right, thumb for left
                    index_ratio = math.dist((to_screen(left_hand, 0, w, h)), (to_screen(left_hand, 8, w, h))) / math.dist((to_screen(left_hand, 0, w, h)), (to_screen(left_hand, 5, w, h)))

                    thumb_ratio = math.dist((to_screen(left_hand, 0, w, h)), (to_screen(left_hand, 4, w, h))) / math.dist((to_screen(left_hand, 0, w, h)), (to_screen(left_hand, 2, w, h)))

                    if thumb_ratio > 1.5:
                        print("left")
                    elif index_ratio >1:
                        a = angle_with_horizontal(to_screen(left_hand, 5, w, h), to_screen(left_hand, 8, w, h))
                        if a <5 and a > -5:
                            print("right")
                        if a <30 and a > 15:
                            print("up")
                        if a >-40 and a <-20:
                            print("down")

                if right_hand:
                    b = get_angle((to_screen(right_hand, 0, w, h), to_screen(right_hand, 4, w, h)), (to_screen(right_hand, 0, w, h), to_screen(right_hand, 8, w, h)))
                    cv2.putText(frame, f"{b}", (to_screen(right_hand, 4, w, h)), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 2)


                # Draw landmarks and connections (bones)
                mp_draw.draw_landmarks(
                    frame, hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_draw.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=4),
                    mp_draw.DrawingSpec(color=(255,0,0), thickness=2)
                )

                # Optional: Draw custom lines between fingertips if you want
                landmarks = hand_landmarks.landmark

                # label left/right hands
                cv2.putText(frame, hand_label, to_screen(landmarks, 0, w, h), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)

                for i in range(len(landmarks)):
                    x1, y1 = to_screen(landmarks, i, w, h)
                    x2, y2 = to_screen(landmarks, 0, w, h)
                    if i in tips:
                        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                
                    #draw the landmarks index - optional for reference
                    cv2.putText(frame, f"{i}", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)

                


        

            


            '''
            if len(result.multi_hand_landmarks)==1:
                middle_pos = [landmarks[12].x*w*dist, landmarks[12].y*h*dist]


                wrist2middle = ((int(landmarks[12].x*w*dist)-int(landmarks[0].x*w*dist))**2 +  (int(landmarks[12].y*h*dist)-int(landmarks[0].y*h*dist))**2)**0.5

                #print(wrist2middle)
                if wrist2middle > 500:
                    #print(middle_pos[0]-last_middle_pos[0])
                    if (middle_pos[0]-last_middle_pos[0]>400):
                        strafe_lr = 0.1

                        print("moving right")
                    elif (middle_pos[0]-last_middle_pos[0]<-400):

                        print("moving left")
                        strafe_lr = -0.1

                    if (middle_pos[1]-last_middle_pos[1]>100):
                        strafe_ud = -0.1
                        print("moving down")

                    elif (middle_pos[1]-last_middle_pos[1]<-100):
                        strafe_ud = 0.1
                        print("moving up")



            # if 2 hands detected -> zoom
            elif len(result.multi_hand_landmarks)==2:

                index2wrist = ((int(landmarks[8].x*w*dist)-int(landmarks[0].x*w*dist))**2 +  (int(landmarks[8].y*h*dist)-int(landmarks[0].y*h*dist))**2)**0.5
                # only activates if right index is open

                if index2wrist >1000:


                    two_index_dist = int(((int(result.multi_hand_landmarks[0].landmark[8].x * w*dist) - (int(result.multi_hand_landmarks[1].landmark[8].x * w*dist)))**2 +(int(result.multi_hand_landmarks[0].landmark[8].y * h*dist) - (int(result.multi_hand_landmarks[1].landmark[8].y * h*dist)))**2)**0.5)
                    print(two_index_dist-last_two_index_dist)
                    if (two_index_dist-last_two_index_dist) > 2000:
                        print("zooming out")
                        zoom = 0.1
                    elif (two_index_dist-last_two_index_dist) < -2000:
                        print("zooming in")
                        zoom = -0.1
                    else:
                        zoom = 0
                    
                    
                    cv2.line(frame, (int(result.multi_hand_landmarks[0].landmark[8].x * w), int(result.multi_hand_landmarks[0].landmark[8].y * h)),
                            (int(result.multi_hand_landmarks[1].landmark[8].x * w), int(result.multi_hand_landmarks[1].landmark[8].y * h)),
                            (255, 0, 255), 2)
                    
                    cv2.putText(frame, f"{int(((int(result.multi_hand_landmarks[0].landmark[8].x * w) - (int(result.multi_hand_landmarks[1].landmark[8].x * w)))**2 +(int(result.multi_hand_landmarks[0].landmark[8].y * h) - (int(result.multi_hand_landmarks[1].landmark[8].y * h)))**2)**0.5)}",
                            (int(result.multi_hand_landmarks[0].landmark[8].x * w), int(result.multi_hand_landmarks[0].landmark[8].y * h)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
                '''



    cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
