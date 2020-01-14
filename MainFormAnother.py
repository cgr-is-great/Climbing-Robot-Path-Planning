# -*- coding: utf-8 -*-


import time
import sys
import numpy as np
import cv2
import LocationDetection

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from cv2 import *

from LocationDetection import *
from Ui_MainForm import *
from Size_get import *


class VideoBox(MainForm):
    VIDEO_TYPE_OFFLINE = 0
    VIDEO_TYPE_REAL_TIME = 1

    STATUS_INIT = 0
    STATUS_PLAYING = 1
    STATUS_PAUSE = 2

    video_url = ""

    def __init__(self, video_type=VIDEO_TYPE_OFFLINE, auto_play=False):
        super(VideoBox, self).__init__()
        # QWidget.__init__(self)
        self.video_type = video_type                # 0: offline    1: realTime
        self.auto_play = auto_play
        self.status = self.STATUS_INIT              # 0: init   1:playing   2: pause

        # 组件展示
        self.pictureLabel = QLabel()
        # init_image = QPixmap("test11C_Moment.jpg").scaled(432, 768)
        # self.pictureLabel.setPixmap(init_image)
        self.pictureLabel.setFixedSize(432, 768)
        self.pictureLabel.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.pictureLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.pictureLabel.setFont(QFont("Roman times", 10, QFont.Bold))             # 设置字体的类型大小和加粗
        self.pictureLabel.setText("原图像区域")
        
        self.pictureLabelL = QLabel()
        # init_imageL = QPixmap("test11C_Moment.jpg").scaled(432, 768)
        # self.pictureLabelL.setPixmap(init_imageL)
        self.pictureLabelL.setFixedSize(432, 768)
        self.pictureLabelL.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.pictureLabelL.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.pictureLabelL.setFont(QFont("Roman times", 10, QFont.Bold))
        self.pictureLabelL.setText("投影视图区域")

        self.pictureLabelT = QLabel()
        # init_imageL = QPixmap("test11C_Moment.jpg").scaled(432, 768)
        # self.pictureLabelL.setPixmap(init_imageL)
        self.pictureLabelT.setFixedSize(432, 768)
        self.pictureLabelT.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.pictureLabelT.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.pictureLabelT.setFont(QFont("Roman times", 10, QFont.Bold))
        self.pictureLabelT.setText("轨迹跟踪区域")

        # 定位结果显示模块
        self.resultxLabel = QLabel()
        self.resultxLabel.setFixedSize(200, 20)
        self.resultxLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.resultxLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.resultxLabel.setFont(QFont("Roman times", 10))
        self.resultxLabel.setText("X(cm)：")

        self.resultyLabel = QLabel()
        self.resultyLabel.setFixedSize(200, 20)
        self.resultyLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.resultyLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.resultyLabel.setFont(QFont("Roman times", 10))
        self.resultyLabel.setText("Y(cm)：")

        self.resultaLabel = QLabel()
        self.resultaLabel.setFixedSize(200,20)
        self.resultaLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.resultaLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.resultaLabel.setFont(QFont("Roman times", 10))
        self.resultaLabel.setText("Angle(°)：")

        self.playButton = QPushButton()
        self.playButton.setEnabled(True)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.switch_video)

        control_box = QHBoxLayout()
        control_box.setContentsMargins(0, 0, 0, 0)
        control_box.addWidget(self.playButton)

        video_box = QHBoxLayout()
        video_box.setContentsMargins(0, 0, 0, 0)
        video_box.addWidget(self.pictureLabel)
        video_box.addWidget(self.pictureLabelL)
        video_box.addWidget(self.pictureLabelT)        
        
        result_box = QHBoxLayout()
        result_box.setContentsMargins(0, 0, 0, 0)
        result_box.addWidget(self.resultxLabel)
        result_box.addWidget(self.resultyLabel) 
        result_box.addWidget(self.resultaLabel)  
        
        layout = QVBoxLayout()
        # layout.addWidget(self.pictureLabel)
        layout.addLayout(video_box)
        layout.addLayout(result_box)
        layout.addLayout(control_box)

        main_frame = QWidget()
        main_frame.setLayout(layout)
        self.setCentralWidget(main_frame)
        
        self.filepath_signal.connect(self.video_playing)
    
    def video_playing(self, video_url):
        self.video_url = video_url
        # timer 设置
        self.timer = VideoTimer()
        self.timer.timeSignal.signal[str].connect(self.show_video_images)

        # video 初始设置
        self.playCapture = VideoCapture()
        if self.video_url != "":
            self.playCapture.open(self.video_url)
            fps = self.playCapture.get(CAP_PROP_FPS)
            self.timer.set_fps(fps)
            self.playCapture.release()
            if self.auto_play:
                self.switch_video()
            # self.videoWriter = VideoWriter('*.mp4', VideoWriter_fourcc('M', 'J', 'P', 'G'), self.fps, size)
        
        self.SrcPointsA = PerspectiveTransform_get(self.video_url)

        Sizeget = Size_get()
        Sizeget.setWindowModality(Qt.ApplicationModal)
        Sizeget.exec_()
     
        self.BHeight = Sizeget.BHeight
        self.BWidth = Sizeget.BWidth
        
        if self.BHeight/self.BWidth > 1920/1080:        
            CanvasPointsA=np.array([[1800,100],[100,100],[1800,100+1700*Sizeget.BWidth/Sizeget.BHeight],[100,100+1700*Sizeget.BWidth/Sizeget.BHeight]],np.float32)
            self.PerspectiveMatrix = cv2.getPerspectiveTransform(self.SrcPointsA, CanvasPointsA)
            self.Base='Height'
        else:
            CanvasPointsA=np.array([[1800,100],[1800-900*Sizeget.BHeight/Sizeget.BWidth,100],[1800,1000],[1800-900*Sizeget.BHeight/Sizeget.BWidth,1000]],np.float32)
            self.PerspectiveMatrix = cv2.getPerspectiveTransform(self.SrcPointsA, CanvasPointsA)
            self.Base='Width'              

    def reset(self):
        self.timer.stop()
        self.playCapture.release()
        self.status = VideoBox.STATUS_INIT
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
#        LocationDetection.FirstM = True

    def show_video_images(self):
        if self.playCapture.isOpened():
            success, frame = self.playCapture.read()
            frameinital = copy.deepcopy(frame)
            if success:                
                frame=np.rot90(frame,-1)
                frame = cv2.resize(frame, (0, 0), fx=0.4, fy=0.4, interpolation=cv2.INTER_CUBIC)
                height, width = frame.shape[:2]
                if frame.ndim == 3:
                    rgb = cvtColor(frame, COLOR_BGR2RGB)
                elif frame.ndim == 2:
                    rgb = cvtColor(frame, COLOR_GRAY2BGR)
                    
                temp_image = QImage(rgb.flatten(),width , height, QImage.Format_RGB888)
                temp_pixmap = QPixmap.fromImage(temp_image)
                self.pictureLabel.setPixmap(temp_pixmap)
                
                frame = copy.deepcopy(frameinital)
                frameL,self.X,self.Y,self.ANGLE=LocationDetection(self.PerspectiveMatrix,frame,self.BHeight,self.BWidth,self.Base)
                frameL = cv2.resize(frameL, (0, 0), fx=0.4, fy=0.4, interpolation=cv2.INTER_CUBIC)
                height, width = frameL.shape[:2]
                if frameL.ndim == 3:
                    rgbL = cvtColor(frameL, COLOR_BGR2RGB)
                elif frameL.ndim == 2:
                    rgbL = cvtColor(frameL, COLOR_GRAY2BGR)
                    
                temp_imageL = QImage(rgbL.flatten(),width , height, QImage.Format_RGB888)
                temp_pixmapL = QPixmap.fromImage(temp_imageL)
                self.pictureLabelL.setPixmap(temp_pixmapL)

                frameT=TrajectoryTracking()
                frameT = cv2.resize(frameT, (0, 0), fx=0.4, fy=0.4, interpolation=cv2.INTER_CUBIC)
                height, width = frameT.shape[:2]
                if frameT.ndim == 3:
                    rgbT = cvtColor(frameT, COLOR_BGR2RGB)
                elif frameT.ndim == 2:
                    rgbT = cvtColor(frameT, COLOR_GRAY2BGR)
                    
                temp_imageT = QImage(rgbT.flatten(),width , height, QImage.Format_RGB888)
                temp_pixmapT = QPixmap.fromImage(temp_imageT)
                self.pictureLabelT.setPixmap(temp_pixmapT)

                self.resultxLabel.setText("X(cm)：%d"%self.X)
                self.resultyLabel.setText("Y(cm)：%d"%self.Y)
                self.resultaLabel.setText("Angle(°)：%.2f"%self.ANGLE)
                    
            else:
                print("read failed, no frame data")
                success, frame = self.playCapture.read()
                if not success and self.video_type is VideoBox.VIDEO_TYPE_OFFLINE:
                    print("play finished")  # 判断本地文件播放完毕
                    self.reset()
                    self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
                return
        else:
            print("open file or capturing device error, init again")
            self.reset()

    def switch_video(self):
        if self.video_url == "" or self.video_url is None:
            return
        if self.status is VideoBox.STATUS_INIT:
            self.playCapture.open(self.video_url)
            self.timer.start()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        elif self.status is VideoBox.STATUS_PLAYING:
            self.timer.stop()
            if self.video_type is VideoBox.VIDEO_TYPE_REAL_TIME:
                self.playCapture.release()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        elif self.status is VideoBox.STATUS_PAUSE:
            if self.video_type is VideoBox.VIDEO_TYPE_REAL_TIME:
                self.playCapture.open(self.video_url)
            self.timer.start()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        self.status = (VideoBox.STATUS_PLAYING,
                       VideoBox.STATUS_PAUSE,
                       VideoBox.STATUS_PLAYING)[self.status]


class Communicate(QObject):
    signal = pyqtSignal(str)


class VideoTimer(QThread):

    def __init__(self, frequent=20):
        QThread.__init__(self)
        self.stopped = False
        self.frequent = frequent
        self.timeSignal = Communicate()
        self.mutex = QMutex()

    def run(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
        while True:
            if self.stopped:
                return
            self.timeSignal.signal.emit("1")
            time.sleep(1 / self.frequent)

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

    def is_stopped(self):
        with QMutexLocker(self.mutex):
            return self.stopped

    def set_fps(self, fps):
        self.frequent = fps


if __name__ == "__main__":
   app = QApplication(sys.argv)
   box = VideoBox()
   box.show()
   sys.exit(app.exec_())