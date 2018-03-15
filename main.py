#!/usr/bin/env python

import numpy as np
import cv2
from time import time
from subprocess import call

cam = cv2.VideoCapture(1)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,1920.0)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT,1080.0)

init_time = time()
captured = time()
low_latency = False

i = 1
while True:

    # Capture frame-by-frame
    ret, frame = cam.read()

    # Show the resulting frame
    cv2.imshow('frame', frame)
    cv2.waitKey(1)

    # Calculate fps
    fps = 1/(time() -captured)
    captured = time()
    print fps

    if time()-init_time > 1 and not low_latency:
        low_latency = not low_latency
        call(['mwcap-control', '--video-output-lowlatency', 'on', '0:0'])
        # cam.set(cv2.CAP_PROP_FPS,30.0)


    # Write the resulting frame
    if time()-init_time > 3 and i <= 10:
        print str(i) + ": " + str(captured)
        cv2.imwrite(str(i) + '.png', frame)
        i += 1
    elif i > 10:
        break

# When everything done, release the capture
# cam.release()
# cv2.destroyAllWindows()
