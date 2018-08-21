#!/usr/bin/env python

from argparse import ArgumentParser
from time import time
import cv2

def main(args):

    if args.maker == 'xm':
        url = 'rtsp://{}:554/user=admin&password=&channel={}&stream={}.sdp?'.format(args.ip, args.channel, args.stream)
    elif args.maker == 'hik':
        url = 'rtsp://admin:hk888888@{}:554/Streaming/Channels/001'.format(args.ip)
    elif args.maker == 'and':
        url = 'rtsp://{}:8080/video/h264'.format(args.ip)
    else:
        print 'please select correct device maker:'
        print '\t xm:\t XiongMai Tech'
        print '\t hik:\t HIKvision'
        print '\t and:\t Android Device'
        return

    cam = cv2.VideoCapture(url)

    frame_count = 0
    init_time = time()
    tic = time()

    try:
        while True:
            # Capture frame-by-frame
            if cam.grab():
                _, frame = cam.retrieve()
                toc = time()
                frame_count += 1
            else:
                continue

            # Calculate fps
            if toc - init_time > 3:
                fps = frame_count / (toc - tic)
                print '{:.2f}: {} x {} @ {:5.1f}'.format(time(), frame.shape[1], frame.shape[0], fps)

                if toc -tic > 3:
                    tic = time()
                    frame_count = 0

            # Show the resulting frame
            if args.visual:
                # if args.stream == 1:
                #     frame = cv2.resize(frame, (int(16*frame.shape[0]/9.), frame.shape[0]))
                frame = cv2.resize(frame, (0, 0), fx=args.scale, fy=args.scale)
                cv2.imshow(args.ip, frame)

                if cv2.waitKey(1) == ord('q'):
                    break
    except KeyboardInterrupt:
        print '\nKeyboardInterrupt'
        pass

    # When everything done, release the capture
    cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('ip', help='camera ip')
    parser.add_argument('-m', '--maker', help='device maker: [xm]/hk/and', default='xm')
    parser.add_argument('-v', '--visual', action='store_true', help='show image frame')
    parser.add_argument('-s', '--scale', type=float, help='output frame scale: [0.25]', default=0.25)
    parser.add_argument('--channel', type=int, help='rtsp channel', default=1)
    parser.add_argument('--stream', type=int, help='rtps stream', default=0)

    args = parser.parse_args()

    main(args)
