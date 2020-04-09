from PyQt5.Qt import QWidget, QColor, QPixmap, QIcon, QSize, QPalette, QBrush
from PyQt5.QtWidgets import *
from PaintBoard import *
from LineStyle import *
from Direction_Manager import *
from PIL import Image
import Cellular_Decomposition
import Generate_trajectory
import os

WIDGET_MIN_HEIGHT = 25
fig_path_rec_expand = ".\\map_fig\\Expand\\rec\\"                       # 膨胀后矩形障碍物轮廓图片保存路径
fig_path_lines_expand = ".\\map_fig\\Expand\\lines\\"                   # 膨胀后折线障碍物轮廓图片保存路径
fig_path_lines_rec_expand = ".\\map_fig\\Expand\\lines_rec\\"           # 膨胀后矩形+折线障碍物轮廓图片保存路径
fig_path_rec = ".\\map_fig\\No_Expand\\rec\\"                           # 未膨胀矩形障碍物轮廓图片保存路径
fig_path_lines = ".\\map_fig\\No_Expand\\lines\\"                       # 未膨胀折线障碍物轮廓图片保存路径
fig_path_lines_rec = ".\\map_fig\\No_Expand\\lines_rec\\"               # 未膨胀矩形+折线障碍物轮廓图片保存路径


class PaintBoardInterface(QWidget):
    def __init__(self, Parent=None):
        super().__init__(Parent)
        self.__InitData()                                       # 先初始化数据，再初始化界面
        self.__InitView()
        
    def __InitData(self):
        self.__size = QSize(1400, 800)
        self.__paintBoard = PaintBoard(self)
        self.__colorList = QColor.colorNames()                  # 获取颜色列表(字符串类型)
        self.__handlePaint = False                              # 允许手绘轨迹
        self.__selectobstacles = False                          # 允许折线框选障碍物
        self.__selectobstacles_Rec = False                      # 允许矩形框选障碍物
        self.__expandobstacles = False                          # 默认未膨胀障碍物
        self.__lineStyle_index = 0                              # 设定线型列表
        self.__dir_index = 0                                    # 设定方向列表
        self.__lineStyleMgr = LineStyleManager()
        self.__dirMgr = DirectionManager()
        self.robot_length = 0                                   # 机器人实际长度单位厘米
        self.robot_width = 0                                    # 机器人实际宽度单位厘米
        self.ratio = 0                                          # 一像素对应的厘米数
        self.coefficient = 1.3                                  # 膨胀障碍物时的调节系数
        self.width = 10                                         # 膨胀障碍物的宽度
        self.cells = 0                                          # 分割的单元总数
        self.finalpoints0 = []                                  # 矩形障碍物膨胀后的坐标列表
        self.finalpoints1 = []                                  # 折线障碍物膨胀后的坐标列表
        self.erode_img = np.ones([BOARD_HEIGHT, BOARD_WIDTH])   # 地图0-1矩阵，0表示障碍物，1表示可通行
        self.separate_img = np.ones([BOARD_HEIGHT, BOARD_WIDTH])  # 分割单元后的地图矩阵
        self.shortest_path_node = []                            # 最短路径顺序
        self.centerx, self.centery = [], []                     # 每个单元的中心点横纵坐标列表
        self.start_end_list = []                                # 各个单元内部起点终点坐标列表
        self.path_list = []                                     # 全覆盖轨迹列表
        self.r = 0                                              # 机器人转弯半径，单位厘米
        self.a_star_list = []                                   # A* 单元之间切换轨迹列表
        self.__paintBoard.grabKeyboard()                        # 只有控件开始捕获键盘，控件的键盘事件才能收到消息

    def __InitView(self):
        """
        初始化界面
        """
        self.setFixedSize(self.__size)
        self.setWindowTitle("绘制轨迹")
        main_layout = QHBoxLayout(self)                         # 新建一个水平布局作为本窗体的主布局
        main_layout.setSpacing(5)                               # 设置主布局内边距以及控件间距为10px
        main_layout.addWidget(self.__paintBoard)                # 在主界面左侧放置画板
        sub_layout = QVBoxLayout()                              # 新建垂直子布局用于放置按键
        sub_layout.setContentsMargins(5, 5, 5, 5)               # 设置此子布局和内部控件的间距为15px
        flayout = QFormLayout()                                 # 在垂直子布局中的水平布局
        flayout.setContentsMargins(0, 0, 0, 0)                  # 设置此子布局和内部控件的间距为0px
        flayout.setSpacing(5)

        self.__btn_Clear = QPushButton("清空")
        self.__btn_Clear.setParent(self)                        # 设置父对象为本界面
        self.__btn_Clear.clicked.connect(self.on_btn_Clear)     # 将按键按下信号与清空画板函数相关联
        self.__btn_Clear.setMinimumHeight(WIDGET_MIN_HEIGHT)
        sub_layout.addWidget(self.__btn_Clear)  

        self.__btn_Quit = QPushButton("退出")
        self.__btn_Quit.setParent(self)
        self.__btn_Quit.clicked.connect(self.Quit)
        self.__btn_Quit.setMinimumHeight(WIDGET_MIN_HEIGHT)
        sub_layout.addWidget(self.__btn_Quit)
        
        self.__btn_Save = QPushButton("保存轨迹/障碍轮廓")
        self.__btn_Save.setParent(self)
        self.__btn_Save.clicked.connect(self.on_btn_Save_Clicked)
        self.__btn_Save.setMinimumHeight(WIDGET_MIN_HEIGHT)
        sub_layout.addWidget(self.__btn_Save)
        
        self.__btn_handlePaint = QPushButton("手绘轨迹")
        self.__btn_handlePaint.setParent(self)
        self.__btn_handlePaint.clicked.connect(self.on_btn_Handle_Paint)
        self.__btn_handlePaint.setMinimumHeight(WIDGET_MIN_HEIGHT)
        self.__handlePaint_palette = self.__btn_handlePaint.palette()
        self.__btn_handlePaint.setAutoFillBackground(True)
        sub_layout.addWidget(self.__btn_handlePaint)

        self.__btn_Select_Obstacles = QPushButton("折线框选障碍物")
        self.__btn_Select_Obstacles.setParent(self)
        self.__btn_Select_Obstacles.clicked.connect(self.on_btn_Select_Obstacles)
        self.__btn_Select_Obstacles.setMinimumHeight(WIDGET_MIN_HEIGHT)
        self.__Select_Obstacles_palette = self.__btn_Select_Obstacles.palette()
        self.__btn_Select_Obstacles.setAutoFillBackground(True)
        sub_layout.addWidget(self.__btn_Select_Obstacles)

        self.__label_dir = QLabel(self)
        self.__label_dir.setText("选择折线框选的方向：")
        self.__label_dir.setFixedHeight(15)
        sub_layout.addWidget(self.__label_dir)
        self.__comboBox_dir = QComboBox(self)
        self.__fillDir(self.__comboBox_dir)                                              # 用"顺时针"和"逆时针"填充下拉列表
        self.__comboBox_dir.currentIndexChanged.connect(self.on_DirChanged)              # 关联下拉列表的当前索引变更信号与函数on_LineStyleChanged
        self.__comboBox_dir.setMinimumHeight(WIDGET_MIN_HEIGHT)
        sub_layout.addWidget(self.__comboBox_dir)

        self.__btn_Select_Obstacles_Rec = QPushButton("矩形框选障碍物")
        self.__btn_Select_Obstacles_Rec.setParent(self)
        self.__btn_Select_Obstacles_Rec.clicked.connect(self.on_btn_Select_Obstacles_Rec)
        self.__btn_Select_Obstacles_Rec.setMinimumHeight(WIDGET_MIN_HEIGHT)
        self.__Select_Obstacles_Rec_palette = self.__btn_Select_Obstacles_Rec.palette()
        self.__btn_Select_Obstacles_Rec.setAutoFillBackground(True)
        sub_layout.addWidget(self.__btn_Select_Obstacles_Rec)
        
        self.__label_lineStyle = QLabel(self)
        self.__label_lineStyle.setText("选择常规轨迹：")
        self.__label_lineStyle.setFixedHeight(15)
        sub_layout.addWidget(self.__label_lineStyle)
        
        self.__comboBox_lineStyle = QComboBox(self)
        self.__fillLineStyle(self.__comboBox_lineStyle)                                     # 用各种线型填充下拉列表
        self.__comboBox_lineStyle.currentIndexChanged.connect(self.on_LineStyleChanged)     # 关联下拉列表的当前索引变更信号与函数on_LineStyleChanged
        self.__comboBox_lineStyle.setMinimumHeight(WIDGET_MIN_HEIGHT)
        sub_layout.addWidget(self.__comboBox_lineStyle)
        
        self.__btn_Paint = QPushButton("绘制常规轨迹")
        self.__btn_Paint.setParent(self)
        self.__btn_Paint.clicked.connect(self.on_btn_Paint_Normal_Line)
        self.__btn_Paint.setMinimumHeight(WIDGET_MIN_HEIGHT)
        sub_layout.addWidget(self.__btn_Paint)

        self.__btn_Expand_Obstacles = QPushButton("障碍物膨胀")
        self.__btn_Expand_Obstacles.setParent(self)
        self.__btn_Expand_Obstacles.clicked.connect(self.on_btn_Expand_Obstacles)
        self.__btn_Expand_Obstacles.setMinimumHeight(WIDGET_MIN_HEIGHT)
        self.__Expand_Obstacles_palette = self.__btn_Expand_Obstacles.palette()
        self.__btn_Expand_Obstacles.setAutoFillBackground(True)
        sub_layout.addWidget(self.__btn_Expand_Obstacles)

        self.__btn_Save_Expand = QPushButton("保存膨胀后的障碍轮廓")
        self.__btn_Save_Expand.setParent(self)
        self.__btn_Save_Expand.clicked.connect(self.on_btn_Save_Expand_Clicked)
        self.__btn_Save_Expand.setMinimumHeight(WIDGET_MIN_HEIGHT)
        sub_layout.addWidget(self.__btn_Save_Expand)

        self.__btn_BCD = QPushButton("单元分解")
        self.__btn_BCD.setParent(self)
        self.__btn_BCD.clicked.connect(self.on_btn_bcd)
        self.__btn_BCD.setMinimumHeight(WIDGET_MIN_HEIGHT)
        sub_layout.addWidget(self.__btn_BCD)

        self.__btn_Generate_trajectory = QPushButton("生成覆盖轨迹")
        self.__btn_Generate_trajectory.setParent(self)
        self.__btn_Generate_trajectory.clicked.connect(self.on_btn_Generate_trajectory)
        self.__btn_Generate_trajectory.setMinimumHeight(WIDGET_MIN_HEIGHT)
        sub_layout.addWidget(self.__btn_Generate_trajectory)

        fwg = QWidget()
        self.__btn_Inputlength = QPushButton("机器人长度(cm)")
        self.__btn_Inputlength.clicked.connect(self.getLength)
        self.line1 = QLineEdit()
        self.__btn_Inputwidth = QPushButton("机器人宽度(cm)")
        self.__btn_Inputwidth.clicked.connect(self.getWidth)
        self.line2 = QLineEdit()
        self.__btn_Inputr = QPushButton("机器人转弯半径(cm)")
        self.__btn_Inputr.clicked.connect(self.getr)
        self.line3 = QLineEdit()
        self.__btn_Inputratio = QPushButton("比例(cm/pixel)")
        self.__btn_Inputratio.clicked.connect(self.getRatio)
        self.line4 = QLineEdit()
        self.__btn_Inputcoefficient= QPushButton("膨胀调节系数")
        self.__btn_Inputcoefficient.clicked.connect(self.getcoefficient)
        self.line5 = QLineEdit()
        flayout.addRow(self.__btn_Inputlength, self.line1)
        flayout.addRow(self.__btn_Inputwidth, self.line2)
        flayout.addRow(self.__btn_Inputr, self.line3)
        flayout.addRow(self.__btn_Inputratio, self.line4)
        flayout.addRow(self.__btn_Inputcoefficient, self.line5)
        fwg.setLayout(flayout)
        sub_layout.addWidget(fwg)

        self.__label_lineStyle = QLabel(self)
        self.__label_lineStyle.setText("设置轨迹线宽：")
        self.__label_lineStyle.setFixedHeight(15)
        sub_layout.addWidget(self.__label_lineStyle)

        self.__spinBox_penThickness = QSpinBox(self)
        self.__spinBox_penThickness.setMaximum(10)
        self.__spinBox_penThickness.setMinimum(2)
        self.__spinBox_penThickness.setValue(PAINTPEN_THICKNESS)                            # 默认粗细为4
        self.__spinBox_penThickness.setSingleStep(2)                                        # 最小变化值为2
        self.__spinBox_penThickness.valueChanged.connect(self.on_PenThicknessChange)        # 关联spinBox值变化信号和函数on_PenThicknessChange
        self.__spinBox_penThickness.setMinimumHeight(WIDGET_MIN_HEIGHT)
        sub_layout.addWidget(self.__spinBox_penThickness)
        
        self.__label_penColor = QLabel(self)
        self.__label_penColor.setText("画笔颜色")
        self.__label_penColor.setFixedHeight(15)
        self.__spinBox_penThickness.setMinimumHeight(WIDGET_MIN_HEIGHT)
        sub_layout.addWidget(self.__label_penColor)
        
        self.__comboBox_penColor = QComboBox(self)
        self.__fillColorList(self.__comboBox_penColor)                                      # 用各种颜色填充下拉列表
        self.__comboBox_penColor.currentIndexChanged.connect(self.on_PenColorChange)        # 关联下拉列表的当前索引变更信号与函数on_PenColorChange
        self.__comboBox_penColor.setMinimumHeight(WIDGET_MIN_HEIGHT)
        sub_layout.addWidget(self.__comboBox_penColor)
        main_layout.addLayout(sub_layout)                                                   # 将子布局加入主布局

    def getLength(self):
        if not self.__expandobstacles:
            self.robot_length, okPressed = QInputDialog.getDouble(self, "输入", "长度(cm):")
            if okPressed:
                self.line1.setText(str(self.robot_length))
        return self.robot_length

    def getWidth(self):
        if not self.__expandobstacles:
            self.robot_width, okPressed = QInputDialog.getDouble(self, "输入", "宽度(cm):")
            if okPressed:
                self.line2.setText(str(self.robot_width))
        return self.robot_width

    def getr(self):
        if not self.__expandobstacles:
            self.r, okPressed = QInputDialog.getDouble(self, "输入", "转弯半径(cm):")
            if okPressed:
                self.line3.setText(str(self.r))
        return self.r

    def getRatio(self):
        if not self.__expandobstacles:
            self.ratio, okPressed = QInputDialog.getDouble(self, "输入", "比例(cm/pixel):")
            if okPressed:
                self.line4.setText(str(self.ratio))
        return self.ratio

    def getcoefficient(self):
        """
        获得膨胀时的调节系数
        """
        if not self.__expandobstacles:
            self.coefficient, okPressed = QInputDialog.getDouble(self, "输入", "膨胀调节系数:")
            if okPressed:
                self.line5.setText(str(self.coefficient))
        return self.coefficient

    def __fillLineStyle(self, comboBox):
        for style in self.__lineStyleMgr.GetLineStyleList():
            comboBox.addItem(style, None)
        comboBox.setCurrentIndex(0)

    def __fillDir(self, comboBox):
        for style in self.__dirMgr.Dirlist():
            comboBox.addItem(style, None)
        comboBox.setCurrentIndex(0)
            
    def __fillColorList(self, comboBox):
        index_black = 0
        index = 0
        for color in self.__colorList: 
            if color == "black":
                index_black = index
            index += 1
            pix = QPixmap(100, WIDGET_MIN_HEIGHT)
            pix.fill(QColor(color))
            comboBox.addItem(QIcon(pix), None)
            comboBox.setIconSize(QSize(100, WIDGET_MIN_HEIGHT))
            comboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        comboBox.setCurrentIndex(index_black)
        
    def on_btn_Save_Clicked(self):
        currPath = '/'.join(os.getcwd().split('\\'))
        savePath = QFileDialog.getSaveFileName(self, 'Save Your Trajectory', currPath, '*.txt')
        if savePath[0] == "":
            print("Save cancel")
            return
        if not self.__paintBoard.IsEmpty():                                                         # 如果画板不为空
            if self.__paintBoard.IsRec() == True and self.__paintBoard.IsLines() == False:          # 如果只有矩形框
                trajectory = self.__paintBoard.GetRecAsData()
            elif self.__paintBoard.IsLines() == True and self.__paintBoard.IsRec() == False:        # 如果只有折线
                trajectory = self.__paintBoard.GetLinesAsData()
            elif self.__paintBoard.IsRec() and self.__paintBoard.IsLines():                         # 如果既有折线又有矩形
                trajectory = self.__paintBoard.GetRec_LinesAsData()
            else:                                                                                   # 如果都没有，则为手绘或者常规轨迹模式
                trajectory = self.__paintBoard.GetContentAsData()
        elif not self.__lineStyleMgr.Empty():
            trajectory = self.__lineStyleMgr.GetLineData()
        else:
            print("No Data")
            return
        if self.__paintBoard.IsRec() and self.__paintBoard.IsLines():
            # 如果既有折线又有矩形，由于trajectory大小特殊，需要另一种方式保存
            with open(savePath[0], 'w') as f:
                f.write("x\ty\n")
                for i in range(len(trajectory[0])):
                    for point in trajectory[0][i]:                                                  # trajectory第一行为矩形左上和右下坐标
                        f.write("%d\t%d\n" % (point[0], point[1]))
                for i in range(len(trajectory[1])):                                                 # trajectory第二行为折线的各点坐标
                    for point in trajectory[1][i]:
                        f.write("%d\t%d\n" % (point[0], point[1]))
        elif (not self.__paintBoard.IsRec() and self.__paintBoard.IsLines()) or (self.__paintBoard.IsRec() and not self.__paintBoard.IsLines()):
            # 只有折线没有矩形或者只有矩形没有折线
            with open(savePath[0], 'w') as f:
                f.write("x\ty\n")
                for i in range(len(trajectory)):
                    for point in trajectory[i]:
                        f.write("%d\t%d\n" % (point[0], point[1]))
        else:
            with open(savePath[0], 'w') as f:
                f.write("x\ty\n")
                for point in trajectory:
                    f.write("%d\t%d\n" % (point[0], point[1]))
        print("save data to %s" % savePath[0])

    def on_btn_Save_Expand_Clicked(self):
        currPath = '/'.join(os.getcwd().split('\\'))
        savePath = QFileDialog.getSaveFileName(self, 'Save Your Trajectory', currPath, '*.txt')
        if savePath[0] == "":
            print("Save cancel")
            return
        if not self.__paintBoard.IsEmpty():                                         # 如果画板不为空
            if self.__paintBoard.IsRec() == True and self.__paintBoard.IsLines() == False:          # 如果只有矩形框
                trajectory0 = self.finalpoints0
            elif self.__paintBoard.IsLines() == True and self.__paintBoard.IsRec() == False:        # 如果只有折线
                trajectory1 = self.finalpoints1
            elif self.__paintBoard.IsRec() and self.__paintBoard.IsLines():                         # 如果既有折线又有矩形
                trajectory0, trajectory1 = self.finalpoints0, self.finalpoints1
        else:
            print("No Data")
            return
        if self.__paintBoard.IsRec() and self.__paintBoard.IsLines():
            # 如果既有折线又有矩形，由于trajectory大小特殊，需要另一种方式保存
            with open(savePath[0], 'w') as f:
                f.write("x\ty\n")
                for i in range(len(trajectory0)):
                    for point in trajectory0[i]:
                        f.write("%d\t%d\n" % (point[0], point[1]))
                for i in range(len(trajectory1)):
                    for point in trajectory1[i]:
                        f.write("%d\t%d\n" % (point[0], point[1]))
            self.Save_Expand_Rec_Lines(trajectory0, trajectory1)
        elif not self.__paintBoard.IsRec() and self.__paintBoard.IsLines():                       # 只有折线没有矩形
            with open(savePath[0], 'w') as f:
                f.write("x\ty\n")
                for i in range(len(trajectory1)):
                    for point in trajectory1[i]:
                        f.write("%d\t%d\n" % (point[0], point[1]))
            self.Save_Expand_RecorLines(trajectory1, 1)
        else:                                                                                     # 只有矩形没有折线
            with open(savePath[0],  'w') as f:
                f.write("x\ty\n")
                for i in range(len(trajectory0)):
                    for point in trajectory0[i]:
                        f.write("%d\t%d\n" % (point[0], point[1]))
            self.Save_Expand_RecorLines(trajectory0, 0)
        print("save data to %s" % savePath[0])

    def on_btn_Handle_Paint(self):
        if not self.__lineStyleMgr.Empty():
            QMessageBox.information(self, "错误提示", "Oops! Clear Existed Line Firstly and Try Again!", QMessageBox.Yes | QMessageBox.No)
            return
        self.__handlePaint = not self.__handlePaint
        self.__paintBoard.SetHandlePaintMode(self.__handlePaint)
        if self.__handlePaint:
            self.__btn_handlePaint.setText("点击此处结束手绘")
            tmpPalette = QPalette(self.__handlePaint_palette)
            tmpPalette.setColor(QPalette.Button, Qt.red)
            tmpPalette.setColor(QPalette.ButtonText, Qt.red)
            self.__btn_handlePaint.setPalette(tmpPalette)
        else:
            self.__btn_handlePaint.setText("手绘轨迹")
            self.__btn_handlePaint.setPalette(self.__handlePaint_palette)

    def on_btn_Select_Obstacles(self):
        if not self.__lineStyleMgr.Empty():
            QMessageBox.information(self, "错误提示", "Oops! Clear Existed Line Firstly and Try Again!", QMessageBox.Yes | QMessageBox.No)
            return
        self.__selectobstacles = not self.__selectobstacles
        self.__paintBoard.SetSelectObstaclesMode(self.__selectobstacles)
        if self.__selectobstacles:
            self.__btn_Select_Obstacles.setText("点击此处结束框选")
            tmpPalette = QPalette(self.__Select_Obstacles_palette)
            tmpPalette.setColor(QPalette.Button, Qt.red)
            tmpPalette.setColor(QPalette.ButtonText, Qt.red)
            self.__btn_Select_Obstacles.setPalette(tmpPalette)
        else:
            self.__btn_Select_Obstacles.setText("折线框选障碍物")
            self.__btn_Select_Obstacles.setPalette(self.__Select_Obstacles_palette)

    def on_btn_Expand_Obstacles(self):
        if not self.__selectobstacles and not self.__selectobstacles_Rec:
            QMessageBox.information(self, "错误提示", "请先使用折线或矩形框选障碍物！", QMessageBox.Yes)
            return
        if self.robot_length == 0 or self.robot_width == 0 or self.ratio == 0:
            QMessageBox.information(self, "错误提示", "请先设置机器人大小以及比例！", QMessageBox.Yes)
            return
        if self.robot_length < 0 or self.robot_width < 0:
            QMessageBox.information(self, "错误提示", "机器人大小必须为正数！", QMessageBox.Yes)
            return
        if self.ratio < 0:
            QMessageBox.information(self, "错误提示", "比例必须为正数！", QMessageBox.Yes)
            return
        self.__expandobstacles = not self.__expandobstacles
        self.__paintBoard.SetExpandObstaclesMode(self.__expandobstacles)
        if self.__expandobstacles:
            self.__btn_Expand_Obstacles.setText("点击此处结束膨胀")
            tmpPalette = QPalette(self.__Expand_Obstacles_palette)
            tmpPalette.setColor(QPalette.Button, Qt.red)
            tmpPalette.setColor(QPalette.ButtonText, Qt.red)
            self.__btn_Expand_Obstacles.setPalette(tmpPalette)

            Robot_Length = self.getLength()                                         # 机器人长度
            Robot_Width = self.getWidth()                                           # 机器人宽度
            Ratio = self.getRatio()                                                 # 实际尺寸与像素的比例，例如：5cm/pixel意思为每个像素点对应实际尺寸5cm
            Robot_Len_Fig = Robot_Length / Ratio                                    # 机器人在图片中的长度尺寸
            Robot_Wid_Fig = Robot_Width / Ratio                                     # 机器人在图片中的宽度尺寸
            self.width = self.coefficient * (max(Robot_Len_Fig, Robot_Wid_Fig) / 2)
            # 障碍物周围膨胀宽度，计算规则如下：
            # 1.若机器人为矩形，取长边一半并扩大1.2倍（1.2是自己设定的默认调节系数以留出余量防止碰撞）
            # 2.若机器人为圆形，取半径一半并扩大1.2倍（1.2是自己设定的默认调节系数以留出余量防止碰撞）
            if self.__selectobstacles and self.__selectobstacles_Rec:               # 如果折线和矩形框选两种模式共用
                points = self.__paintBoard.GetRec_LinesAsData()
                r1_poly, r2_poly = self.Polygon_Judgment(points[1])
                r1_rec = [True for x in range(len(points[0]))]                           # 矩形部分肯定为凸多边形，为适应self.Expand函数，令其为全True
                r2_rec = [[-1] for x in range(len(points[0]))]                           # 同理，为适应self.Expand函数，令其为全[-1]
                self.finalpoints0 = self.Expand(self.width, points[0], r1_rec, r2_rec)   # 矩形部分膨胀后点的坐标
                self.finalpoints1 = self.Expand(self.width, points[1], r1_poly, r2_poly) # 多边形膨胀后点的坐标
                self.draw_expand(self.finalpoints0)                                      # 对矩形进行膨胀
                self.draw_expand(self.finalpoints1)                                      # 对多边形进行膨胀
            elif self.__selectobstacles and not self.__selectobstacles_Rec:              # 如果只有折线
                points = self.__paintBoard.GetLinesAsData()
                r1_poly, r2_poly = self.Polygon_Judgment(points)
                self.finalpoints1 = self.Expand(self.width, points, r1_poly, r2_poly)    # 多边形膨胀后点的坐标
                self.draw_expand(self.finalpoints1)                                      # 对多边形进行膨胀
            elif not self.__selectobstacles and self.__selectobstacles_Rec:              # 如果只有矩形，必然为凸多边形
                points = self.__paintBoard.GetRecAsData()                                # 矩形部分膨胀后点的坐标
                r1_rec = [True for x in range(len(points))]                              # 矩形部分肯定为凸多边形，为适应self.Expand函数，令其为全True
                r2_rec = [[-1] for x in range(len(points))]                              # 同理，为适应self.Expand函数，令其为全[-1]
                self.finalpoints0 = self.Expand(self.width, points, r1_rec, r2_rec)      # 矩形部分膨胀后点的坐标
                self.draw_expand(self.finalpoints0)                                      # 对矩形进行膨胀
        else:
            self.__btn_Expand_Obstacles.setText("障碍物膨胀")
            self.__btn_Expand_Obstacles.setPalette(self.__Expand_Obstacles_palette)

    def on_btn_Select_Obstacles_Rec(self):
        if not self.__lineStyleMgr.Empty():
            QMessageBox.information(self, "错误提示", "Oops! Clear Existed Line Firstly and Try Again!", QMessageBox.Yes | QMessageBox.No)
            return
        self.__selectobstacles_Rec = not self.__selectobstacles_Rec
        self.__paintBoard.SetSelectObstaclesRecMode(self.__selectobstacles_Rec)
        if self.__selectobstacles_Rec:
            self.__btn_Select_Obstacles_Rec.setText("点击此处结束框选")
            tmpPalette = QPalette(self.__Select_Obstacles_Rec_palette)
            tmpPalette.setColor(QPalette.Button, Qt.red)
            tmpPalette.setColor(QPalette.ButtonText, Qt.red)
            self.__btn_Select_Obstacles_Rec.setPalette(tmpPalette)
        else:
            self.__btn_Select_Obstacles_Rec.setText("矩形框选障碍物")
            self.__btn_Select_Obstacles_Rec.setPalette(self.__Select_Obstacles_Rec_palette)

    def on_LineStyleChanged(self):
        self.__lineStyle_index = self.__comboBox_lineStyle.currentIndex()

    def on_DirChanged(self):
        self.__dir_index = self.__comboBox_dir.currentIndex()
        return self.__dir_index
        
    def on_btn_Paint_Normal_Line(self):
        if  self.__handlePaint:
            self.on_btn_Handle_Paint()
        if not self.__paintBoard.IsEmpty():
            QMessageBox.information(self, "错误提示", "Oops! Clear Existed Line Firstly and Try Again!", QMessageBox.Yes | QMessageBox.No)
            return
        self.__lineStyleMgr.PaintLineStyle(self.__lineStyle_index, self.__paintBoard)
            
    def on_btn_Clear(self):
        self.__paintBoard.Clear()
        self.__lineStyleMgr.Clear()
        
    def on_PenColorChange(self):
        color_index = self.__comboBox_penColor.currentIndex()
        color_str = self.__colorList[color_index]
        self.__paintBoard.ChangePenColor(color_str)

    def on_PenThicknessChange(self):
        penThickness = self.__spinBox_penThickness.value()
        self.__paintBoard.ChangePenThickness(penThickness)
        
    def Quit(self):
        self.close()

    def get_vect(self, a, b):
        """
        获得两个点之间的向量，a, b为两个点的坐标，a,b的类型为1*2的list
        """
        return [b[0] - a[0], b[1] - a[1]]

    def chaji(self, v1, v2):
        """
        计算两个向量的叉积，v1，v2时两个向量，类型为1*2的list
        """
        return v1[0] * v2[1] - v1[1] * v2[0]

    def Polygon_Judgment(self, points):
        """
        判断多边形是否为凸多边形，如果不是，返回多边形顶点坐标列表中凹顶点的下标，如凹四边形中第二个点为凹顶点则返回1
        :param points: 一系列多边形顶点坐标列表，类型为list，list的每一行为一个多边形的坐标
        :return: 一系列多边形的凸凹性列表，True：凸；False：凹
        """
        result1 = []                                                                # 存储凹凸性
        result2 = []                                                                # 存储凹顶点坐标，没有凹顶点则储存[-1, -1]
        result2_temp = []                                                           # result2缓存用
        temp_vec = []                                                               # 向量缓存列表
        temp_chaji = []                                                             # 叉积缓存列表
        flag = True                                                                 # 默认为凸
        for i in range(len(points)):
            if len(points[i]) == 3:                                                 # 三角形直接判定为凸
                result1.append(True)                                                # result1记录凹凸性，直接存储True
                result2.append([-1])                                                # result2记录凹顶点坐标，凸多边形都存储-1
                continue
            else:
                for j in range(len(points[i]) - 1):                                 # 计算各邻边向量
                    temp_vec.append(self.get_vect(points[i][j], points[i][j + 1]))
                temp_vec.append(self.get_vect(points[i][len(points[i]) - 1], points[i][0]))
                for j in range(len(temp_vec) - 1):                                  # 计算各向量叉积
                    temp_chaji.append(self.chaji(temp_vec[j], temp_vec[j + 1]))
                temp_chaji.append(self.chaji(temp_vec[len(temp_vec) - 1], temp_vec[0]))
                if self.on_DirChanged() == 0:                                       # 如果为顺时针，寻找叉积为负的点
                    for j in range(len(temp_chaji)):
                        if temp_chaji[j] > 0:
                            flag = False
                            if j == len(temp_chaji) - 1:
                                result2_temp.append(0)
                            else:
                                result2_temp.append(j+1)
                    if not flag:                                                    # 如果没找到，则为凸多边形，不用进入此语句，找到的话需要进入存储result2
                        result2.append(result2_temp)
                        result2_temp = []
                else:                                                               # 如果为逆时针，寻找叉积为正的点
                    for j in range(len(temp_chaji)):
                        if temp_chaji[j] < 0:
                            flag = False
                            if j == len(temp_chaji) - 1:
                                result2_temp.append(0)
                            else:
                                result2_temp.append(j+1)
                    if not flag:                                                    # 如果没找到，则为凸多边形，不用进入此语句，找到的话需要进入存储result2
                        result2.append(result2_temp)
                        result2_temp = []
                if flag:                                                            # 如果为凸多边形
                    result1.append(True)                                            # 存储结果并且重置向量与叉积列表
                    result2.append([-1])
                    temp_chaji = []
                    temp_vec = []
                    flag = True
                else:                                                               # 如果为凹多边形
                    result1.append(False)                                           # 上述操作中已经存储过result2了，这里不用重复操作
                    temp_chaji = []
                    temp_vec = []
                    flag = True
        return result1, result2

    def Expand(self, width, points, r1, r2):
        """
        对多边形障碍物进行膨胀
        :param width: 膨胀的宽度
        :param points: 需要膨胀的多边形顶点坐标列表
        :param r1: 判断凹凸性的结果
        :param r2: 判断凹凸性的结果
        """
        temp_vec = []                                                               # 邻边向量缓存列表
        temp_vec_vertical = []                                                      # 与邻边垂直的向量缓存列表
        temp_vec_move = []                                                          # 顶点扩张向量缓存列表
        vec_move = []                                                               # 初始点到扩张后点的向量列表
        final_points_temp = []                                                      # 扩张后点的坐标缓存列表
        final_points = []                                                           # 扩张后点的坐标最终结果列表
        for i in range(len(points)):
            for j in range(len(points[i]) - 1):
                # 求邻边向量以及与边长垂直的向量，所求结果为单位化的向量，即模长为1
                ans = (sum(x ** 2 for x in self.get_vect(points[i][j], points[i][j+1]))) ** 0.5
                temp_vec.append([self.get_vect(points[i][j], points[i][j + 1])[0] / ans, self.get_vect(points[i][j], points[i][j + 1])[1] / ans])
                temp_vec_vertical.append([temp_vec[j][1], -temp_vec[j][0]])
            ans = (sum(x**2 for x in self.get_vect(points[i][len(points[i]) - 1], points[i][0]))) ** 0.5
            temp_vec.append([self.get_vect(points[i][len(points[i])-1], points[i][0])[0]/ans, self.get_vect(points[i][len(points[i])-1], points[i][0])[1]/ans])
            temp_vec_vertical.append([temp_vec[len(temp_vec) - 1][1], -temp_vec[len(temp_vec) - 1][0]])
            if r1[i]:                                                               # 如果为凸多边形
                for j in range(len(temp_vec)):
                    if j == 0:
                        # temp_vec_move为单位化的从原多边形顶点移动到膨胀后的多边形顶点的向量
                        ans = (sum(x**2 for x in[temp_vec[len(temp_vec)-1][0] - temp_vec[0][0], temp_vec[len(temp_vec)-1][1] - temp_vec[0][1]]))**0.5
                        temp_vec_move.append([(temp_vec[len(temp_vec)-1][0] - temp_vec[0][0])/ans, (temp_vec[len(temp_vec)-1][1] - temp_vec[0][1])/ans])
                    else:
                        ans = (sum(x ** 2 for x in [temp_vec[j - 1][0] - temp_vec[j][0], temp_vec[j - 1][1] - temp_vec[j][1]])) ** 0.5
                        temp_vec_move.append([(temp_vec[j - 1][0] - temp_vec[j][0]) / ans, (temp_vec[j - 1][1] - temp_vec[j][1]) / ans])
            else:                                                                   # 如果为凹多边形
                for j in range(len(temp_vec)):
                    if j == 0:
                        ans = (sum(x**2 for x in[temp_vec[len(temp_vec)-1][0] - temp_vec[0][0], temp_vec[len(temp_vec)-1][1] - temp_vec[0][1]]))**0.5
                        if j in r2[i]:                                              # 如果为凹顶点，操作与凸顶点相反
                            temp_vec_move.append([(temp_vec[0][0]-temp_vec[len(temp_vec)-1][0])/ans,(temp_vec[0][1]-temp_vec[len(temp_vec)-1][1])/ans])
                        else:                                                       # 凸顶点与凸多边形相同
                            temp_vec_move.append([(temp_vec[len(temp_vec)-1][0]-temp_vec[0][0])/ans,(temp_vec[len(temp_vec)-1][1]-temp_vec[0][1])/ans])
                    else:
                        ans = (sum(x ** 2 for x in [temp_vec[j - 1][0] - temp_vec[j][0], temp_vec[j - 1][1] - temp_vec[j][1]])) ** 0.5
                        if j in r2[i]:
                            temp_vec_move.append([(temp_vec[j][0] - temp_vec[j - 1][0]) / ans, (temp_vec[j][1] - temp_vec[j - 1][1]) / ans])
                        else:
                            temp_vec_move.append([(temp_vec[j - 1][0] - temp_vec[j][0]) / ans, (temp_vec[j - 1][1] - temp_vec[j][1]) / ans])
            for j in range(len(temp_vec_move)):                                     # 求temp_vec_move与temp_vec_vertical的余弦
                COS = abs((temp_vec_move[j][0]*temp_vec_vertical[j][0] + temp_vec_move[j][1]*temp_vec_vertical[j][1])/((temp_vec_move[j][0]**2 + temp_vec_move[j][1]**2)*(
                                temp_vec_vertical[j][0] ** 2 + temp_vec_vertical[j][1] ** 2)) ** 0.5)
                # 膨胀宽度除以余弦即为原多边形顶点移动到膨胀后的多边形顶点的距离，即float(width / COS)，
                # 顶点移动方向为temp_vec_move，移动距离为float(width / COS)，vec_move即为顶点移动向量
                vec_move.append([float(width / COS) * temp_vec_move[j][0], float(width / COS) * temp_vec_move[j][1]])
            for j in range(len(vec_move)):
                # 膨胀后的终点坐标即为初始点坐标加上vec_move
                final_points_temp.append([vec_move[j][0] + points[i][j][0], vec_move[j][1] + points[i][j][1]])
            final_points.append(final_points_temp)
            final_points_temp = []
            temp_vec = []
            temp_vec_vertical = []
            temp_vec_move = []
            vec_move = []
        return final_points

    def draw_expand(self, final_points):
        """
        在界面上绘制膨胀后的图形
        """
        temp = []
        Final_Points = []
        for i in range(len(final_points)):
            for j in range(len(final_points[i])):
                temp.append(QPoint(final_points[i][j][0], BOARD_HEIGHT - AXIS_MARGIN - final_points[i][j][1]))
            Final_Points.append(temp)
            temp = []
        self.__paintBoard.PaintPoly(Final_Points)

    def Save_Expand_RecorLines(self, points, flag):
        """
        绘制矩形或折线障碍物膨胀后的地图并且保存在文件夹下
        flag: 0, 矩形； 1, 折线
        """
        x_arr = []
        y_arr = []
        x_draw = []
        y_draw = []
        if len(points) == 0:
            return []
        for i in range(len(points)):
            for j in range(len(points[i])):
                x_arr.append(points[i][j][0])
                y_arr.append(points[i][j][1])
            x_draw.append(x_arr)
            y_draw.append(y_arr)
            x_arr, y_arr = [], []
        for i in range(len(x_draw)):
            plt.fill(x_draw[i], y_draw[i], facecolor='k')
        plt.xlim(0, BOARD_WIDTH)
        plt.ylim(0, BOARD_HEIGHT)
        plt.axis('off')
        fig = plt.gcf()
        fig.set_size_inches(float(BOARD_WIDTH) / 100, float(BOARD_HEIGHT) / 100)  # dpi = 100, output = BOARD_WIDTH*BOARD_HEIGHT pixels
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)
        if flag == 0:
            fig.savefig(fname=fig_path_rec_expand + 'rec_expand.png', dpi=100, pad_inches=0, transparent=True)
        else:
            fig.savefig(fname=fig_path_lines_expand+'lines_expand.png', dpi=100, pad_inches=0, transparent=True)

    def Save_Expand_Rec_Lines(self, points0, points1):
        """
        绘制矩形+折线障碍物膨胀后的地图并且保存在文件夹下
        """
        x_arr, y_arr = [], []
        x_draw0, y_draw0 = [], []
        x_draw1, y_draw1 = [], []
        if len(points0) == 0 and len(points1) == 0:
            return []
        for i in range(len(points0)):
            for j in range(4):
                x_arr.append(points0[i][j][0])
                y_arr.append(points0[i][j][1])
            x_draw0.append(x_arr)
            y_draw0.append(y_arr)
            x_arr, y_arr = [], []
        for i in range(len(points1)):
            for j in range(len(points1[i])):
                x_arr.append(points1[i][j][0])
                y_arr.append(points1[i][j][1])
            x_draw1.append(x_arr)
            y_draw1.append(y_arr)
            x_arr, y_arr = [], []
        for i in range(len(x_draw0)):
            plt.fill(x_draw0[i], y_draw0[i], facecolor='k')
        for i in range(len(x_draw1)):
            plt.fill(x_draw1[i], y_draw1[i], facecolor='k')
        plt.xlim(0, BOARD_WIDTH)
        plt.ylim(0, BOARD_HEIGHT)
        plt.axis('off')
        fig = plt.gcf()
        fig.set_size_inches(float(BOARD_WIDTH) / 100, float(BOARD_HEIGHT) / 100)  # dpi = 100, output = BOARD_WIDTH*BOARD_HEIGHT pixels
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)
        fig.savefig(fname=fig_path_lines_rec_expand + 'lines_rec_expand.png', dpi=100, pad_inches=0, transparent=True)

    def on_btn_bcd(self):
        """
        单元分解，膨胀机器人，不膨胀障碍物
        """
        if self.__paintBoard.IsRec() and not self.__paintBoard.IsLines():           # 如果只有矩形障碍
            img = np.array(Image.open(fig_path_rec + 'rec.png'))
        elif not self.__paintBoard.IsRec() and self.__paintBoard.IsLines():         # 如果只有折线障碍
            img = np.array(Image.open(fig_path_lines + 'lines.png'))
        elif self.__paintBoard.IsRec() and self.__paintBoard.IsLines():             # 如果两者都有
            img = np.array(Image.open(fig_path_lines_rec + 'lines_rec.png'))
        else:                                                                       # 如果两者都没有
            QMessageBox.information(self, "错误提示", "请先使用折线或矩形框选障碍物！", QMessageBox.Yes)
            return
        if len(img.shape) > 2:
            img = img[:, :, 0]
        self.erode_img = img / np.max(img)
        separate_img, self.cells = Cellular_Decomposition.bcd(self.erode_img)
        self.separate_img, self.centerx, self.centery, self.shortest_path_node = Cellular_Decomposition.map_process(separate_img, self.cells)
        print('Total cells: {}'.format(self.cells))
        Cellular_Decomposition.display_separate_map(self.separate_img, self.cells, self.centerx, self.centery, self.shortest_path_node)

    def on_btn_Generate_trajectory(self):
        """
        在每个单元内生成全覆盖轨迹
        """
        if self.robot_length == 0 or self.robot_width == 0 or self.ratio == 0:
            QMessageBox.information(self, "错误提示", "请先设置机器人大小以及比例！", QMessageBox.Yes)
            return
        if self.robot_length < 0 or self.robot_width < 0:
            QMessageBox.information(self, "错误提示", "机器人大小必须为正数！", QMessageBox.Yes)
            return
        if self.ratio < 0:
            QMessageBox.information(self, "错误提示", "比例必须为正数！", QMessageBox.Yes)
            return
        self.start_end_list, self.path_list = Generate_trajectory.cover_map(self.erode_img, self.separate_img, self.cells, self.shortest_path_node, self.robot_length, self.robot_width, self.ratio,
                                       self.coefficient, self.r)
        return
