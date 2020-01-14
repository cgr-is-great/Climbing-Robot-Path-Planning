from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QPixmap, QPainter, QPoint, QPointF, QPaintEvent, QMouseEvent, QPen, QBrush, QLineF, QPolygonF,\
                     QPainterPath, QColor, QSize, QRectF
from PyQt5.QtCore import Qt
from math import *
from Interpolate import *


class Axis:
    def __init__(self, start, end, zeroPoint):
        self.__start = start
        self.__end = end
        self.__zero = zeroPoint

    def PaintAxis(self, paintBoard, scale_margin_factor=2):
        """
        绘制坐标轴
        :param paintBoard:画板
        :param scale_margin_factor:为轴刻度的文字偏离轴的距离系数
        :return:
        """
        line = QLineF(self.__start, self.__end)
        line.setLength(line.length() - 10)                      # 留出箭头的长度
        
        v = line.unitVector()                                   # 获取轴的单位向量
        v.setLength(10)                                         # 设置箭头长度为10
        v.translate(QPointF(line.dx(), line.dy()))              # 移动到坐标轴末尾
        
        n = v.normalVector()                                    # 轴的垂直方向，normalVector()得到同长度同起点的垂直线段
        n.setLength(n.length() * 0.5)
        n2 = n.normalVector().normalVector()                    # 垂直方向的反向
        
        p1 = v.p2()
        p2 = n.p2()
        p3 = n2.p2()
        
        arrow = QPolygonF([p1, p2, p3, p1])                     # 箭头这个多边形的绘制路径
        path = QPainterPath()
        path.moveTo(self.__start)
        path.lineTo(self.__end)
        path.addPolygon(arrow)
        
        # 绘制坐标轴
        pen = QPen(QColor("black"), 6)
        pen.setJoinStyle(Qt.MiterJoin)                          # 让箭头变尖
        
        brush = QBrush()
        brush.setColor(QColor("black"))                         # 填充箭头
        brush.setStyle(Qt.SolidPattern)
        paintBoard.PaintPath(path, pen, brush)
        
        # 绘制坐标轴刻度
        axis_len = sqrt((self.__zero.x() - self.__end.x()) ** 2 + (self.__zero.y() - self.__end.y()) ** 2)
        axis_len_truncted = (axis_len // 100) * 100
        
        scale_pos = np.linspace(0, axis_len_truncted, 11)
        axis_angle_acos = acos((self.__end.x() - self.__zero.x()) / axis_len)
        axis_angle_asin = asin((self.__end.y() - self.__zero.y()) / axis_len)
        scale_pos_coord_x = scale_pos * cos(axis_angle_acos) + self.__zero.x()
        scale_pos_coord_y = scale_pos * sin(axis_angle_asin) + self.__zero.y()
        
        if axis_angle_asin >= 0:
            scale_line = line.unitVector().normalVector().normalVector().normalVector()
        else:
            scale_line = line.unitVector().normalVector()
        scale_line.setLength(5)
        scale_text = ["%d" % int(scale_pos[i]) for i in range(len(scale_pos))]
        text_pos = scale_line.unitVector()
        text_pos.translate(-1 * scale_margin_factor * (scale_line.p2() - scale_line.p1()))
        
        for i in range(1, len(scale_pos_coord_x) - 1):
            text_pos.translate(QPointF(scale_pos_coord_x[i], scale_pos_coord_y[i]) - scale_line.p1())
            scale_line.translate(QPointF(scale_pos_coord_x[i], scale_pos_coord_y[i]) - scale_line.p1())
            paintBoard.PaintLine(scale_line.p1(), scale_line.p2(), pen)
            paintBoard.PaintText(text_pos.p1(), scale_text[i], pen)
            

class StraightLinePainter:
    """
    直线轨迹绘制
    """
    def __init__(self):
        self.__trajectory = []
        
    def GetLineContent(self):
        return Interpolate_Line(self.__trajectory, "linear")

    def PaintLin(self, start, end, paintBoard):
        startPoint = paintBoard.TransferCoordinate(start[0], start[1])
        endPoint = paintBoard.TransferCoordinate(end[0], end[1])

        paintBoard.PaintLine(startPoint, endPoint)
        self.__trajectory = [startPoint, endPoint]
        
        
class CyclePainter:
    """
    圆形轨迹绘制
    """
    def __init__(self):
        self.__trajectory = []
    
    def GetLineContent(self):
        return Interpolate_Cycle(self.__trajectory)
        
    def PaintCycle(self, center_x, center_y, radius, paintBoard):

        start = paintBoard.TransferCoordinate(center_x + radius, center_y + radius)
        w = radius * 2
        h = radius * 2
        
        # 矩形用以定位圆，要求矩形的四条边与圆完全相切，当矩形不是正方形时，为椭圆
        rec = QRectF(start.x(), start.y(), w, h)
        
        '''
        startAngle = 0
        if center_x >= 0 and center_x < radius:
            startAngle = degrees(acos(center_x / radius))
        elif center_x < 0 and (center_x + radius) > 0:
            startAngle = 90 + degrees(acos(center_x / radius))
        
        spanAngle = 360
        if center_y >= 0 and center_y < radius:
            spanAngle = degrees(asin(center_y / radius)) + 180 - startAngle
        elif center_y < 0 and (center_y + radius) > 0:
            spanAngle = 180 - degrees(asin(-1 * center_y / radius)) - startAngle
        
        print(startAngle, spanAngle)
        
        paintBoard.PaintArc(rec, startAngle * 16, spanAngle*16)
        '''
        paintBoard.PaintEllipse(rec)
        
        self.__trajectory = []
        for i in range(360 * 3):
            point_x = center_x + radius * cos((i / (180 * 3)) * np.pi)
            point_y = center_y + radius * sin((i / (180 * 3)) * np.pi)
            self.__trajectory.append(QPointF(point_x, point_y))


