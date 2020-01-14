from PyQt5.Qt import QWidget, QSize
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt
from LinePainter import *

LINE_STYLE_INVALID = 0
LINE_STYLE_STRAIGHT_LINE = 1
LINE_STYLE_CYCLE = 2


class StraightLineInfoWindow(QWidget):
    def __init__(self, Parent=None):
        super().__init__(Parent)
        self.__InitData()                                       # 先初始化数据，再初始化界面
        self.__InitView()
        
    def __InitData(self):
        self.__size = QSize(300, 200)
        self.__start_point = [1, 1]
        self.__end_point = [100, 100]
        self.__valid = False                                    # 标识数据是否有效
        self.__action = None  
        self.__range = [0, 0, 0, 0]
    
    def __InitView(self):
        self.setFixedSize(self.__size)
        self.setWindowTitle("输入直线参数")
        
        main_layout = QVBoxLayout(self) 
        main_layout.setSpacing(10) 
        
        sub_layout_1 = QHBoxLayout(self)
        sub_layout_1.setSpacing(10)
        
        self.__label_1 = QLabel(self)
        self.__label_1.setText("start point: ")
        self.__label_1.setFixedHeight(20)
        sub_layout_1.addWidget(self.__label_1)
        
        self.__label_2 = QLabel(self)
        self.__label_2.setText("x ")
        self.__label_2.setFixedHeight(20)
        sub_layout_1.addWidget(self.__label_2)
        
        self.__lineEdit_start_x = QLineEdit("0")
        self.__lineEdit_start_x.setFixedHeight(20)
        sub_layout_1.addWidget(self.__lineEdit_start_x)
        
        self.__label_3 = QLabel(self)
        self.__label_3.setText("y ")
        self.__label_3.setFixedHeight(20)
        sub_layout_1.addWidget(self.__label_3)
        
        self.__lineEdit_start_y = QLineEdit("0")
        self.__lineEdit_start_y.setFixedHeight(20)
        sub_layout_1.addWidget(self.__lineEdit_start_y)
        
        main_layout.addLayout(sub_layout_1)
        
        sub_layout_2 = QHBoxLayout(self)
        sub_layout_2.setSpacing(10)
        
        self.__label_4 = QLabel(self)
        self.__label_4.setText("end point: ")
        self.__label_4.setFixedHeight(20)
        sub_layout_2.addWidget(self.__label_4)
        
        self.__label_5 = QLabel(self)
        self.__label_5.setText("x ")
        self.__label_5.setFixedHeight(20)
        sub_layout_2.addWidget(self.__label_5)
        
        self.__lineEdit_end_x = QLineEdit("100")
        self.__lineEdit_end_x.setFixedHeight(20)
        sub_layout_2.addWidget(self.__lineEdit_end_x)
        
        self.__label_6 = QLabel(self)
        self.__label_6.setText("y ")
        self.__label_6.setFixedHeight(20)
        sub_layout_2.addWidget(self.__label_6)
        
        self.__lineEdit_end_y = QLineEdit("100")
        self.__lineEdit_end_y.setFixedHeight(20)
        sub_layout_2.addWidget(self.__lineEdit_end_y)
        
        main_layout.addLayout(sub_layout_2)
        
        self.__btn_Quit = QPushButton("取消")
        self.__btn_Quit.setParent(self)
        self.__btn_Quit.clicked.connect(self.Quit)
        main_layout.addWidget(self.__btn_Quit)
        
        self.__btn_OK = QPushButton("确认")
        self.__btn_OK.setParent(self)
        self.__btn_OK.clicked.connect(self.Confirm)
        main_layout.addWidget(self.__btn_OK)
    
    def __resetData(self):
        self.__start_point = [0, 0]
        self.__end_point = [100, 100]
        self.__valid = False
        
    def __checkExceedRange(self, point):
        if point[0] < self.__range[0] or point[0] > (self.__range[0] + self.__range[2]):
            return False
        if point[1] < self.__range[1] or point[1] > (self.__range[1] + self.__range[3]):
            return False
        return True
    
    def SetConfirmAction(self, action):
        self.__action = action
        
    def SetPaintRange(self, range):
        self.__range = range
        
    def Quit(self):
        self.__resetData()
        self.close()
        
    def Confirm(self):
        self.__resetData()

        try:
            self.__start_point[0] = int(self.__lineEdit_start_x.text())
            self.__start_point[1] = int(self.__lineEdit_start_y.text())
            self.__end_point[0] = int(self.__lineEdit_end_x.text())
            self.__end_point[1] = int(self.__lineEdit_end_y.text())
        except ValueError:
            QMessageBox.information(self, "错误提示", "Oops! Invalid Input. Try Again!", QMessageBox.Yes | QMessageBox.No)
            self.__resetData()
            return
            
        try:
            if self.__checkExceedRange(self.__start_point) == False:
                raise ValueError
            if self.__checkExceedRange(self.__end_point) == False:
                raise ValueError
        except ValueError:
            QMessageBox.information(self, "错误提示", "Oops! Exceed Range, Try Again!", QMessageBox.Yes | QMessageBox.No)
            self.__resetData()
            return
            
        self.__valid = True
        self.close()
        self.__action(LINE_STYLE_STRAIGHT_LINE, self.GetParams())
        
    def Valid(self):
        return self.__valid
        
    def GetParams(self):
        return [self.__start_point, self.__end_point]
        
    
class CycleInfoWindow(QWidget):
    def __init__(self, Parent=None):
        super().__init__(Parent)
        
        self.__InitData()
        self.__InitView()
        
    def __InitData(self):
        self.__size = QSize(300, 200)
        self.__center_x = 50  # 圆心
        self.__center_y = 50
        self.__radius = 10 # 半径
        self.__valid = False # 标识数据是否有效
        self.__action = None
        self.__range = [0, 0, 0, 0]
        
    def __InitView(self):
        
        self.setFixedSize(self.__size)
        self.setWindowTitle("输入圆参数")
        
        main_layout = QVBoxLayout(self) 
        main_layout.setSpacing(10) 
        
        sub_layout_1 = QHBoxLayout(self)
        sub_layout_1.setSpacing(10)
        
        self.__label_1 = QLabel(self)
        self.__label_1.setText("x0: ")
        self.__label_1.setFixedHeight(20)
        sub_layout_1.addWidget(self.__label_1)
        
        self.__lineEdit_center_x = QLineEdit("50")
        self.__lineEdit_center_x.setFixedHeight(20)
        sub_layout_1.addWidget(self.__lineEdit_center_x)
        
        main_layout.addLayout(sub_layout_1)
        
        sub_layout_2 = QHBoxLayout(self)
        sub_layout_2.setSpacing(10)
        
        self.__label_2 = QLabel(self)
        self.__label_2.setText("y0: ")
        self.__label_2.setFixedHeight(20)
        sub_layout_2.addWidget(self.__label_2)
        
        self.__lineEdit_center_y = QLineEdit("50")
        self.__lineEdit_center_y.setFixedHeight(20)
        sub_layout_2.addWidget(self.__lineEdit_center_y)
        
        main_layout.addLayout(sub_layout_2)
        
        sub_layout_3 = QHBoxLayout(self)
        sub_layout_3.setSpacing(10)
        
        self.__label_3 = QLabel(self)
        self.__label_3.setText("r: ")
        self.__label_3.setFixedHeight(20)
        sub_layout_3.addWidget(self.__label_3)
        
        self.__lineEdit_radius = QLineEdit("10")
        self.__lineEdit_radius.setFixedHeight(20)
        sub_layout_3.addWidget(self.__lineEdit_radius)
        
        main_layout.addLayout(sub_layout_3)
        
        self.__btn_Quit = QPushButton("取消")
        self.__btn_Quit.setParent(self) #设置父对象为本界面
        self.__btn_Quit.clicked.connect(self.Quit)
        main_layout.addWidget(self.__btn_Quit)
        
        self.__btn_OK = QPushButton("确认")
        self.__btn_OK.setParent(self) #设置父对象为本界面
        self.__btn_OK.clicked.connect(self.Confirm)
        main_layout.addWidget(self.__btn_OK)
    
    def __restData(self):
        self.__center_x = 50
        self.__center_y = 50
        self.__radius = 100 
        self.__valid = False
     
    def __checkExceedRange(self, point):
        if point[0] < self.__range[0] or point[0] > (self.__range[0] + self.__range[2]):
            return False
        if point[1] < self.__range[1] or point[1] > (self.__range[1] + self.__range[3]):
            return False
        return True
    
    def SetConfirmAction(self, action):
        self.__action = action
        
    def SetPaintRange(self, range):
        self.__range = range
        
    def Quit(self):
        self.__restData()
        self.close()
        
    def Confirm(self):
    
        self.__restData()
        
        try:
            self.__center_x = int(self.__lineEdit_center_x.text())
            self.__center_y = int(self.__lineEdit_center_y.text())
            self.__radius = int(self.__lineEdit_radius.text())
        except ValueError:
            QMessageBox.information(self, "错误提示", "Oops! Invalid Input. Try Again!", QMessageBox.Yes | QMessageBox.No)
            return
            
        left = [self.__center_x - self.__radius, self.__center_y]
        right = [self.__center_x + self.__radius, self.__center_y]
        top = [self.__center_x, self.__center_y + self.__radius]
        right = [self.__center_x, self.__center_y - self.__radius]
        try:
            if self.__checkExceedRange(left) == False:
                raise ValueError
            if self.__checkExceedRange(left) == False:
                raise ValueError
            if self.__checkExceedRange(left) == False:
                raise ValueError
            if self.__checkExceedRange(left) == False:
                raise ValueError
        except:
            QMessageBox.information(self, "错误提示", "Oops! Exceed Range, Try Again!", QMessageBox.Yes | QMessageBox.No)
            return

        self.__valid = True
        self.close()
        
        self.__action(LINE_STYLE_CYCLE, self.GetParams())
        
    def Valid(self):
        return self.__valid
        
    def GetParams(self):
        return [self.__center_x, self.__center_y, self.__radius]
        
    
class LineStyleManager():
    def __init__(self):
        self.__sl = StraightLineInfoWindow()
        self.__cyc = CycleInfoWindow()
        self.__slp = StraightLinePainter()
        self.__cycp = CyclePainter()
        self.__paintBoard = None
        self.__valid = False
        self.__currLine = LINE_STYLE_INVALID
        pass
    
    def Clear(self):
        self.__valid = False
        
    def Empty(self):
        return self.__valid == False
        
    def __getLineStyleParams(self, lineStyle):
        if lineStyle == LINE_STYLE_INVALID:
            return None
        if lineStyle == LINE_STYLE_STRAIGHT_LINE:
            self.__sl.show()

            return self.__sl.GetParams()
        elif lineStyle == LINE_STYLE_CYCLE:
            self.__cyc.show()
            self.__cyc.setWindowModality(Qt.ApplicationModal)
            if self.__cyc.Valid() == False:
                return None
            return self.__cyc.GetParams()
        else:
            return None

    def GetLineStyleList(self):
        return ["-----------", "直线", "圆形"]
    
    def GetLineData(self):
        if self.__valid == False:
            return []
        if self.__currLine == LINE_STYLE_STRAIGHT_LINE:
            return self.__slp.GetLineContent()
        elif self.__currLine == LINE_STYLE_CYCLE:
            return self.__cycp.GetLineContent()
        else:
            return []
        
    def __paintAction(self, lineStyle, params):
        if lineStyle == LINE_STYLE_STRAIGHT_LINE:
            self.__slp.PaintLin(params[0], params[1], self.__paintBoard)
            self.__valid = True
            self.__currLine = LINE_STYLE_STRAIGHT_LINE
        elif lineStyle == LINE_STYLE_CYCLE:
            self.__cycp.PaintCycle(params[0], params[1], params[2], self.__paintBoard)
            self.__valid = True
            self.__currLine = LINE_STYLE_CYCLE
        return

    def PaintLineStyle(self, lineStyle, paintBoard):
        if self.__valid == True:
            QMessageBox.information(None, "错误提示", "Oops! Clear Existed Line Firstly and Try Again!", QMessageBox.Yes | QMessageBox.No)
            return
            
        self.__paintBoard = paintBoard
        
        if lineStyle == LINE_STYLE_STRAIGHT_LINE:
            self.__sl.SetPaintRange(paintBoard.GetPaintRange())
            self.__sl.SetConfirmAction(self.__paintAction)
        elif lineStyle == LINE_STYLE_CYCLE:
            self.__cyc.SetPaintRange(paintBoard.GetPaintRange())
            self.__cyc.SetConfirmAction(self.__paintAction)
        
        self.__getLineStyleParams(lineStyle)
        return
