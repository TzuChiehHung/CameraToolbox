#!/usr/bin/env python

import cv2
from argparse import ArgumentParser
from time import time, sleep

def main(args):

    if args.maker == 'xm':
        url = 'rtsp://{}:554/user=admin&password=&channel=1&stream=0.sdp?'.format(args.ip)
    elif args.maker == 'hik':
        url = 'rtsp://admin:hk888888@{}:554/Streaming/Channels/001'.format(args.ip)
    else:
        print 'please select correct device maker:'
        print '\t xm:\t XiongMai Tech'
        print '\t hik:\t HIKvision'
        return

    cam = cv2.VideoCapture(url)

    frame_count = 0
    init_time = time()
    
    while True:

        # Capture frame-by-frame
        if cam.grab():
            _, frame = cam.retrieve()
            grab_time = time()
            frame_count += 1
        else:
            continue

        # Calculate fps
        if grab_time - init_time > 10:
            fps = frame_count / (grab_time - init_time)
            print '{:.2f}: {} x {} @ {:5.1f}'.format(time(), frame.shape[1], frame.shape[0], fps)
        
        # Show the resulting frame
        if args.visual:
            frame = cv2.resize(frame, (0, 0), fx=1./4, fy=1./4)
            cv2.imshow(args.device, frame)

            if cv2.waitKey(1) == ord('q'):
                break

    # When everything done, release the capture
    cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('ip', help='camera ip')
    parser.add_argument('-m', '--maker', help='maker: [xm]/hk', dest='maker', default='xm')
    parser.add_argument('-v', '--VISUAL', action='store_true', dest='visual', help='Show image frame')
    args = parser.parse_args()

    main(args)
