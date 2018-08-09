#!/usr/bin/env python
import os
import cv2
import numpy as np
from argparse import ArgumentParser
from uuid import uuid4 as uuid
from multi_cam import IPCameraStream

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
CYAN = (255, 255, 0)
YELLOW = (0, 255, 255)


class FisheyeCalibration():

    def __init__(self):
        self.frame_size = None
        self.geometry_done = False
        self.lens_center = None
        self.lens_radius = None
        self.fitted_radius = None
        self.available_radius = None
        self.current = (0, 0)
        self.ref_points = [] # List of points defining lens circles
        self.measure_points = []

    def on_mouse(self, event, x, y, buttons, scale):
        # Mouse callback that gets called for every mouse event (i.e. moving, clicking, etc.)

        if event == cv2.EVENT_MOUSEMOVE:
            self.current = tuple(np.round(np.array([x, y])/args.scale).astype(int))
        if event == cv2.EVENT_LBUTTONDOWN:
            pt = tuple(np.round(np.array([x, y])/args.scale).astype(int))
            print 'Adding reference point #{} with position ({}, {})'.format(len(self.ref_points)+1, pt[0], pt[1])
            self.ref_points.append(pt)
        if event == cv2.EVENT_RBUTTONDOWN:
            if self.geometry_done:
                pt = tuple(np.round(np.array([x, y])/args.scale).astype(int))
                self.measure_points.append(pt)

    def draw_measurement_circle(self, frame):
        if self.geometry_done and self.measure_points:
            for pt in self.measure_points:
                radius = np.round(np.linalg.norm(np.array(self.lens_center) - np.array(pt))).astype(int)
                self._draw_circle(frame, self.lens_center, radius, color=YELLOW, thickness=2)
        return frame

    def draw_available_circle(self, frame):
        if self.geometry_done:
            self._draw_circle(frame, self.lens_center, self.available_radius, color=RED, thickness=2)
            string = 'Available radius: {}'.format(self.available_radius)
            cv2.putText(frame, string, (10, 90), cv2.FONT_HERSHEY_COMPLEX, 1, RED, 1)
        return frame

    def draw_fitted_circle(self, frame):
        if self.geometry_done:
            self._draw_circle(frame, self.lens_center, self.fitted_radius, color=BLUE, thickness=2)
            string = 'Fitted radius: {}'.format(self.fitted_radius)
            cv2.putText(frame, string, (10, 60), cv2.FONT_HERSHEY_COMPLEX, 1, BLUE, 1)
        return frame

    def draw_lens_circle(self, frame):
        if self.geometry_done:
            cv2.line(frame, (self.lens_center[0], 0), (self.lens_center[0], self.frame_size[1]), color=GREEN, thickness=1)
            cv2.line(frame, (0, self.lens_center[1]), (self.frame_size[0], self.lens_center[1]), color=GREEN, thickness=1)
            self._draw_circle(frame, self.lens_center, self.lens_radius, color=GREEN, thickness=1)
            string = 'Lens radius: {}'.format(self.lens_radius)
            cv2.putText(frame, string, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, GREEN, 1)
        return frame

    def delete_last_measure_point(self):
        if self.measure_points:
            self.measure_points.remove(self.measure_points[-1])

    def clear_measure_point(self):
        self.measure_points = []

    def get_ref_points(self, frame):
        if not self.frame_size:
            self.frame_size = frame.shape[:2][::-1]

        for pt in self.ref_points:
            cv2.circle(frame, pt, 4, RED, -1)
        # draw cross
        cv2.line(frame, (0, self.current[1]), (frame.shape[1], self.current[1]), color=CYAN, thickness=1)
        cv2.line(frame, (self.current[0], 0), (self.current[0], frame.shape[0]), color=CYAN, thickness=1)

    def get_lens_geometry(self):
        if len(self.ref_points) == 3:
            # calculate center
            # solve Ax=b (Dx+Ey+F = -x^2-y^2)
            A, b = [], []
            for pt in self.ref_points:
                A.append([pt[0], pt[1], 1])
                b.append(-np.sum(np.array(pt)**2))
            try:
                sol = np.linalg.solve(A, b)
                self.lens_center = tuple(np.round(-sol[:2]/2).astype(int))
            except np.linalg.LinAlgError:
                self.ref_points = []
                print 'Got singular matrix, please re-select reference points.'
                self.geometry_done = False
                return self.geometry_done

            # calculate radius
            radius = []
            for pt in self.ref_points:
                radius.append(np.linalg.norm(np.array(self.lens_center) - np.array(pt)))
            self.lens_radius = int(min(radius))
            self.fitted_radius = min(self.lens_center[1], self.frame_size[1]-self.lens_center[1])
            self.available_radius = self.frame_size[1] - self.lens_radius

            print 'Generate Circle. Clear reference point.'
            print '\nLens center: {}'.format(self.lens_center)
            print 'Lens radius: {}'.format(self.lens_radius)
            print 'Fitted radius: {}'.format(self.fitted_radius)
            print 'Available radius: {}\n'.format(self.available_radius)

            self.geometry_done = True
            self.ref_points = []
        elif self.ref_points:
            self.geometry_done = False

        return self.geometry_done

    def _draw_circle(self, frame, center, radius, color=(0, 255, 0), thickness=1):
        if radius > 0:
            cv2.circle(frame, center, radius, color=color, thickness=thickness)
        else:
            pass


def main(args):

    # camera thread
    cam = IPCameraStream(name='Camera', ip=args.ip, maker=args.maker)
    cam.start()

    cal = FisheyeCalibration()

    try:
        cv2.namedWindow(args.ip)
        cv2.setMouseCallback(args.ip, cal.on_mouse, args.scale)
        while True:
            # Capture frame-by-frame
            ret, ori_frame = cam.read()

            if ret:
                frame = ori_frame.copy()
                cal.get_ref_points(frame)

                 # TODO calibrate

                if cal.get_lens_geometry():
                    frame = cal.draw_lens_circle(frame)
                    frame = cal.draw_fitted_circle(frame)
                    frame = cal.draw_available_circle(frame)
                    frame = cal.draw_measurement_circle(frame)

                frame = cv2.resize(frame, (0, 0), fx=args.scale, fy=args.scale)
                cv2.imshow(args.ip, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('d'):
                cal.delete_last_measure_point()
            elif key == ord('r'):
                cal.clear_measure_point()
            elif key == ord('s'):
                directory = './calibration'
                if not os.path.exists(directory):
                    os.makedirs(directory)
                fn = os.path.join(directory, '{}.png'.format(uuid().hex))
                cv2.imwrite(fn, ori_frame)
    except KeyboardInterrupt:
        print '\nKeyboardInterrupt'
        pass

    cam.stop = True
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('ip', help='camera ip')
    parser.add_argument('-m', '--maker', help='device maker: [xm]/hk', default='xm')
    parser.add_argument('-s', '--scale', type=float, help='output frame scale: [0.25]', default=1.0)

    args = parser.parse_args()

    main(args)
