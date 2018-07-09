#!/usr/bin/env python

import threading
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

    def run(self):
        while not self.stop:
            # print '{}: grab frame'.format(self.name)
            self.cam.grab()

    def read(self):
        return self.cam.retrieve()

class RetrieveFrame(threading.Thread):

    def __init__(self, name, lock, cam_info, cam_threads):
        super(RetrieveFrame,  self).__init__(name=name)
        self.daemon =True
        self.lock = lock
        self.cam_threads = cam_threads
        self.stop = False
        self.cam_info = cam_info

    def run(self):
        while not self.stop:
            with self.lock:
                idx = self.cam_info.list['timestamp'].idxmin()
                print '{}: try {} @ {}'.format(self.name, self.cam_info.list['name'][idx], time.time())
                ret, frame = self.cam_threads[idx].read()
                if ret:
                    self.cam_info.list.at[idx, 'timestamp'] = time.time()
                    print '{}: got {} @ {:.6f}'.format(self.name, self.cam_info.list['name'][idx], self.cam_info.list['timestamp'][idx])
                    for i in self.cam_info.list['timestamp']:
                        print i
                    print
                else:
                    print '{}: got {} nothing @ {:.6f}'.format(self.name, self.cam_info.list['name'][idx], self.cam_info.list['timestamp'][idx])
                    for i in self.cam_info.list['timestamp']:
                        print i
                    print

            # run model
            time.sleep(0.5)
        print '{}: stop retrieve'.format(self.name)


if __name__ == '__main__':

    # camera thread list
    cam_info = CameraInfo()
    cam_info.add_camera(name='camera_1', ip='192.168.1.14', maker='xm')
    cam_info.add_camera(name='camera_2', ip='192.168.1.15', maker='hik')
    print cam_info.list
    
    cam_threads = list()
    for i in cam_info.list.index:
        cam_threads.append(IPCameraStream(
            name=cam_info.list['name'][i],
            ip=cam_info.list['ip'][i],
            maker=cam_info.list['maker'][i]))

    retrieve_threads = list()
    table_lock = threading.Lock()
    for i in xrange(2):
        retrieve_threads.append(RetrieveFrame(name='retrieve_{}'.format(i+1), lock=table_lock, cam_info=cam_info, cam_threads=cam_threads,))

    for cam in cam_threads:
        cam.start()

    for retrieve in retrieve_threads:
        retrieve.start()

    time.sleep(3)

    for cam in cam_threads:
        cam.stop = True

    for retrieve in retrieve_threads:
        retrieve.stop = True