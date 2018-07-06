#!/usr/bin/env python

import numpy as np
import cv2
from argparse import ArgumentParser
from time import time, sleep
from subprocess import call
import random

parser = ArgumentParser()
parser.add_argument('-d', '--device', help='device number: /dev/video#', dest='device', default=0)

args = parser.parse_args()


codec = 0x47504A4D # MJPG
#codec = 844715353.0 # YUY2

cam = cv2.VideoCapture(args.device)
cam.set(cv2.cv.CV_CAP_PROP_FOURCC, codec)
cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,1920.0)
cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,1080.0)

init_time = time()
last = time()

while True:

    # Capture frame-by-frame
    ret, frame = cam.read()

    # Calculate fps
    now = time()
    fps = 1/(now -last)
    last = time()
    print '{:.2f}: {} x {} @ {:5.1f}'.format(now, frame.shape[1], frame.shape[0], fps)

    # Show the resulting frame
    cv2.imshow('frame', frame)
    cv2.waitKey(1)

# When everything done, release the capture
cam.release()
cv2.destroyAllWindows()
