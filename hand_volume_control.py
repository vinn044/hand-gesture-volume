import cv2
import math
import numpy as np
from cvzone.HandTrackingModule import HandDetector

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# Setup system volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volumeControl = cast(interface, POINTER(IAudioEndpointVolume))

# Get system volume range (in dB)
volRange = volumeControl.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

# Webcam setup
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)  # draw=True by default

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]  # List of 21 landmarks

        # Thumb tip and Index tip
        thumb = lmList[4]
        index = lmList[8]

        x1, y1 = thumb[:2]
        x2, y2 = index[:2]

        # Draw circles and line
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 255, 0), 3)

        # Distance between fingers
        length = math.hypot(x2 - x1, y2 - y1)

        # Convert distance to volume level
        vol = np.interp(length, [30, 200], [minVol, maxVol])
        volumeControl.SetMasterVolumeLevel(vol, None)

        # Convert distance to visual volume % and bar
        volBar = np.interp(length, [30, 200], [400, 150])
        volPer = int(np.interp(length, [30, 200], [0, 100]))

        # Draw volume bar and percentage
        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{volPer} %', (40, 430), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show webcam feed
    cv2.imshow("Image", img)
    cv2.waitKey(1)
