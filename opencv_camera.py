#!/usr/bin/env python3

from argparse import ArgumentParser
from time import time
from threading import Thread
from queue import Queue
import cv2


class OpencvCamera():


    def __init__(self, device_id, frame_queue):
        self.device_id = device_id
        self.cam = cv2.VideoCapture(device_id)
        self.frame_queue = frame_queue
        self.is_running = False
        self._frame_count = 0
        self._last_t = time()
        self._data = {}

    def capture_queue(self):
        self._last_t = time()

        while self.is_running and self.cam.isOpened():
            if self.cam.grab():
                self._frame_count += 1
                if self.frame_queue.qsize() < 1:
                    t = time()
                    _, frame = self.cam.retrieve()
                    self._data['image'] = frame.copy()
                    self._data['fps'] = self._frame_count / (t - self._last_t)
                    self.frame_queue.put(self._data)
                    self._last_t = t
                    self._frame_count = 0

    def run(self):
        self.is_running = True
        self.thread_capture = Thread(target=self.capture_queue)
        self.thread_capture.start()

    def stop(self):
        self.is_running = False
        self.cam.release()


def main(args):

    frame_queue = Queue()
    cam = OpencvCamera(args.device_id, frame_queue)
    cam.run()

    while True:
        data = frame_queue.get()
        frame = cv2.resize(data['image'], (0, 0), fx=args.scale, fy=args.scale)
        cv2.imshow(args.device_id, frame)
        print('{:.2f}: {} x {} @ {:5.1f}'.format(time(), data['image'].shape[1], data['image'].shape[0], data['fps']))
        frame_queue.task_done()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('device_id', help='device_id')
    parser.add_argument('-s', '--scale', type=float, help='output frame scale: [0.25]', default=0.25)

    args = parser.parse_args()

    main(args)
