import os

from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5 import QtGui
from PyQt5.QtCore import QBuffer

CR="\n"

class ContourArc():
    
    def __init__(self,parent):
        
        path = os.getcwd()
        self.__imageNames = [
                    
                    path + "/img/contour/circle-pic1_1.jpg",
                    path + "/img/contour/circle-pic1_2.jpg"
                ]
        self.parent = parent
        self.window = parent.window
        self.buffer = QBuffer()
        ## use lambda to pass extra parameter to the Signal function
        
        self.window.rbCP_1.clicked.connect(lambda clicked: self.onCenterPosChange(0))
        self.window.rbCP_2.clicked.connect(lambda clicked: self.onCenterPosChange(1))
        
        self.window.rbTrc.clicked.connect(lambda clicked: self.onToolMoveChanged("on"))
        self.window.rbTrcl.clicked.connect(lambda clicked: self.onToolMoveChanged("left"))
        self.window.rbTrcr.clicked.connect(lambda clicked: self.onToolMoveChanged("right"))
        
        self.window.hSliderArcStart.valueChanged.connect(self.onArcStart)
        self.window.hSliderArcEnd.valueChanged.connect(self.onArcEnd)
        
        self.window.hSliderArcStart.sliderReleased.connect(self.onSliderReleased)
        self.window.hSliderArcEnd.sliderReleased.connect(self.onSliderReleased)
        
                
        self.arcPix = False
        self.pixmap = QPixmap()
        self.painter = QPainter()
        
        for i in range(1,3):
            obj = "rbCP_"+str(i)
            attr = getattr(self.window,obj)
            if attr.isChecked():
                attr.clicked.emit()
        
        self.updateMillTool()
        
        
        
    def updateMillTool(self):
        
        if self.window.rbTrc.isChecked():
            self.window.rbTrc.clicked.emit()
        elif self.window.rbTrcl.isChecked():
            self.window.rbTrcl.clicked.emit()
        elif self.window.rbTrcr.isChecked():
            self.window.rbTrcr.clicked.emit()
    
    def updatePosForm(self,boolean):
        self.window.centerX.setEnabled(boolean)
        self.window.centerY.setEnabled(boolean)
        self.window.label_X.setEnabled(boolean)
        self.window.label_Y.setEnabled(boolean)
        
    
    def onCenterPosChange(self, pos):
        if self.pixmap.load(self.__imageNames[pos]):
            self.window.image.setPixmap(self.pixmap)
            self.drawCenterPos(pos)
        else:
            print("Image Load Error ", self.__imageNames[pos])
    
    def onToolMoveChanged(self,pos):
        self.arcPix = False
        self.window.hSliderArcStart.setValue(0)
        self.window.hSliderArcEnd.setValue(0)
        if pos == "on":
            self.drawMiller(40)
        elif pos == "right":
            self.drawMiller(20)
        elif pos == "left":
            self.drawMiller(60)
    
    def onArcStart(self,value):
        self.window.arcStart.setText(str(value)+".0")
    
    def onArcEnd(self,value):
        self.window.arcEnd.setText(str(value)+".0")
    
    def onSliderReleased(self):
        arcStart = self.window.hSliderArcStart.value()
        arcEnd = self.window.hSliderArcEnd.value()
        self.drawArc(arcStart,arcEnd)
    
          
    
    def drawCenterPos(self,pos):
        pen = QtGui.QPen()
        pen.setWidth(3)
        pen.setColor(QtGui.QColor('red'))
        pix = self.pixmap
        self.painter.begin(pix)
        self.painter.setPen(pen)
        
        
        if pos == 0:
            xh = 40
            yh = pix.height() -40
            self.painter.drawLine(xh-10,yh,xh+10,yh)
            self.painter.drawLine(xh,yh-10,xh,yh+10)
            self.updatePosForm(True)
 
        if pos == 1:
            xh = pix.width()/2
            yh = pix.height()/2
            self.painter.drawLine(xh-10,yh,xh+10,yh)
            self.painter.drawLine(xh,yh-10,xh,yh+10)
            self.updatePosForm(False)
        
        self.painter.end()
        self.window.image.update()
        self.updateMillTool()
        
        

    def drawMiller(self,pos):
        
        pen = QtGui.QPen()
        pen.setWidth(30)
        pen.setColor(QtGui.QColor('blue'))
        self.window.image.setPixmap(self.pixmap)
        pix = self.window.image.pixmap()    
        self.painter.begin(pix)
        self.painter.setPen(pen)
        self.painter.drawEllipse(pix.width()-pos,pix.height()/2,4,4)
        self.painter.end()
        self.window.image.update()
        
        #self.window.image.setPixmap(pix)
    
    def drawArc(self,start,end):
        pen = QtGui.QPen()
        pen.setWidth(3)
        pen.setColor(QtGui.QColor('black'))
        pix = QPixmap()
        if self.arcPix:
            pix.loadFromData(self.buffer.data())
        else:
            pix = self.window.image.pixmap()
            self.buffer.open(QBuffer.ReadWrite)
            pix.save(self.buffer,"PNG")
            self.arcPix = True
        self.painter.begin(pix)
        self.painter.setPen(pen)
        self.painter.drawArc(40,40,pix.width()-80,pix.height()-80,int(start*16),int(end*16))
        self.painter.end()
        self.window.image.setPixmap(pix)
   
        
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
    
    
    
