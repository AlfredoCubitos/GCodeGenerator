from math import *
import os

from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5 import QtGui
from PyQt5.QtCore import QBuffer, Qt

CR = "\n"


#----------------------------------------------------------------------------
#
# This class define your GCode generator
#
# It is a subclass from GeometricalFrame and provide a couple of functionalities
# like an image frame, a standard input entries frame, your "own" entries Frame
# and standard Buttons
#
# Copy this file into your your own file. Typical filenames are <kind shape>
# like ContourArc or ContourRect or PocketArc, ...
#
#
#
#----------------------------------------------------------------------------
class ContourRoundRectangle():

    #
    # define your own images to describe your GCode-Generator
    def __init__(self, parent):
        path = os.getcwd()
        

        self.__imageNames = [
            # left down
            path + "/img/contour/round-rectangle-pic1_1.jpg",
            path + "/img/contour/round-rectangle-pic1_2.jpg",
            
        ]
        
        self.parent = parent
        self.window = parent.window
        self.centerPos = 0
        
        self.window.rbCPRR_1.clicked.connect(lambda clicked: self.onCenterPosChange(0))
        self.window.rbCPRR_2.clicked.connect(lambda clicked: self.onCenterPosChange(1))
        
        self.window.rbTrcRRect.clicked.connect(lambda clicked: self.onToolMoveChanged("on"))
        self.window.rbTrclRRect.clicked.connect(lambda clicked: self.onToolMoveChanged("left"))
        self.window.rbTrcrrRect.clicked.connect(lambda clicked: self.onToolMoveChanged("right"))
        
        self.window.edgeRadius.editingFinished.connect(self.onEdgeRadiusChanged)
        
        self.arcPix = False
        self.buffer = QBuffer()
        self.pixmap = QPixmap()
        self.painter = QPainter()
        
        for i in range(1,3):
            obj = "rbCPRR_"+str(i)
            attr = getattr(self.window,obj)
            if attr.isChecked():
                attr.clicked.emit()
        
        self.updateMillTool()
        self.drawRoundedRect(1.0)
    
    def updateMillTool(self):
        
        if self.window.rbTrcRRect.isChecked():
            self.window.rbTrcRRect.clicked.emit()
        elif self.window.rbTrclRRect.isChecked():
            self.window.rbTrclRRect.clicked.emit()
        elif self.window.rbTrcrrRect.isChecked():
            self.window.rbTrcrrRect.clicked.emit()
    
    def updatePosForm(self,boolean):
        self.window.posRRX.setEnabled(boolean)
        self.window.posRRY.setEnabled(boolean)
        self.window.labelRRX.setEnabled(boolean)
        self.window.labelRRY.setEnabled(boolean)
    
    def onCenterPosChange(self, pos):
        if self.pixmap.load(self.__imageNames[pos]):
            self.window.imageRR.setPixmap(self.pixmap)
            self.drawCenterPos(pos)
        else:
            print("Image Load Error ", self.__imageNames[pos])
    
    def onToolMoveChanged(self,pos):
        self.arcPix = False
        if pos == "on":
            self.drawMiller(40)
        elif pos == "right":
            self.drawMiller(20)
        elif pos == "left":
            self.drawMiller(60)
    
    def onEdgeRadiusChanged(self):
        value = self.window.edgeRadius.text()
        self.drawRoundedRect(float(value))
    
    def drawRoundedRect(self,r):
        pen = QtGui.QPen()
        pen.setWidth(2)
        pen.setColor(QtGui.QColor('black'))
        pix = QPixmap()
        if self.arcPix:
            pix.loadFromData(self.buffer.data())
        else:
            pix = self.window.imageRR.pixmap()
            self.buffer.open(QBuffer.ReadWrite)
            pix.save(self.buffer,"PNG")
            self.arcPix = True
        self.painter.begin(pix)
        self.painter.setPen(pen)
        self.painter.drawRoundedRect(40,78,220,150,r,r)
        
        self.painter.end()
        self.window.imageRR.setPixmap(pix)
       # self.window.imageRR.update()
        
    
    def drawCenterPos(self,pos):
        pen = QtGui.QPen()
        pen.setWidth(3)
        pen.setColor(QtGui.QColor('red'))
        pix = QPixmap()
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
        
        self.updateMillTool()
    
    def drawMiller(self,pos):
        pen = QtGui.QPen()
        pen.setWidth(30)
        pen.setColor(QtGui.QColor('blue'))
        self.window.imageRR.setPixmap(self.pixmap)
        pix = self.window.imageRR.pixmap()    
        self.painter.begin(pix)
        self.painter.setPen(pen)
        self.painter.drawEllipse(pix.width()-pos,pix.height()/2,4,4)
        self.painter.end()
        self.window.image.update()
        self.window.edgeRadius.editingFinished.emit()
    #-------------------------------------------------------------
    # here you generate your GCode.
    # some of this code should be used every time.
    # insert your code bettween marked rows
    #-------------------------------------------------------------
    def generateGCode(self, parent):
        '''
        generate GCode for a rounded rectangle.
        This class is copied from pocketRoundRectangle. Some unnessesary
        code are removed. Some parts are new (cutter compensation)
        '''
        print("ContourRoundRect")
        cPoint = (float(self.window.posRRX.text()), float(self.window.posRRY.text()))
        sizeAB = (float(self.window.heightRA.text()), float(self.window.heightRB.text()))
        radius = float(self.window.edgeRadius.text())
        toolDia = float(self.window.toolDiameter.text())

        zPos = {
            "safetyZ": float(self.window.zSafe.text()),
            "startZ": float(self.window.startZ.text())
        }

        depth = (
            float(self.window.depthRRTotal.text()),
            float(self.window.depthRRStep.text())
        )

        dir = parent.commonGcode.getDir()

        feeds = {
            "XYG0": float(self.window.speedXY.text()),
            "XYGn": float(self.window.speedG2G3.text()),
            "ZG0": float(self.window.speedZ.text()),
            "ZGn": float(self.window.speedZg1.text())
        }
        gc = ""
        gc += self.window.preamble.text()
        # set Unit
        gc += parent.commonGcode.getUnit() + CR
        # set Z axis
        gc += CR + "(set Z saftey position)" + CR
        gc += "G00 Z{0:08.3f} F{1:05.1f} {2}".format(zPos["safetyZ"],
                                                     feeds["ZG0"], CR)

        #
        # even which center point user choosed, we start on
        # center point object - left down (5)
        
        if self.centerPos == 5:
            cPoint = (0.0 - (sizeAB[1] / 2.0), 0.0 - (sizeAB[0] / 2.0))

        # set start postion X/Y
        gc += CR + "(set center position)" + CR
        gc += "G00 X{0:08.3f} Y{1:08.3f} F{2:05.1f} {3}".format(
            cPoint[0], cPoint[1], feeds["XYG0"], CR)
        #
        # generate as many shape steps are needed until depthtotal is reached
        # cut an Arc
        step = depth[1]
        #        depth = float(self.__depthtotal.get())
        z = step
        loop = ""
        gc += CR + "(------- start shape -------------)" + CR

        # start with shape
        gc += CR + "(move Z-axis to start postion near surface)" + CR
        gc += "G00 Z{0:08.3f} F{1:05.1f} {2}".format(zPos["startZ"],
                                                     feeds["ZG0"], CR)
        spaces = "".ljust(2)
        #----------------------------------------------------------------------
        # This loop asume, that you try to mill into your object.
        # if not needed for your shape, remove this part and rewrite
        #----------------------------------------------------------------------
        #

        pocketMillTracks = []
        x = 1
        t = self.__createPocketTracks(
            cPoint,
            sizeAB,
            radius,
            feeds,
            0.0  # no offset, milling only one time !
        )
        
        pocketMillTracks.append(t)
        #gc += self.getGCodeCutterComp(self.__cuttercompensation.get(), toolDia)
        gc += parent.commonGcode.getGCodeCutterComp( parent.commonGcode.getCompensation(), toolDia)

        #
        # it's time to generate the real gCode
        #
        # Every round we mill all tracks in the same detph
        # than we increase depth as long as we reached total depthStep

        gc += CR + "(-- START DEPTH Loop --)" + CR
        z = depth[1]
        
        while (abs(z) < abs(depth[0])):
            # set next Z depth
            print("Z: ",abs(z)," MaxD: ",abs(depth[0]))
            if ((abs(depth[0]) - abs(z)) < abs(depth[1])):
                # this happens, if a small amount is the rest
                z -= (abs(depth[0]) - abs(z))
                print( "rest Z: ", z)
            else:
                z -= abs(depth[1])
                print( "new Z: ",z)

            loop += CR
            gc += spaces + "(-- START Track Loop  --)" + CR
            
            for t in pocketMillTracks:
                # every track contain a fixed number of separate gCode
                # commands
                print(t)
                spaces2 = spaces.ljust(2)
                # set new depth
                gc += CR + spaces2 + "(-- next depth z {0:08.3f} --){1}".format(
                    z, CR)
                gc += spaces2 + "G01 Z{0:08.3f} {1}".format(z, CR)
                for cmd in list(t):
                    #
                    # combine all parameter to one command
                    gc += spaces2
                    #  0  1  2  3  4
                    # GC, X, Y, I, J
                    print( cmd)
                    for p in range(len(cmd)):
                        if p == 0:
                            gc += cmd[p]
                        if p == 1:
                            f = " F{0:05.1f}".format(float(cmd[p]))
                        if p == 2:
                            gc += " X{0:08.3f}".format(float(cmd[p]))
                        if p == 3:
                            gc += " Y{0:08.3f}".format(float(cmd[p]))
                        if p == 4:
                            gc += " I{0:08.3f}".format(float(cmd[p]))
                        if p == 5:
                            gc += " J{0:08.3f}".format(float(cmd[p]))

                    gc += f + CR

            gc += spaces + "(-- END Track Loop  --)" + CR
            pass

        gc += "(-- END DEPTH loop --)" + CR
        gc += parent.commonGcode.getGCode_Homeing(cPoint[0], cPoint[1], zPos["safetyZ"], feeds["XYG0"])
        gc += self.window.postGcode.text()
        gc += CR
        return gc

    def __createPocketTracks(self, cPoint, sizeAB, r, feeds, offset=0.0):
        '''
        This method create for a track all needed GCode parameters and save
        them in a list. This list is used (afterwards) to create the real
        GCode commands

        This method is called in a loop with a new offset. The offset describes
        next millings position
        '''
        # h = h1 + 2*r
        # w = w1 + 2*r
        w0 = sizeAB[1]
        w1 = sizeAB[1] - (2 * r)  # horizontal distance between arcs
        h0 = sizeAB[0]
        h1 = sizeAB[0] - (2 * r)  # vertical distance betwween arcs

        x = cPoint[0]
        y = cPoint[1]
        # sequence to mill a rounded rectangle
        seq = []
            #start
        seq.append(("G01", feeds["XYGn"], x, y - offset))
            # arc1
            # G02, F X Y I J
        if r > 0:
            seq.append(("G02", feeds["XYGn"], x - r - offset, y + r, 0.0, r + offset))
            # vertical to arc2
            
        seq.append(("G01", feeds["XYGn"], x - r - offset, y + r + h1))
            # arc2
            # G02, F X Y I J
        if r > 0:
            seq.append(("G02", feeds["XYGn"], x, y + h0 + offset, r + offset, 0.0))
            # horizontal to arc 3
        seq.append(("G01", feeds["XYGn"], x + w1, y + h0 + offset))
            # arc 3
            # G02, F X Y I J
        if r > 0:
            seq.append(("G02", feeds["XYGn"], x + w1 + r + offset, y + r + h1, 0.0, -r - offset))
            # vertical to arc 4
        seq.append(("G01", feeds["XYGn"], x + w1 + r + offset, y + r))
            # arc 4
            # G02, G02, F X Y I J
        if r > 0:
            seq.append(("G02", feeds["XYGn"], x + w1, y - offset, -r - offset, 0.0))
            # go back to start position
        seq.append(("G01", feeds["XYGn"], x, y - offset))
        
        #print "{1}---- offset {0} -----".format(offset,CR)
        #print (seq)
        return seq
