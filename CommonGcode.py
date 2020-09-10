import sys

CR="\n"

class CommonGcode():
    def __init__(self,parent):
        
        self._standardGCodeSeq = {
            "HOMEING": [
                "G00 Z{0:08.3f} F{1:05.1f} {2}",
                "G00 X{0:08.3f} Y{1:08.3f} F{2:05.1f} {3}"
            ],
            "SPINDLE_CW": ["M3 S{0:08.4f} {1}"],
            "SPINDLE_CCW": ["M4 S{0:08.4f} {1}"],
            "TOOL": ["T{0:03d} {1}M6 {1}"],
            "PREAMBLE": ["G90 G64 G17 G40 G49 {0}"],
            "POSTAMBLE": ["G00 Z10 F100 M2 {0}"],
            "ZAXIS": [3.0, 10.0],
            "TRAVEL_SPEEDXYZ": ["500", "500", "400"],  #[X,Y,Z]
        }
            
        self.window = parent.window
        self.parent = parent
        
    def getUnit(self):
        
        if self.window.unitMm.isChecked():
            return self.parent.gcValues["mm"]
        elif self.window.unitInch.isChecked():
            return self.parent.gcValues["inch"]
        else:
            return False
        
    
    def getPos(self):
        if self.window.rbCP_5.isChecked():
            return False
        else:
            return True
    
    def getCompensation(self):
        if self.window.rbTrc.isChecked():
            return self.parent.gcValues["trc"]
        elif self.window.rbTrcl.isChecked():
            return self.parent.gcValues["trcl"]
        elif self.window.rbTrcr.isChecked():
            return self.parent.gcValues["trcr"]
    
    def getDir(self):
        if self.window.dirCW.isChecked():
            return "G2"
        elif self.window.dirCCW.isChecked():
            return "G3"   
    
    
    
    def getGCodeCutterComp(self, compensation="G40", toolDia=0.0, x=0.0,
                           y=0.0):
        '''
        return a GCode for given cutter compensation

        This cutter compensation do not use tool table adjustment for
        tool diameters.

        if toolDia is not set (0.0) than preset tool diameter is used

        # if cutter compensation is used please remember:
        #   G41 is LEFT from path
        #   G42 is RIGHT from path
        #
        #   if our start position is at 3-clock and G41 is used, tool is inside
        #   arc (circle), because we should start LEFT from path.
        #
        #   if G42 is used, tool is outside of arc (circle) (RIGHT)
        #
        #   this behaviour depends on general contour direction (CW or CCW)
        #   CW => above behaviour
        #   CCW => G41 is RIGHT, G42 is LEFT

        '''
        gc = ""
        #if toolDia == 0.0:
        #    compensation = "G40"

        gc += "(-- cutter compensation --)" + CR
        if (compensation == "G41"):
            if toolDia == 0.0:
                gc += "G41 {1}".format(CR)
            else:
                gc += "G41.1 D{0:05.2f} X{2:08.3f} Y{3:08.3f}{1}".format(
                    toolDia, CR, x, y)
                #gc += "G41.1 D{0:05.2f}{1}".format(toolDia, CR)
        elif (compensation == "G42"):
            if toolDia == 0.0:
                gc += "G42 {1}".format(CR)
            else:
                gc += "G42.1 D{0:05.2f} X{2:08.3f} Y{3:08.3f}{1}".format(
                    toolDia, CR, x, y)
                #gc += "G42.1 D{0:05.2f}{1}".format(toolDia, CR)
        else:  # G40
            gc += "G40 {0}".format(CR)
        return gc
    
   
        
    def saveFile(self, event=None):
        gc = self.getGCode()
        if gc is None:
            return None
        fname = tkFileDialog.asksaveasfilename(
            initialdir="./",
            title="Save file",
            defaultextension="*.ngc",
            filetypes=(("Axis ", "*.ngc"), ("Gcode ", "*.gcode"), ("all files",
                                                                   "*.*")))
        if (fname == None):
            # cancle button
            return None
        print("Save gcode to '{}'".format(fname))
        f = open(fname, "w")
        f.write(gc)
        f.close()
    
    def copyConsole(self, event=None):
        print("---------------- copyConsole -----------------")
        gc = self.getGCode()
        if gc is None:
            return None
        sys.stdout.write(self.getGCode())
    
    def getGCode(self,parent):
        
        gc = "%"
        #
        # removed because some trouble with GCode-Interpreters (BK-13.12.2018)
        gc += '''
; (--------------------------)
; (          __              )
; (  _(\    |@@|             )
; ( (__/\__ \--/ __          )
; (    \___|----|  |   __    )
; (        \ }{ /\ )_ / _\   )
; (        /\__/\ \__O (__   )
; (       (--/\--)    \__/   )
; (       _)(  )(_           )
; (      `---''---`          )
; (    (c) by LunaX 2018     )
; (--------------------------)
         '''
        gc += CR
        gc += parent.toolBoxObj.generateGCode(parent)
        
        gc += "%" + CR
        return gc
    
    def getGCode_Homeing(self, x=0, y=0, z=10, fxy=100, fz=100):
        gc = "(HOMEING)" + CR
        gc += self._standardGCodeSeq["HOMEING"][0].format(z, fz, CR)
        gc += self._standardGCodeSeq["HOMEING"][1].format(x, y, fxy, CR)
        return gc
