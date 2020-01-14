
Clockwise = 0
Counterclockwise = 1


class DirectionManager():
    def __init__(self):
        self.currLine = Clockwise

    def Dirlist(self):
        return ["顺时针", "逆时针"]
