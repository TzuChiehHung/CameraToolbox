#!/usr/bin/env python

from argparse import ArgumentParser
import os
import cv2
import time

def list_files(directory, ext):
    return (f for f in os.listdir(directory) if f.endswith('.{}'.format(ext)))

def main(args):

    # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    fourcc = cv2.VideoWriter_fourcc(*args.fourcc)
    
    list_img = list_files(args.directory, args.input_ext)

    for fn in sorted(map(lambda x: int(x.split('.')[0]), list_img)):
        img = cv2.imread(os.path.join(args.directory, '{}.{}'.format(fn, args.input_ext)))
        if 'video' not in locals():
            height, width, _ = img.shape
            video = cv2.VideoWriter(args.output, fourcc, args.fps, (width, height))
        video.write(img)

    cv2.destroyAllWindows()
    video.release()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-i', '--directory', type=str, help='image directroy [cwd]', default=os.getcwd())
    parser.add_argument('-e', '--input_ext', type=str, help='image format [png]', default='png')
    parser.add_argument('-o', '--output', type=str , help='output video [output.avi]', default='output.avi')
    parser.add_argument('-f', '--fps', type=int , help='output fps', default=25)
    parser.add_argument('-F', '--fourcc', type=str , help='fourcc [XVID]/MJPG', default='XVID')

    args = parser.parse_args()
    main(args)
