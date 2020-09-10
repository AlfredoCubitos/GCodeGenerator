import os
#from PySide2.QtGui import QPixmap
from PyQt5.QtGui import QPixmap


CR="\n"

class ContourArc():
    
    def __init__(self,parent):
        
        path = os.getcwd()
        self.__imageNames = [
                    # left down
                    path + "/img/contour/circle-pic1_1.jpg",
                    # left upper
                    path + "/img/contour/circle-pic1_2.jpg",
                    # right upper
                    path + "/img/contour/circle-pic1_3.jpg",
                    # right down
                    path + "/img/contour/circle-pic1_4.jpg",
                    # center
                    path + "/img/contour/circle-pic1_5.jpg"
                ]
        self.parent = parent
        self.window = parent.window
        
        ## use lambda to pass extra parameter to the Signal function
        self.window.rbCP_1.clicked.connect(lambda clicked: self.onCenterPosChange(0))
        self.window.rbCP_2.clicked.connect(lambda clicked: self.onCenterPosChange(1))
        self.window.rbCP_3.clicked.connect(lambda clicked: self.onCenterPosChange(2))
        self.window.rbCP_4.clicked.connect(lambda clicked: self.onCenterPosChange(3))
        self.window.rbCP_5.clicked.connect(lambda clicked: self.onCenterPosChange(4))
        
        for i in range(1,6):
            obj = "rbCP_"+str(i)
            attr = getattr(self.window,obj)
            if attr.isChecked():
                attr.clicked.emit()
        
    def onCenterPosChange(self, pos):
        pixmap = QPixmap()
        if pixmap.load(self.__imageNames[pos]):
            self.window.image.setPixmap(pixmap)
        else:
            print("Image Load Error ", self.__imageNames[pos])


        
    def generateGCode(self,parent):
        gc = ""
        gc += self.window.preamble.text()
        # set Unit
        gc += " " +parent.commonGcode.getUnit()
    
        toolDia = float(self.window.toolDiameter.text())
        
        if parent.commonGcode.getPos():
            xoffset = float(self.window.centerX.text())    
            yoffset = float(self.window.centerY.text())
        else:
            # ignore user input
            X = xoffset = float(0.0)    
            Y = yoffset = float(0.0)
        
        intend = "".ljust(2)
        # X
        #X = (float(self.__dia.get()) / 2.0) + xoffset
        X += xoffset
        # Y
        #Y = float(self.__centerY.get()) + yoffset
        Y += yoffset

        # I - this is the radius
        R = (float(self.window.arcDiameter.text()) / 2.0)
        I = R * -1.0

        # J
        J = -0.0

        # set Z axis to saftey
        gc += CR + "(set Z saftey position)" + CR
        gc += "G00 Z{0:08.3f} F{1:05.1f} {2}".format(
            float(self.window.zSafe.text()), float(self.window.speedZ.text()), CR)

        # set start postion X/Y
        # for milling an arc, we move to 3clock position and start from
        # this position.
        # if cutter compensation is used please remember:
        #   G41 is LEFT from path
        #   G42 is RIGHT from path
        #
        #   Our start position is at 3-clock. If G41 is used, tool is inside
        #   arc (circle)
        #   if G42 is used, tool is outside of arc (circle)
        #
        #   this behaviour depends on general turn (CW or CCW)
        #   CW => above behaviour
        #   CCW => G41 is RIGHT, G42 is LEFT
        #
        #
        gc += "G00 X{0:08.3f} Y{1:08.3f} F{2:05.1f} {3}".format(
            float(X + R), float(Y), float(self.window.speedXY.text()), CR)

        # cutter compensation
        #
        gc += parent.commonGcode.getGCodeCutterComp(
            parent.commonGcode.getCompensation(), x=(X + R), y=Y, toolDia=toolDia)

        # set to Z-start position
        gc += CR + "(move Z-axis to start postion near surface)" + CR
        gc += "G01 Z{0:08.3f} F{1:05.1f} {2}".format(
            float(self.window.startZ.text()), float(self.window.speedZg1.text()), CR)

        # start with circel
        #
        # generate as many circle steps as needed until depthtotal is reached
        # cut an Arc
        step = float(self.window.depthStep.text())
        depth = float(self.window.depthTotal.text())
        z = 0.0
        loop = ""
        gc += CR + "(-- START circel --)" + CR
        gc += "(-- Dia {0:06.3f}, Depth {1:06.3f}, Step Z {2:06.3f} --){3}".format(
            float(toolDia), depth, step, CR)
        gc += "(-- X {0:06.3f}, Y {1:06.3f} --) {2}".format(
            float(X + R), float(Y), CR)
        gc += "(-- LOOP --)" + CR + CR
        while (abs(z) < abs(depth)):
            # set next Z depth
            if ((abs(depth) - abs(z)) < abs(step)):
                # this happens, if a small amount is the rest
                z -= (abs(depth) - abs(z))
                print("rest Z: {}".format(z))
            else:
                z -= abs(step)
                print( "new Z: {}".format(z))

            loop += intend + "(set new Z {0:05.2f} position)".format(z) + CR
            loop += intend + "G01 Z{0:08.3f} F{1:05.1f} {2}".format(
                float(z), float(self.window.speedZ.text()), CR)
            # set direction G02/G03
            #
            loop += intend + parent.commonGcode.getDir()
            loop += " X{0:08.3f} Y{1:08.3f} I{2:08.3f} J{3:08.3f} F{4:05.1f} {5}".format(
                X + R, Y, I, J, float(self.window.speedG2G3.text()), CR)
            loop += CR
            #
            # for saftey issues.
            if (abs(step) == 0.0):
                break
            pass

        gc += loop
        #----------------------------
        gc += CR + "(-- END circle -)" + CR
        gc += parent.commonGcode.getGCode_Homeing(X, Y, float(self.window.zSafe.text()),
                                    float(self.window.speedXY.text()),
                                    float(self.window.speedZ.text())) + CR
        gc += self.window.postGcode.text()
        gc += CR
        
        return gc    
    
    
    
