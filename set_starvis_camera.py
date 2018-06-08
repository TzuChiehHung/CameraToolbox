#!/usr/bin/env python
'''
sudo apt-get install v4l-utils
'''
import cv2
import os
import sys
import subprocess
import time
import re
import string

class CameraAdjustParameter:

    def __init__(self):
        self.run_path = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0] + "/"
        self.camera_parameters = ['brightness', 'contrast', 'saturation', 'hue', 'gamma', 'gain', 'white_balance_temperature_auto', 'white_balance_temperature', 'sharpness', 'backlight_compensation', 'exposure_auto', 'exposure_absolute']
        self.default_value = ['64', '32', '56', '40', '100', '0', '0 = off, 1 = on', 'min = 2800, default = 4600', '3', '1', '0 = off, 1 = on', '156']
        self.brightness = 64  # -64~64
        self.contrast = 32
        self.saturation = 56
        self.hue = 40         # -40~40
        self.gamma = 100
        self.gain = 0
        self.white_balance_temperature_auto = 1
        self.white_balance_temperature = 4600
        self.sharpness = 3
        self.backlight_compensation = 1
        self.exposure_auto = 1
        self.exposure_absolute = 156

        self.pre_brightness = 64
        self.pre_contrast = 32
        self.pre_saturation = 56
        self.pre_hue = 40
        self.pre_gamma = 100
        self.pre_gain = 0
        self.pre_white_balance_temperature_auto = 1
        self.pre_white_balance_temperature = 4600
        self.pre_sharpness = 3
        self.pre_backlight_compensation = 1
        self.pre_exposure_auto = 1
        self.pre_exposure_absolute = 156

        self.camera_parameters_folder = "camera_parameters"

    def get_opencv_version(self):
        version = cv2.__version__

        return version

    def check_necessary_install_package(self):
        cmd = "which v4l2-ctl"
        result = os.system(cmd)
        if result != 0:
            print "Not found install v4l-utils"
            print "Please install v4l-utils : sudo apt-get install v4l-utils"
            sys.exit()

    def get_camera_now_parameter(self, camera_number):
        camera_parameter_values = []
        for para in self.camera_parameters:
            cmd = "v4l2-ctl -d /dev/video%s --get-ctrl %s" % (str(camera_number), para)
            proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            camera_parameter_values.append(out[:-1])

        return camera_parameter_values

    def set_init_controlbar_parameter_value(self, camera_parameter_values):
        index = 0
        for data in camera_parameter_values:
            bar_name = str(data[:data.find(":")]).replace("_", " ")
            bar_value = int(str(data[data.find(":")+1:]))
            print bar_name, bar_value

            if str(data[:data.find(":")]) == self.camera_parameters[0]:
                bar_value = 64 + bar_value
            if str(data[:data.find(":")]) == self.camera_parameters[3]:
                bar_value = 40 + bar_value
            if str(data[:data.find(":")]) == self.camera_parameters[10]:
                if bar_value == 3:
                    bar_value = 1
                else:
                    bar_value = 0
            cv2.setTrackbarPos(string.capwords(bar_name) + '\n' + self.default_value[index], 'Control', bar_value)
            index += 1

    def get_controller_parameter(self):
        self.brightness = cv2.getTrackbarPos('Brightness\n' + self.default_value[0], 'Control')
        self.contrast = cv2.getTrackbarPos('Contrast\n' + self.default_value[1], 'Control')
        self.saturation = cv2.getTrackbarPos('Saturation\n' + self.default_value[2], 'Control')
        self.hue = cv2.getTrackbarPos('Hue\n' + self.default_value[3], 'Control')
        self.gamma = cv2.getTrackbarPos('Gamma\n' + self.default_value[4], 'Control')
        self.gain = cv2.getTrackbarPos('Gain\n' + self.default_value[5], 'Control')
        self.white_balance_temperature_auto = cv2.getTrackbarPos('White Balance Temperature Auto\n' + self.default_value[6], 'Control')
        self.white_balance_temperature = cv2.getTrackbarPos('White Balance Temperature\n' + self.default_value[7], 'Control')
        self.sharpness = cv2.getTrackbarPos('Sharpness\n' + self.default_value[8], 'Control')
        self.backlight_compensation = cv2.getTrackbarPos('Backlight Compensation\n' + self.default_value[9], 'Control')
        self.exposure_auto = cv2.getTrackbarPos('Exposure Auto\n' + self.default_value[10], 'Control')
        self.exposure_absolute = cv2.getTrackbarPos('Exposure Absolute\n' + self.default_value[11], 'Control')

    def set_camera_parameter(self, camera_number):
        if (self.brightness != self.pre_brightness):
            real_brightness = self.brightness - 64
            result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl brightness=%s" % (str(camera_number), str(real_brightness)))
            if result == 0:
                print "Brightness = %s" % str(self.brightness)
                self.pre_brightness = self.brightness
        elif(self.contrast != self.pre_contrast):
            result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl contrast=%s" % (str(camera_number), str(self.contrast)))
            if result == 0:
                print "Contrast = %s" % str(self.contrast)
                self.pre_contrast = self.contrast
        elif(self.saturation != self.pre_saturation):
            result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl saturation=%s" % (str(camera_number), str(self.saturation)))
            if result == 0:
                print "Saturation = %s" % str(self.saturation)
                self.pre_saturation = self.saturation
        elif(self.hue != self.pre_hue):
            real_hue = self.hue - 40
            result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl hue=%s" % (str(camera_number), str(real_hue)))
            if result == 0:
                print "Hue = %s" % str(self.hue)
                self.pre_hue = self.hue
        elif(self.gamma != self.pre_gamma):
            result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl gamma=%s" % (str(camera_number), str(self.gamma)))
            if result == 0:
                print "Gamma = %s" % str(self.gamma)
                self.pre_gamma = self.gamma
        elif(self.gain != self.pre_gain):
            result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl gain=%s" % (str(camera_number), str(self.gain)))
            if result == 0:
                print "Gain = %s" % str(self.gain)
                self.pre_gain = self.gain
        elif(self.white_balance_temperature_auto != self.pre_white_balance_temperature_auto):
            result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl white_balance_temperature_auto=%s" % (str(camera_number), str(self.white_balance_temperature_auto)))
            if result == 0:
                print "White Balance Temperature Auto = %s" % str(self.white_balance_temperature_auto)
                self.pre_white_balance_temperature_auto = self.white_balance_temperature_auto
        elif(self.white_balance_temperature != self.pre_white_balance_temperature):
            result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl white_balance_temperature_auto=0" % str(camera_number))
            self.white_balance_temperature_auto = 0
            self.pre_white_balance_temperature_auto = self.white_balance_temperature_auto
            cv2.setTrackbarPos('White Balance Temperature Auto\n' + self.default_value[6], 'Control', 0)
            if result == 0:
                result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl white_balance_temperature=%s" % (str(camera_number), str(self.white_balance_temperature)))
                if result == 0:
                    print "White Balance Temperature = %s" % str(self.white_balance_temperature)
                    self.pre_white_balance_temperature = self.white_balance_temperature
            else:
                print "Adjustment white_balance_temperature parameter fail"
        elif(self.sharpness != self.pre_sharpness):
            result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl sharpness=%s" % (str(camera_number), str(self.sharpness)))
            if result == 0:
                print "Sharpness = %s" % str(self.sharpness)
                self.pre_sharpness = self.sharpness
        elif(self.backlight_compensation != self.pre_backlight_compensation):
            result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl backlight_compensation=%s" % (str(camera_number), str(self.backlight_compensation)))
            if result == 0:
                print "Backlight Compensation = %s" % str(self.backlight_compensation)
                self.pre_backlight_compensation = self.backlight_compensation
        elif(self.exposure_auto != self.pre_exposure_auto):
            if self.exposure_auto == 1:
                real_exposure_auto = 3
                result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl exposure_auto=%s" % (str(camera_number), str(real_exposure_auto)))
            else:
                real_exposure_auto = 1
                result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl exposure_auto=%s" % (str(camera_number), str(real_exposure_auto)))
                result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl exposure_absolute=%s" % (str(camera_number), str(self.exposure_absolute)))
            if result == 0:
                print "Exposure Auto = %s" % str(real_exposure_auto)
                self.pre_exposure_auto = self.exposure_auto
        elif(self.exposure_absolute != self.pre_exposure_absolute):
            result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl exposure_auto=1" % str(camera_number))
            self.exposure_auto = 1
            self.pre_exposure_auto = self.exposure_auto
            cv2.setTrackbarPos('Exposure Auto\n' + self.default_value[10], 'Control', 0)
            if result ==0:
                result = os.system("v4l2-ctl -d /dev/video%s --set-ctrl exposure_absolute=%s" % (str(camera_number), str(self.exposure_absolute)))
                if result == 0:
                    print "Exposure Absolute = %s" % str(self.exposure_absolute)
                    self.pre_exposure_absolute = self.exposure_absolute
            else:
                print "Adjustment white_balance_temperature parameter fail"

    def get_camera_new_parameter(self):
        save_parameters = []

        for item in self.camera_parameters:
            if self.camera_parameters.index(item) == 0:
                real_brightness = str(int(self.brightness) - 64)
                save_parameters.append(item + '=' + real_brightness)
            elif self.camera_parameters.index(item) == 1:
                save_parameters.append(item + '=' + str(self.contrast))
            elif self.camera_parameters.index(item) == 2:
                save_parameters.append(item + '=' + str(self.saturation))
            elif self.camera_parameters.index(item) == 3:
                real_hue = str(int(self.hue) - 40)
                save_parameters.append(item + '=' + real_hue)
            elif self.camera_parameters.index(item) == 4:
                save_parameters.append(item + '=' + str(self.gamma))
            elif self.camera_parameters.index(item) == 5:
                save_parameters.append(item + '=' + str(self.gain))
            elif self.camera_parameters.index(item) == 6:
                save_parameters.append(item + '=' + str(self.white_balance_temperature_auto))
            elif self.camera_parameters.index(item) == 7:
                if self.white_balance_temperature < 2800:
                    save_parameters.append(item + '=2800')
                else:
                    save_parameters.append(item + '=' + str(self.white_balance_temperature))
            elif self.camera_parameters.index(item) == 8:
                save_parameters.append(item + '=' + str(self.sharpness))
            elif self.camera_parameters.index(item) == 9:
                save_parameters.append(item + '=' + str(self.backlight_compensation))
            elif self.camera_parameters.index(item) == 10:
                save_parameters.append(item + '=' + str(self.exposure_auto))
            elif self.camera_parameters.index(item) == 11:
                save_parameters.append(item + '=' + str(self.exposure_absolute))

        return save_parameters

    def save_camera_parameter(self, file_name, save_parameters):
        folder_path = self.run_path + self.camera_parameters_folder
        # Check ramdisk folder is exist
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        file_path = folder_path + '/' + file_name
        try:
            if not os.path.isfile(file_path):
                f= open(file_path, "w+")
            text_file = open(file_path, "w")
            for line in save_parameters:
                if save_parameters.index(line) == 0:
                    text_file.write(line)
                else:
                    text_file.write("\n" + line)
            text_file.close()
            print "Save Camera Parameters Complete !!\nFile Path in %s" % file_path
 
        except Exception as e:
            print str(e)

    def nothing(self, x):
        pass

    def run_camera(self, camera_number):
        frame_interval = 1  # Number of frames after which to run face detection
        fps_display_interval = 1  # seconds
        frame_rate = 0
        frame_count = 0
        start_time = time.time()

        cap = cv2.VideoCapture(camera_number)

        version = self.get_opencv_version()

        if version[:version.find('.')] == "2":
            cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.cv.CV_CAP_PROP_FOURCC, cv2.cv.CV_FOURCC(*"MJPG"))
        else:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

        cv2.namedWindow('Control', cv2.WINDOW_NORMAL)
        cv2.moveWindow('Control', 1350,0)
        cv2.createTrackbar('Brightness\n' + self.default_value[0], 'Control', 0, 128, self.nothing)
        cv2.createTrackbar('Contrast\n' + self.default_value[1], 'Control', 0, 64, self.nothing)
        cv2.createTrackbar('Saturation\n' + self.default_value[2], 'Control', 0, 128, self.nothing)
        cv2.createTrackbar('Hue\n' + self.default_value[3], 'Control', 0, 80, self.nothing)
        cv2.createTrackbar('Gamma\n' + self.default_value[4], 'Control', 72, 500, self.nothing)
        cv2.createTrackbar('Gain\n' + self.default_value[5], 'Control', 0, 100, self.nothing)
        cv2.createTrackbar('White Balance Temperature Auto\n' + self.default_value[6], 'Control', 0 , 1, self.nothing)
        cv2.createTrackbar('White Balance Temperature\n' + self.default_value[7], 'Control', 2800, 6500, self.nothing)
        cv2.createTrackbar('Sharpness\n' + self.default_value[8], 'Control', 0,6, self.nothing)
        cv2.createTrackbar('Backlight Compensation\n' + self.default_value[9], 'Control', 0, 2, self.nothing)
        cv2.createTrackbar('Exposure Auto\n' + self.default_value[10], 'Control', 0 , 1, self.nothing)
        cv2.createTrackbar('Exposure Absolute\n' + self.default_value[11], 'Control', 1, 5000, self.nothing)
        camera_parameter_values = self.get_camera_now_parameter(camera_number)
        self.set_init_controlbar_parameter_value(camera_parameter_values)

        while(True):
            self.get_controller_parameter()
            if (self.brightness != self.pre_brightness) or (self.contrast != self.pre_contrast) or (self.saturation != self.pre_saturation) or (self.hue != self.pre_hue) or (self.gamma != self.pre_gamma) or (self.gain != self.pre_gain) or (self.white_balance_temperature_auto != self.pre_white_balance_temperature_auto) or(self.white_balance_temperature != self.pre_white_balance_temperature) or (self.sharpness != self.pre_sharpness) or (self.backlight_compensation != self.pre_backlight_compensation) or (self.exposure_auto != self.pre_exposure_auto) or (self.exposure_absolute != self.pre_exposure_absolute):
                self.set_camera_parameter(camera_number)

            # Capture frame-by-frame
            ret, frame = cap.read()

            # Show camera fps
            if (frame_count % frame_interval) == 0:
                # Check our current fps
                end_time = time.time()
                if (end_time - start_time) > fps_display_interval:
                    frame_rate = int(frame_count / (end_time - start_time))
                    start_time = time.time()
                    frame_count = 0
            frame_count += 1

            cv2.putText(frame, str(frame_rate) + " fps", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),
                        thickness=2, lineType=2)
            cv2.imshow('frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                file_name = raw_input("Please Input File Name OR Push ENTER exit: ")
                if file_name == "":
                    break
                if file_name.find(" ") < 0:
                    save_parameters = self.get_camera_new_parameter()
                    self.save_camera_parameter(file_name, save_parameters)
                else:
                    print "Invalid File Name"

        # When everything done, release the capture
        try:
            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
           print str(e)
           os.kill(os.getpid(), 9)
        
if __name__ == '__main__':
    my_cap = CameraAdjustParameter()
    my_cap.check_necessary_install_package()
    camera_number = raw_input("Input usb camera number : ")
    my_cap.run_camera(int(camera_number))
