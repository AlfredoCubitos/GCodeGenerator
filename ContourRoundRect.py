from math import *
import os

from PyQt5.QtGui import QPixmap

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
            path + "/img/contour/round-rectangle-pic1_3.jpg",
            path + "/img/contour/round-rectangle-pic1_4.jpg",
            path + "/img/contour/round-rectangle-pic1_5.jpg",
        ]
        
        self.parent = parent
        self.window = parent.window
        self.centerPos = 0
        
        self.window.rbCPRR_1.clicked.connect(lambda clicked: self.onCenterPosChange(0))
        self.window.rbCPRR_2.clicked.connect(lambda clicked: self.onCenterPosChange(1))
        self.window.rbCPRR_3.clicked.connect(lambda clicked: self.onCenterPosChange(2))
        self.window.rbCPRR_4.clicked.connect(lambda clicked: self.onCenterPosChange(3))
        self.window.rbCPRR_5.clicked.connect(lambda clicked: self.onCenterPosChange(4))
        
        for i in range(1,6):
            obj = "rbCPRR_"+str(i)
            attr = getattr(self.window,obj)
            if attr.isChecked():
                attr.clicked.emit()
    
    def onCenterPosChange(self, pos):
        pixmap = QPixmap()
        if pixmap.load(self.__imageNames[pos]):
            self.window.imageRR.setPixmap(pixmap)
            self.centerPos = pos+1
        else:
            print("Image Load Error ", self.__imageNames[pos])
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
        cPoint = (float(self.window.centerX.text()), float(self.window.centerY.text()))
        sizeAB = (float(self.window.heightRA.text()), float(self.window.heightRB.text()))
        radius = float(self.window.edgeRadius.text())
        toolDia = float(self.window.toolDiameter.text())

        zPos = {
            "safetyZ": float(self.window.zSafe.text()),
            "startZ": float(self.window.startZ.text())
        }

        depth = (
            float(self.window.depthTotal.text()),
            float(self.window.depthStep.text())
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
        seq = [
            #start
            ("G01", feeds["XYGn"], x, y - offset),
            # arc1
            # G02, F X Y I J
            ("G02", feeds["XYGn"], x - r - offset, y + r, 0.0, r + offset),
            # vertical to arc2
            ("G01", feeds["XYGn"], x - r - offset, y + r + h1),
            # arc2
            # G02, F X Y I J
            ("G02", feeds["XYGn"], x, y + h0 + offset, r + offset, 0.0),
            # horizontal to arc 3
            ("G01", feeds["XYGn"], x + w1, y + h0 + offset),
            # arc 3
            # G02, F X Y I J
            ("G02", feeds["XYGn"], x + w1 + r + offset, y + r + h1, 0.0,
             -r - offset),
            # vertical to arc 4
            ("G01", feeds["XYGn"], x + w1 + r + offset, y + r),
            # arc 4
            # G02, G02, F X Y I J
            ("G02", feeds["XYGn"], x + w1, y - offset, -r - offset, 0.0),
            # go back to start position
            ("G01", feeds["XYGn"], x, y - offset),
        ]
        #print "{1}---- offset {0} -----".format(offset,CR)
        #print (seq)
        return seq
