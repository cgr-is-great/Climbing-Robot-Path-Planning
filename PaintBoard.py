from PyQt5.QtWidgets import QWidget, QLabel, QFrame
from PyQt5.Qt import QPixmap, QPainter, QPoint, QPointF, QPaintEvent, QMouseEvent, QPen, QBrush, QLineF, QPolygonF, \
    QPainterPath, QColor, QSize, QImage
from PyQt5.QtGui import QFont, QPolygon
from PyQt5.QtCore import Qt
from LinePainter import *
from Interpolate import *
import os

PAINTPEN_THICKNESS = 4                                                              # 默认画笔粗细为4px
BACKGROUND_IMAGE_PATH = "./paintBoard_background.jpg"
BOARD_WIDTH = 1100
BOARD_HEIGHT = 780
AXIS_MARGIN = 40


class PaintBoard(QWidget):
    """
    绘制轨迹的画板
    """
    def __init__(self, Parent=None):
        super().__init__(Parent)
        self.__InitData()                                                           # 先初始化数据，再初始化界面
        self.__InitView()

    def __InitData(self):
        self.__size = QSize(BOARD_WIDTH, BOARD_HEIGHT)                              # 画板大小，左上角为(0, 0), 右下角为(1100, 780)
        self.__x_axis_end = QPointF(AXIS_MARGIN, BOARD_HEIGHT - AXIS_MARGIN)        # x坐标轴终点
        self.__x_axis_start = QPointF(BOARD_WIDTH, BOARD_HEIGHT - AXIS_MARGIN)      # x坐标轴起点
        self.__y_axis_start = QPointF(BOARD_WIDTH - AXIS_MARGIN, BOARD_HEIGHT)      # y坐标轴起点
        self.__y_axis_end = QPointF(BOARD_WIDTH - AXIS_MARGIN, AXIS_MARGIN)         # y坐标轴终点

        self.__x_axis = Axis(self.__x_axis_start, self.__x_axis_end, QPointF(BOARD_WIDTH - AXIS_MARGIN, BOARD_HEIGHT - AXIS_MARGIN))
        self.__y_axis = Axis(self.__y_axis_start, self.__y_axis_end, QPointF(BOARD_WIDTH - AXIS_MARGIN, BOARD_HEIGHT - AXIS_MARGIN))

        self.__board = QPixmap(self.__size)                                         # 新建QPixmap作为画板，尺寸为__size
        self.__board.fill(Qt.white)                                                 # 用白色填充画板

        self.__IsEmpty = True                                                       # 默认为空画板
        self.__IsRec = False                                                        # 默认不存在矩形框
        self.__IsLines = False                                                      # 默认不存在折线
        self.EraserMode = False                                                     # 默认为禁用橡皮擦模式

        self.__lastPos = QPointF(0, 0)                                              # 上一次鼠标位置
        self.__currentPos = QPointF(0, 0)                                           # 当前的鼠标位置
        self.__firstPos = QPointF(0, 0)                                             # 鼠标右键在框选每一个障碍物时第一次点下的位置

        self.__painter = QPainter()                                                 # 新建绘图工具

        self.__thickness = PAINTPEN_THICKNESS                                       # 默认画笔粗细
        self.__penColor = QColor("black")                                           # 设置默认画笔颜色为黑色
        self.__colorList = QColor.colorNames()                                      # 获取颜色列表

        self.__trajectory = []                                                      # 记录直线/圆/手绘的轨迹
        self.__trajectory_flag = []                                                 # 折线框选模式下用于记录切换障碍物时的点数
        self.__trajectory_rec = []                                                  # 记录矩形框选时障碍物的轮廓
        self.__trajectory_lines = []                                                # 记录折线框选时障碍物的轮廓
        self.__point_list = [0, 0]                                                  # 折线框选模式下记录点的坐标，第一个元素为上一次右键点击的点，第二个元素为当前的点
        self.__point_list_Rec = [0, 0]                                              # 矩形框选模式下记录点的坐标，第一个元素为上一次右键点击的点，第二个元素为当前的点
        self.__handle_Paint = False                                                 # 手绘轨迹模式
        self.__handle_paint_start = False                                           # 手绘轨迹模式开启
        self.__Select_Obstatles = False                                             # 折线框选障碍物模式
        self.__Select_Obstatles_start = False                                       # 折线框选障碍物模式开启
        self.__Select_Obstatles_Rec = False                                         # 矩形框选障碍物模式
        self.__Select_Obstatles_Rec_start = False                                   # 矩形框选障碍物模式开启
        self.__Expand_Obstatles = False                                             # 障碍物膨胀模式
        self.__Pos_Rec_x = 0                                                        # 矩形框左上角x坐标
        self.__Pos_Rec_y = 0                                                        # 矩形框左上角y坐标
        self.__Pos_Rec_l = 0                                                        # 矩形框长度
        self.__Pos_Rec_w = 0                                                        # 矩形框宽度

        self.right = 0                                                              # 从上次按下右键后按下右键的次数，默认为0即未按下
        self.right_num = 0                                                          # 按下右键的总次数默认为0
        self.middle = False                                                         # 按下中键标志位，默认为未按下
        self.middle_flag = False                                                    # 中键翻转标志位，默认为未翻转
        self.flag = False                                                           # 判断右键点击次数的标志位
        self.ctrl = False                                                           # Ctrl是否按下，默认未按下
        self.Rec = 0                                                                # 矩形框选模式下左键点击次数
        self.setMouseTracking(True)                                                 # 鼠标跟踪

    def __InitView(self):
        self.setFixedSize(self.__size)                                              # 设置界面的尺寸为__size
        background = QImage(BACKGROUND_IMAGE_PATH)                                  # 设置背景
        self.__painter.begin(self.__board)
        rec = QRectF(0, 0, self.__size.width(), self.__size.height())
        self.__painter.drawImage(rec, background)
        self.__painter.end()

        self.__x_axis.PaintAxis(self, 4)                                            # 绘制x坐标轴
        self.__y_axis.PaintAxis(self, 2)                                            # 绘制y坐标轴

        self.label_mouse = QLabel(self)                                             # 坐标显示
        self.label_mouse.setFrameShape(QFrame.Box)
        font = QFont()
        font.setBold(True)
        font.setPixelSize(15)
        self.label_mouse.setFont(font)
        self.label_mouse.setStyleSheet('border-width: 1px;border-style: solid; border-color: rgb(255, 0, 0);')
        self.label_mouse.setGeometry(50, 50, 150, 60)                               # 红框的位置(50, 50)，大小为150*60
        self.label_mouse.setMouseTracking(True)

    def Clear(self):
        """
        清空画板
        """
        self.__board.fill(Qt.white)
        background = QImage(BACKGROUND_IMAGE_PATH)                                  # 绘制背景
        self.__painter.begin(self.__board)                                          # 设置背景
        rec = QRectF(0, 0, self.__size.width(), self.__size.height())
        self.__painter.drawImage(rec, background)
        self.__painter.end()

        self.__x_axis.PaintAxis(self, 4)
        self.__y_axis.PaintAxis(self, 2)

        self.label_mouse = QLabel(self)                                             # 坐标显示
        font = QFont()
        font.setBold(True)
        font.setPixelSize(15)
        self.label_mouse.setFont(font)
        self.label_mouse.setFrameShape(QFrame.Box)
        self.label_mouse.setStyleSheet('border-width: 2px;border-style: solid; border-color: rgb(255, 0, 0);')
        self.label_mouse.setGeometry(50, 50, 150, 60)
        self.label_mouse.setMouseTracking(True)

        self.update()
        self.__IsEmpty = True
        self.__IsRec = False
        self.__IsLines = False
        self.__lastPos = QPointF(0, 0)
        self.__currentPos = QPointF(0, 0)
        self.__firstPos = QPointF(0, 0)
        self.right_num = 0
        self.__trajectory = []
        self.__trajectory_rec = []
        self.__trajectory_lines = []
        self.__trajectory_flag =[]

    def PaintPoint(self, x, y, pen=None):
        self.__painter.begin(self.__board)
        if pen is None:
            self.__painter.setPen(QPen(self.__penColor, self.__thickness))
        else:
            self.__painter.setPen(pen)

        self.__painter.drawPoint(x, y)
        self.__painter.end()
        self.update()

    def PaintRect(self, a, b, c, d, pen=None):
        self.__painter.begin(self.__board)
        if pen is None:
            self.__painter.setPen(QPen(self.__penColor, self.__thickness))
        else:
            self.__painter.setPen(pen)

        self.__painter.drawRect(a, b, c, d)
        self.__painter.end()
        self.update()

    def PaintPoly(self, points, pen=None):
        self.__painter.begin(self.__board)
        if pen is None:
            self.__painter.setPen(QPen(QColor("red"), self.__thickness))
        else:
            self.__painter.setPen(pen)

        for i in range(len(points)):
            self.__painter.drawPolygon(QPolygon(points[i]))
        self.__painter.end()
        self.update()

    def PaintLine(self, startPoint, endPoint, pen=None):
        self.__painter.begin(self.__board)
        if pen is None:
            self.__painter.setPen(QPen(self.__penColor, self.__thickness))
        else:
            self.__painter.setPen(pen)

        self.__painter.drawLine(startPoint, endPoint)
        self.__painter.end()
        self.update()

    def PaintPath(self, path, pen=None, brush=None):
        self.__painter.begin(self.__board)
        if pen is None:
            self.__painter.setPen(QPen(self.__penColor, self.__thickness))
        else:
            self.__painter.setPen(pen)

        if brush is not None:
            self.__painter.setBrush(brush)
        self.__painter.drawPath(path)
        self.__painter.end()

    def PaintArc(self, rectangle, startAngle, spanAngle, pen=None):
        self.__painter.begin(self.__board)
        if pen is None:
            self.__painter.setPen(QPen(self.__penColor, self.__thickness))
        else:
            self.__painter.setPen(pen)

        self.__painter.drawArc(rectangle, startAngle, spanAngle)
        self.__painter.end()

    def PaintEllipse(self, rectangle, pen=None):
        self.__painter.begin(self.__board)
        if pen is None:
            self.__painter.setPen(QPen(self.__penColor, self.__thickness))
        else:
            self.__painter.setPen(pen)

        self.__painter.drawEllipse(rectangle)
        self.__painter.end()

    def PaintText(self, pos, text, pen=None):
        self.__painter.begin(self.__board)
        if pen is None:
            self.__painter.setPen(QPen(self.__penColor, self.__thickness))
        else:
            self.__painter.setPen(pen)

        self.__painter.drawText(pos, text)
        self.__painter.end()

    def GetPaintRange(self):
        """
        获取绘制应该满足的范围
        """
        return [0, 0, BOARD_WIDTH - AXIS_MARGIN, BOARD_HEIGHT - AXIS_MARGIN]

    def SetHandlePaintMode(self, allow):
        """
        设置手绘模式
        """
        self.__handle_Paint = allow

    def SetSelectObstaclesMode(self, allow):
        """
        设置折线框选障碍物模式
        """
        self.__Select_Obstatles = allow

    def SetSelectObstaclesRecMode(self, allow):
        """
        设置矩形框选障碍物模式
        """
        self.__Select_Obstatles_Rec = allow

    def SetExpandObstaclesMode(self, allow):
        """
        设置膨胀障碍物模式
        """
        self.__Expand_Obstatles = allow

    def ChangePenColor(self, color="black"):
        """
        改变画笔颜色
        """
        self.__penColor = QColor(color)

    def ChangePenThickness(self, thickness=10):
        """
        改变画笔粗细
        """
        self.__thickness = thickness

    def IsEmpty(self):
        """
        返回画板是否为空
        """
        return self.__IsEmpty

    def IsRec(self):
        """
        判断画板中是否存在矩形框
        """
        return self.__IsRec

    def IsLines(self):
        """
        判断画板中是否存在折线
        """
        return self.__IsLines

    def GetContentAsQImage(self):
        """
        获取画板内容（返回QImage）
        """
        image = self.__board.toImage()
        return image

    def GetContentAsData(self):
        """
        获取画板内容（返回QPoint List）
        """
        return Interpolate_Line(self.__trajectory, "linear")

    def GetRecAsData(self):
        """
        获取矩形框的轨迹坐标（返回QPoint List）
        """
        return Interpolate_Rec(self.__trajectory_rec)

    def GetLinesAsData(self):
        """
        获取折线框选的轨迹坐标（返回QPoint List）
        """
        return Interpolate_Lines(self.__trajectory_lines, self.__trajectory_flag)

    def GetRec_LinesAsData(self):
        """
        在既有矩形又有折线时获取障碍物轮廓坐标（返回QPoint List）
        """
        return Interpolate_Rec_Lines(self.__trajectory_rec, self.__trajectory_lines, self.__trajectory_flag)

    def TransferCoordinateP(self, point):
        newPoint = QPointF(BOARD_WIDTH - AXIS_MARGIN - point.x(), BOARD_HEIGHT - AXIS_MARGIN - point.y())
        return newPoint

    def TransferCoordinate(self, x, y):
        newPoint = QPointF(BOARD_WIDTH - AXIS_MARGIN - x, BOARD_HEIGHT - AXIS_MARGIN - y)
        return newPoint

    def __checkExceedAxis(self, point):
        if point.x() > BOARD_WIDTH - AXIS_MARGIN:
            return True
        if point.y() > BOARD_HEIGHT - AXIS_MARGIN:
            return True
        return False

    def paintEvent(self, paintEvent):
        """
        绘图时必须使用QPainter的实例，此处为__painter，绘图在begin()函数与end()函数间进行
        begin(param)的参数要指定绘图设备，即把图画在哪里，drawPixmap用于绘制QPixmap类型的对象
        :param paintEvent:绘图事件
        """
        self.__painter.begin(self)
        self.__painter.drawPixmap(0, 0, self.__board)                                   # 0, 0为绘图的左上角起点的坐标，__board即要绘制的图
        self.__painter.end()

    def keyPressEvent(self, keyevent):
        if keyevent.modifiers() == Qt.ControlModifier:
            self.ctrl = True

    def mousePressEvent(self, mouseEvent):
        """
        左键按下不放，连续绘制轨迹模式；
        右键按下松开，再次右键按下，在两次按下位置之间绘制线段，即折线绘制框选模式；
        中键按下一次，暂停框选，再按一次，恢复框选
        Ctrl+左键，矩形框选障碍物模式
        """
        if mouseEvent.buttons() == Qt.LeftButton:                                       # 鼠标左键按下时，连续绘制轨迹模式
            if not self.ctrl:
                self.__currentPos = mouseEvent.pos()
                self.__lastPos = self.__currentPos
                if not self.__handle_Paint:
                    return
                self.__handle_paint_start = True
                self.__trajectory.append(self.TransferCoordinateP(self.__currentPos))
            else:
                if not self.__Select_Obstatles_Rec:
                    return
                self.__Select_Obstatles_Rec_start = True
                self.Rec = self.Rec + 1
                self.__point_list_Rec[0] = self.__lastPos                               # 添加障碍物的轮廓坐标到self.__point_list
                self.__point_list_Rec[1] = self.__currentPos

                self.__lastPos = self.__currentPos
                self.__currentPos = mouseEvent.pos()

                self.__Pos_Rec_x = self.__point_list_Rec[0].x()                         # 矩形左上角点横坐标
                self.__Pos_Rec_y = self.__point_list_Rec[0].y()                         # 矩形左上角点纵坐标
                self.__Pos_Rec_l = self.__point_list_Rec[1].x() - self.__point_list_Rec[0].x()          # 矩形水平方向长度
                self.__Pos_Rec_w = self.__point_list_Rec[1].y() - self.__point_list_Rec[0].y()          # 矩形垂直方向长度
                if self.Rec == 1:
                    self.PaintPoint(mouseEvent.x(), mouseEvent.y(), QPen(self.__penColor, 8))
                    self.__IsEmpty = False
                    self.__IsRec = True
                    self.__trajectory_rec.append(self.TransferCoordinateP(self.__currentPos))
                if self.Rec == 2:
                    self.PaintPoint(mouseEvent.x(), mouseEvent.y(), QPen(self.__penColor, 8))
                    self.PaintRect(self.__Pos_Rec_x, self.__Pos_Rec_y, self.__Pos_Rec_l, self.__Pos_Rec_w)
                    self.__IsEmpty = False
                    self.__IsRec = True
                    self.Rec = 0
                    self.__trajectory_rec.append(self.TransferCoordinateP(self.__currentPos))

        elif mouseEvent.buttons() == Qt.RightButton:                                    # 鼠标右键按下时，框选障碍物模式
            if not self.__Select_Obstatles:
                return
            self.__Select_Obstatles_start = True
            self.__point_list[0] = self.__lastPos                                       # 添加障碍物的轮廓坐标到self.__point_list
            self.__point_list[1] = self.__currentPos

            self.__lastPos = self.__currentPos
            self.__currentPos = mouseEvent.pos()
            self.right = self.right + 1                                                 # 按下右键次数加一
            self.PaintPoint(mouseEvent.x(), mouseEvent.y(), QPen(self.__penColor, 8))   # 绘制折线顶点
            self.right_num = self.right_num + 1
            if self.right_num == 1 or (self.right == 1 and self.flag == False):         # 记录框选每一个障碍物时第一次点击的位置
                self.__firstPos = mouseEvent.pos()

            self.__IsEmpty = False
            self.__trajectory_lines.append(self.TransferCoordinateP(self.__currentPos))
            if not self.middle:
                if self.right == 2 and self.flag == False:
                    self.flag = True
                    self.PaintLine(self.__point_list[0], self.__point_list[1])
                    self.__IsEmpty = False
                    self.__IsLines = True
                    self.middle_flag = False
                    self.right = 0
                if self.right == 1 and self.flag == True:
                    self.PaintLine(self.__point_list[0], self.__point_list[1])
                    self.__IsEmpty = False
                    self.__IsLines = True
                    self.middle_flag = False
                    self.right = 0
        elif mouseEvent.buttons() == Qt.MiddleButton:                                   # 鼠标中键按下时，暂停框选障碍物
            self.middle = not self.middle
            self.middle_flag = True
            self.right = 0
            self.flag = False
            if self.middle_flag == True and self.middle == False:
                self.__trajectory_flag.append(self.right_num)
                self.PaintLine(self.__firstPos, self.__point_list[1])
                self.__firstPos = QPointF(0, 0)

    def mouseMoveEvent(self, mouseEvent):
        self.__currentPos = mouseEvent.pos()                                            # 鼠标移动时，更新当前位置，并在上一个位置和当前位置间画线
        if self.__checkExceedAxis(self.__currentPos):
            return
        realPos = self.TransferCoordinateP(self.__currentPos)
        self.label_mouse.setText("x: %d, y: %d" % (realPos.x(), realPos.y()))

        if mouseEvent.buttons() == Qt.LeftButton:
            if not self.__handle_Paint:
                return
            if not self.__handle_paint_start:
                return
            self.PaintLine(self.__lastPos, self.__currentPos)
            self.__trajectory.append(self.TransferCoordinateP(self.__currentPos))
            self.__lastPos = self.__currentPos

    def mouseReleaseEvent(self, mouseEvent):
        if not self.__handle_Paint:
            return
        self.__handle_paint_start = False
        self.__IsEmpty = False                                                          # 画板不再为空
