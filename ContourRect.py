import os
#from PySide2.QtGui import QPixmap
from PyQt5.QtGui import QPixmap

CR="\n"

class ContourRectangle():
    
    def __init__(self,parent):
        
        path = os.getcwd()
        self.__imageNames = [
                    # left down
            path + "/img/contour/rectangle-pic1_1.jpg",
            # left upper
            path + "/img/contour/rectangle-pic1_2.jpg",
            # right upper
            path + "/img/contour/rectangle-pic1_3.jpg",
            # right down
            path + "/img/contour/rectangle-pic1_4.jpg",
            # center
            path + "/img/contour/rectangle-pic1_5.jpg"
                ]
        self.parent = parent
        self.window = parent.window
        
        if self.window.cpRectangle.count() > 0:
            self.window.cpRectangle.clear()
            
        self.window.cpRectangle.addItems(["1","2","3","4","5","6","7","8","9"])
        
        self.window.cpRectangle.setCurrentIndex(8)
        ## direct connect to Fn does not work, so lambda is used
        self.window.cpRectangle.currentIndexChanged.connect(lambda idx: self.onCenterPosChange(idx))
        

    def onCenterPosChange(self, pos):
        if pos > 4:
            pos = 4
        
        pixmap = QPixmap()
        if pixmap.load(self.__imageNames[pos]):
            self.window.imageRect.setPixmap(pixmap)
        else:
            print("Image Load Error ", self.__imageNames[pos])
    
    def generateGCode(self, parent):
        cPoint = (float(self.window.centerX.text()), float(self.window.centerY.text()))
        zPos = {
            "safetyZ": float(self.window.zSafe.text()),
            "startZ": float(self.window.startZ.text())
        }

        sizeAB = (float(self.window.heightA.text()), float(self.window.heightB.text()))

        feeds = {
            "XYG0": float(self.window.speedXY.text()),
            "XYGn": float(self.window.speedG2G3.text()),
            "ZG0": float(self.window.speedZ.text()),
            "ZGn": float(self.window.speedZg1.text())
        }

        # X/Y
        cutterComp = (0.0, 0.0)

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

        # User used left down corner as CP
        if (int(self.window.cpRectangle.currentText()) == 1):
            cPoint = (float(self.window.centerX_Rect.text()), float(self.window.centerY_Rect.text()))
        # User used left upper corner as CP
        if (int(self.window.cpRectangle.currentText()) == 2):
            cPoint = (float(self.window.centerX_Rect.text()),
                      float(self.window.centerY_Rect.text()) - sizeAB[0])
        # User used right upper corner as CP
        if (int(self.window.cpRectangle.currentText()) == 3):
            cPoint = (float(self.window.centerX_Rect.text()) - sizeAB[1],
                      float(self.window.centerY_Rect.text()) - sizeAB[0])
        # User used right down corner as CP
        if (int(self.window.cpRectangle.currentText()) == 4):
            cPoint = (float(self.window.centerX_Rect.text()) - sizeAB[1],
                      float(self.window.centerY_Rect.text()))

        # object left down - this is our real center point
        if (int(self.window.cpRectangle.currentText()) == 5):
            cPoint = (0.0 - sizeAB[1], 0.0)
        # object left upper
        if (int(self.window.cpRectangle.currentText()) == 6):
            cPoint = (0.0, 0.0 - sizeAB[0])
        # object right upper
        if (int(self.window.cpRectangle.currentText()) == 7):
            cPoint = (0.0 - sizeAB[1], 0.0 - sizeAB[0])
        # object right down
        if (int(self.window.cpRectangle.currentText()) == 8):
            cPoint = (0.0 - sizeAB[1], 0.0)
        # object center
        if (int(self.window.cpRectangle.currentText()) == 9):
            print ("cc 9")
            cPoint = (0.0 - (sizeAB[1] / 2.0), 0.0 - (sizeAB[0] / 2.0))

        # cutter compensation
        if (parent.commonGcode.getCompensation() == "G40"):
            gc += CR + "(-- Cutter compensation --){}".format(CR)
            gc += "{} {}".format(parent.commonGcode.getCompensation(), CR)
            # nothing to do with cutterComp
            cutterComp = (0.0, 0.0)
        if (parent.commonGcode.getCompensation() == "G41"):
            gc += CR + "(-- Cutter compensation LEFT --){}".format(CR)
            gc += "{} {}".format(parent.commonGcode.getCompensation(), CR)
            cutterComp = (-(float(self.window.toolDiameter.text()) / 2.0),
                          -(float(self.window.toolDiameter.text()) / 2.0))
        if (parent.commonGcode.getCompensation() == "G42"):
            gc += CR + "(-- Cutter compensation RIGHT --){}".format(CR)
            gc += "{} {}".format(parent.commonGcode.getCompensation(), CR)
            cutterComp = ((float(self.window.toolDiameter.text()) / 2.0),
                          (float(self.window.toolDiameter.text()) / 2.0))

        #dir = int(self.__dir.get())
        #if (dir == 0):
        #    dirS = "CW"
        #else:
        #    dirS = "CCW"

        dirS = parent.commonGcode.getDir()
        cPoint = (
            cPoint[0] + cutterComp[0],
            cPoint[1] + cutterComp[1],
        )

        #
        # generate as many shape steps are needed until depthtotal is reached
        # cut an Arc
        step = float(self.window.depthStep.text())
        depth = float(self.window.depthTotal.text())
        z = 0.0
        loop = ""
        gc += CR + "(------- start shape -------------)" + CR
        gc += "(-- A {0:06.3f}, B {1:06.3f}, Depth {2:06.3f}, Step {3:06.3f} --){4}".format(
            sizeAB[0], sizeAB[1], depth, step, CR)
        gc += "(-- X {0:06.3f}, Y {1:06.3f} --) {2}".format(
            cPoint[0], cPoint[1], CR)
        # start with shape
        gc += CR + "(move Z-axis to start postion near surface)" + CR
        gc += "G00 Z{0:08.3f} F{1:05.1f} {2}".format(zPos["startZ"],
                                                     feeds["ZG0"], CR)

        # set start postion X/Y
        gc += CR + "(we allways start at lower left corner)" + CR
        gc += "G00 X{0:08.3f} Y{1:08.3f} F{2:05.1f} {3}".format(
            cPoint[0], cPoint[1], feeds["XYG0"], CR)

        #----------------------------------------------------------------------
        # This loop asume, that you try to mill into your object.
        # if not needed for your shape, remove this part and rewrite
        #----------------------------------------------------------------------
        #
        gc += CR + "(-- loop in {} --)".format(dirS) + CR
        gc += CR + "(-- Z {0:08.3f} --)".format(z) + CR
        # start with shape

        # set start postion X/Y
        while (abs(z) < abs(depth)):
            # set next Z depth
            if ((abs(depth) - abs(z)) < abs(step)):
                # this happens, if a small amount is the rest
                z -= (abs(depth) - abs(z))
                print ("rest Z: {}".format(z))
            else:
                z -= abs(step)
                print ("new Z: {}".format(z))

            #
            # start with this start position
            #loop += self.__createGCodeRect(dir, X,Y,Z,a,b)
            loop += self.__createGCodeRect(dir, cPoint, z, sizeAB, feeds)
            #---------------------------------------------------
            # indiviual GCode - END
            #---------------------------------------------------
            #
            # for saftey issues.
            if (abs(step) == 0.0):
                break

        gc += loop
        #----------------------------
        gc += "(----------------------------------)" + CR
        gc += parent.commonGcode.getGCode_Homeing(0, 0, zPos["safetyZ"], feeds["XYG0"])
        gc += self.window.postGcode.text()
        gc += CR
        return gc

    def __createGCodeRect(self, dir, cPoint, z, sizeAB, feeds):
        gc = ""
        gc += CR + "(set new Z {0:05.2f} position)".format(z) + CR
        gc += "G00 Z{0:08.3f} F{1:05.1f} {2}".format(
            float(z), feeds["ZGn"], CR)

        # Positions
        # 2-------------3
        # |             |
        # |             |
        # |             |
        # 1-------------4
        # start is #1
        millPos = {
            "#1":
            "G01 X{0:08.3f} Y{1:08.3f} Z{2:08.3f} F{3:05.1f} {4}".format(
                cPoint[0], cPoint[1], z, feeds["XYGn"], CR),
            "#2":
            "G01 X{0:08.3f} Y{1:08.3f} Z{2:08.3f} F{3:05.1f} {4}".format(
                cPoint[0], cPoint[1] + sizeAB[0], float(z), feeds["XYGn"], CR),
            "#3":
            "G01 X{0:08.3f} Y{1:08.3f} Z{2:08.3f} F{3:05.1f} {4}".format(
                cPoint[0] + sizeAB[1], cPoint[1] + sizeAB[0], float(z),
                feeds["XYGn"], CR),
            "#4":
            "G01 X{0:08.3f} Y{1:08.3f} Z{2:08.3f} F{3:05.1f} {4}".format(
                cPoint[0] + sizeAB[1], cPoint[1], float(z), feeds["XYGn"], CR)
        }
        # start on #1
        gc += millPos["#1"]
        # to #2 / #4
        if (dir == 0):
            # CW
            gc += millPos["#2"]
        else:
            # CCW
            gc += millPos["#4"]

        # to #3 / #3
        if (dir == 0):
            # CW
            gc += millPos["#3"]
        else:
            # CCW
            gc += millPos["#3"]

        # to #4 / #2
        if (dir == 0):
            # CW
            gc += millPos["#4"]
        else:
            # CCW
            gc += millPos["#2"]

        # back on #1
        gc += millPos["#1"]

        return gc
        
    
    
    
    
    
