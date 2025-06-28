import cv2
import pyautogui
import webbrowser
import subprocess
import time
import ctypes
from cvzone.HandTrackingModule import HandDetector

# Set always-on-top flag (Windows only)
def set_always_on_top(window_name):
    hwnd = ctypes.windll.user32.FindWindowW(None, window_name)
    if hwnd != 0:
        ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)

# Initialize
detector = HandDetector(maxHands=2, detectionCon=0.7)
cap = cv2.VideoCapture(0)
flip_camera = True

# For gesture hold detection
prev_gesture = None
gesture_start_time = None

def gesture_held(current_gesture):
    global prev_gesture, gesture_start_time
    now = time.time()
    if current_gesture == prev_gesture:
        if now - gesture_start_time >= 1:
            return True
    else:
        prev_gesture = current_gesture
        gesture_start_time = now
    return False

while True:
    success, img = cap.read()
    if not success:
        break

    if flip_camera:
        img = cv2.flip(img, 1)

    hands, img = detector.findHands(img, draw=True)

    gesture = None

    if hands:
        for hand in hands:
            fingers = detector.fingersUp(hand)
            handType = hand["type"]
            if flip_camera:
                handType = "Left" if handType == "Right" else "Right"

            # Detect gestures
            if fingers == [0, 0, 0, 0, 0]: gesture = "Pause/Play Media"
            elif fingers == [0, 1, 0, 0, 0]: gesture = "Move Cursor"
            elif fingers == [0, 1, 1, 0, 0]: gesture = "Take Screenshot"
            elif fingers == [1, 1, 1, 1, 1]: gesture = "Increase Volume"
            elif fingers == [1, 0, 0, 0, 0]: gesture = "Open Browser"
            elif fingers == [0, 0, 0, 0, 1]: gesture = "Show Desktop"
            elif fingers == [1, 0, 0, 0, 1]: gesture = "Switch Tabs"
            elif fingers == [1, 1, 1, 0, 0]: gesture = "Lock Screen (Play animation.mp4)"
            elif fingers == [0, 1, 1, 1, 1]: gesture = "Open WhatsApp"
            elif fingers == [0, 1, 0, 0, 1]: gesture = "Quit Program"
            else: gesture = "🤷 Unknown Gesture"

            if gesture_held(gesture):
                if gesture == "Pause/Play Media":
                    pyautogui.press("space")

                elif gesture == "Move Cursor":
                    pyautogui.moveTo(500, 500, duration=0.2)

                elif gesture == "Take Screenshot":
                    pyautogui.screenshot("screenshot.png")

                elif gesture == "Increase Volume":
                    pyautogui.press("volumeup")

                elif gesture == "Open Browser":
                    webbrowser.open("https://www.google.com")

                elif gesture == "Show Desktop":
                    pyautogui.hotkey("win", "d")

                elif gesture == "Switch Tabs":
                    pyautogui.hotkey("ctrl", "tab")

                elif gesture == "Volume Down":
                    pyautogui.press("volumedown")

                elif gesture == "Open WhatsApp":
                    webbrowser.open("https://web.whatsapp.com/")
                    
                elif gesture == "Quit Program":
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

                # Prevent multiple triggers after execution
                gesture_start_time = time.time() + 9999  # reset timer artificially

            # Show gesture label
            cv2.putText(img, f"{gesture}", (hand["bbox"][0], hand["bbox"][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display
    win_name = "Hand Gesture Recognition"
    cv2.imshow(win_name, img)
    set_always_on_top(win_name)  # keep window on top

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
