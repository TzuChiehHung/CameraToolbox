#!/usr/bin/env python

from argparse import ArgumentParser
import threading
import Queue
import cv2
import time
import random
import pandas as pd

class CameraInfo():

    def __init__(self):
        columns = ['name', 'ip', 'maker', 'timestamp']
        self.list = pd.DataFrame(columns=columns)

    def add_camera(self, name, ip, maker):
        new_row = {
            'name': name,
            'ip': ip,
            'maker': maker,
            'timestamp': time.time()
        }
        self.list = self.list.append(new_row, ignore_index=True)


class IPCameraStream(threading.Thread):

    def __init__(self, name, ip, maker='xm'):
        super(IPCameraStream,  self).__init__(name=name)
        self.daemon =True

        if maker == 'xm':
            self._url = 'rtsp://{}:554/user=admin&password=&channel=1&stream=0.sdp?'.format(ip)
        elif maker == 'hik':
            self._url = 'rtsp://admin:hk888888@{}:554/Streaming/Channels/001'.format(ip)

        self.cam = cv2.VideoCapture(self._url)
        self.stop = False
        self._new_frame = threading.Event()

    def run(self):
        while not self.stop:
            if self.cam.grab():
                self._new_frame.set()

    def read(self):
        if self._new_frame.is_set():
            ret, frame = self.cam.retrieve()
            self._new_frame.clear()
            return ret, frame
        else:
            return False, None

class RetrieveFrame(threading.Thread):

    def __init__(self, name, lock, cam_info, cam_threads, output_queue=None):
        super(RetrieveFrame,  self).__init__(name=name)
        self.daemon =True
        self.lock = lock
        self.cam_threads = cam_threads
        self.stop = False
        self.cam_info = cam_info
        self.output = output_queue

    def run(self):
        while not self.stop:
            with self.lock:
                idx = self.cam_info.list['timestamp'].idxmin()
                ret, frame = self.cam_threads[idx].read()
                self.cam_info.list.at[idx, 'timestamp'] = time.time()
                if ret:
                    self.output.put((self.cam_info.list['ip'][idx], frame))
                else:
                    pass
        print '{}: stop retrieve'.format(self.name)


def main(args):

    # camera list
    cam_info = CameraInfo()

    # test
    cam_info.add_camera(name='camera_1', ip='192.168.1.101', maker='xm')
    cam_info.add_camera(name='camera_2', ip='192.168.1.102', maker='xm')
    # cam_info.add_camera(name='camera_3', ip='192.168.1.103', maker='xm')
    # cam_info.add_camera(name='camera_4', ip='192.168.1.104', maker='xm')

    # rongzong
    # cam_info.add_camera(name='camera_1', ip='192.168.1.11', maker='xm')
    # cam_info.add_camera(name='camera_2', ip='192.168.1.21', maker='xm')
    # cam_info.add_camera(name='camera_3', ip='192.168.1.22', maker='xm')
    # cam_info.add_camera(name='camera_4', ip='192.168.1.23', maker='xm')
    # cam_info.add_camera(name='camera_5', ip='192.168.1.24', maker='xm')

    print cam_info.list

    # create camera threads
    cam_threads = list()
    for i in cam_info.list.index:
        cam_threads.append(IPCameraStream(
            name=cam_info.list['name'][i],
            ip=cam_info.list['ip'][i],
            maker=cam_info.list['maker'][i]))

    # create output queue
    output_queue = Queue.Queue()

    # create retrieve threads
    num_retrieve_threads = 1
    retrieve_threads = list()
    table_lock = threading.Lock()
    for i in xrange(num_retrieve_threads):
        retrieve_threads.append(RetrieveFrame(
            name='retrieve_{}'.format(i+1),
            lock=table_lock,
            cam_info=cam_info,
            cam_threads=cam_threads,
            output_queue=output_queue))

    # initial camera/retrieve threads
    for cam in cam_threads:
        cam.start()

    for retrieve in retrieve_threads:
        retrieve.start()

    # show image frames and fps
    ip_list = cam_info.list['ip']
    idx = 0
    frame_count = 0
    tic = time.time()
    toc = time.time()

    try:
        while True:
            (ip, frame) = output_queue.get()

            if ip == ip_list[idx]:
                frame = cv2.resize(frame, (0, 0), fx=args.scale, fy=args.scale)
                cv2.putText(frame, ip, (10, frame.shape[0]-10), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)
                cv2.imshow('frame', frame)

                # calculate fps
                if args.fps:
                    if toc-tic < 5:
                        frame_count += 1
                        toc = time.time()
                        print '{}: {:5.2f} fps'.format(ip, frame_count/(toc-tic))
                    else:
                        frame_count = 0
                        tic = time.time()
            else:
                pass

            # hotkeys
            key = cv2.waitKey(1) & 0xFF
            if key ==ord('n'):
                idx += 1
                idx %= len(ip_list)
                print 'Switch to {}:\t{}'.format(cam_info.list['name'][idx], cam_info.list['ip'][idx])
                frame_count = 0
                tic = time.time()
            elif key == ord('q'):
                break

    except KeyboardInterrupt:
        pass

    # stop camera/retrieve threads
    for cam in cam_threads:
        cam.stop = True

    for retrieve in retrieve_threads:
        retrieve.stop = True


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-s', '--scale', type=float, help='output frame scale: [0.25]', default=0.25)
    parser.add_argument('-f', '--fps', action='store_true', help='print FPS')

    args = parser.parse_args()

    main(args)
