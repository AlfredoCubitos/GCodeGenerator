from PyQt5.QtGui import QPixmap
from math import *
import os, re

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
class PocketCircle():

    #
    # define your own images to describe your GCode-Generator
    def __init__(self, parent):
        path = os.getcwd()
        
        self.__imageNames = [
            # left down
            path + "/img/pocket/PocketCircle.005.png"
        ]
        
        self.parent = parent
        self.window = parent.window

  
    
    #-------------------------------------------------------------
    # here you generate your GCode.
    # some of this code should be used every time.
    # insert your code bettween marked rows
    #-------------------------------------------------------------
    def generateGCode(self, parent):
        '''
        for a pocket in an rounded rectangle, even what user set as reference point, we
        recalculate it to inner contour and start with milling on outer line
        of this contour until we touch outer line contour
        '''
        cPoint = (float(self.window.centerX.text()), float(self.window.centerY.text()))
        radii = (float(self.window.outerRadius.text()),
                 float(self.window.innerRadius.text()))

        toolDia = float(self.window.toolDiameter.text())

        stepover = float(self.window.stepOver.text())
        stepover = round(toolDia - (float(toolDia * stepover) / 100), 1)

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

        # we do not use G41/G42 ! - we calculate it for G02 vecorts
        # we start with inner contour and from this ContourRect
        # left outside - in this case we have an offset of half tool dia
        offset = toolDia / 2.0
        toPosition = radii[0] - radii[1]
        currentPosition = offset
        pocketMillTracks = []
        x = 1
        finished = False
        #
        # start at "3 a clock" position
        cPoint = (cPoint[0] + radii[0], cPoint[1])
        while (not finished):
            print(
                "cPointX {} oRadius {} iRadius {} toPosition {} currentPosition {}"
                .format(cPoint[0], radii[0], radii[1], toPosition,
                        currentPosition))
            if (currentPosition + (toolDia / 2.0) >= toPosition):
                # oh, we over shot, we have to reduce offset to a value
                # which is the difference between width - currentPosition
                currentPosition += (toPosition - currentPosition) - (
                    toolDia / 2.0)
                # this is our last track
                finished = True


#    def __createPocketTracks(self, cPoint, r, feeds, depth, offset=0.0 ):
            t = self.__createPocketTracks(
                cPoint,
                radii[0],  # outer radius
                feeds,
                z,
                currentPosition)
            pocketMillTracks.append(t)
            x += 1
            currentPosition += stepover

        #
        # it's time to generate the real gCode
        #
        # Every round we mill all tracks in the same detph
        # than we increase depth as long as we reached total depthStep

        gc += CR + "(-- START DEPTH Loop --)" + CR
        z = 0.0
        while (abs(z) < abs(depth[0])):
            # set next Z depth
            if ((abs(depth[0]) - abs(z)) < abs(depth[1])):
                # this happens, if a small amount is the rest
                z -= (abs(depth[0]) - abs(z))
                print( "rest Z: {}".format(z))
            else:
                z -= abs(depth[1])
                print( "new Z: {}".format(z))

            loop += CR
            gc += spaces + "(-- START Track Loop  --)" + CR
            for t in pocketMillTracks:
                # every track contain a fixed number of separate gCode
                # commands
                spaces2 = spaces.ljust(2)
                # set new depth
                gc += CR + spaces2 + "(-- next depth z {0:08.3f} --){1}".format(
                    z, CR)
                for cmd in t:
                    #
                    # combine all parameter to one command
                    gc += spaces2
                    print( cmd)
                    #
                    # pattern to recognize special command set
                    regFloat = r"{\d:\d+\.\d+f}"
                    for p in range(len(cmd)):
                        if isinstance(cmd[p], str):
                            x = re.findall(regFloat, cmd[p], re.UNICODE)
                            if (len(x) != 0):
                                #print "RegFloat found"
                                gc += cmd[p].format(float(z))
                            else:
                                # normal string
                                gc += " " + cmd[p]
                        if isinstance(cmd[p], float):
                            gc += "{0:08.3f}".format(cmd[p])
                        if isinstance(cmd[p], int):
                            gc += "{0:05d}".format(cmd[p])
                    gc += CR

            gc += spaces + "(-- END Track Loop  --)" + CR
            pass

        gc += "(-- END DEPTH loop --)" + CR
        gc += parent.commonGcode.getGCode_Homeing(cPoint[0], cPoint[1], zPos["safetyZ"],
                                    feeds["XYG0"])
        gc += self.window.postGcode.text()
        gc += CR
        return gc

    def __createPocketTracks(self, cPoint, r, feeds, depth, offset=0.0):
        '''
        This method create for a track all needed GCode parameters and save
        them in a list. This list is used (afterwards) to create the real
        GCode commands

        This method is called in a loop with a new offset. The offset describes
        next millings position
        '''
        x = cPoint[0]
        y = cPoint[1]

        # sequence to mill a rounded rectangle
        seq = [
            #start
            ("G00", "X", x - offset, "Y", y, "F", feeds["XYG0"]),
            # G01 Zxxx Fyyy
            (
                "G01",
                "Z",
                "{0:08.3f}",
                "F",
                feeds["ZGn"],
            ),
            # G02, F X Y I
            ("G02", "I", -(r - offset), "F", feeds["XYGn"]),
        ]
        #print "{1}---- offset {0} -----".format(offset,CR)
        #print seq
        return seq
