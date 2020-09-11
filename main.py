# This Python file uses the following encoding: utf-8
import sys
import os
import json


from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QFile, QSettings
from PyQt5 import uic

from GcodeWindow import GcodeWindow
from CommonGcode import CommonGcode

class GCodeGenerator(QMainWindow):
    def __init__(self):
        super(GCodeGenerator, self).__init__()
        
        self.settings = QSettings("GCodeGenerator","GcodeConfig")
        self.settings.setDefaultFormat(QSettings.IniFormat)
        
        
        self.materialFile = "millingparameters.json"
        
        self.load_ui()
        self.init_Material()
        if len(self.settings.allKeys()) > 0:
            self.init_settings()
        
        self.toolBoxObj = None
        
        
                
        self.gcValues = {
            'mm'  : 'G21',
            'inch': 'G20',
            'trcr': 'G42',    #Tool Radius Compensation Right
            'trcl': 'G41',    #Tool Radius Compensation Left
            'trc' : 'G40',    #Tool Radius Compensation on (disables G41/G42)
            }
        
        self.window.toolBox.currentChanged.connect(self.onTabBarClicked)
        tbIdx = self.window.toolBox.currentIndex()
        self.window.toolBox.currentChanged.emit(tbIdx)
        self.gcodeWidget = GcodeWindow(self)
        self.commonGcode = CommonGcode(self)
        self.window.pb_gCode.clicked.connect(self.onGCodeClicked)
        
        self.window.toolBox_Pocket.currentChanged.connect(self.onPocketToolChanged)
        self.window.toolBox_Pocket.currentChanged.emit(0)

    def load_ui(self):
        #loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        #self.window = loader.load(ui_file, self)
        self.window = uic.loadUi(ui_file)
        ui_file.close()
        self.window.actionGCode_Pre_Post.triggered.connect(self.onActionGCode_Pre_Post)
        self.window.actionMaterial.triggered.connect(self.onActionMaterial)
        self.window.actionMachine_Params.triggered.connect(self.onActionMachineParams)
        
        self.window.actionGCode_Pre_Post.triggered.emit()
        self.window.actionMaterial.triggered.emit()
        self.window.actionMachine_Params.triggered.emit()
        
        
        
    def write_settings(self):
        self.settings.setValue("Preamble",self.window.preamble.text())
        self.settings.setValue("PostGcode",self.window.postGcode.text())
        self.settings.setValue("Material",self.window.cbMaterial.currentIndex())
        self.settings.setValue("Materials",self.window.cbMaterials.currentIndex())
        self.settings.setValue("ToolId",self.window.toolId.text())
        self.settings.setValue("SpindleSpeed",self.window.spindleSpeed.text())
        if self.window.dirCCW.isChecked():
            self.settings.setValue("Direction_CCW",1)
            self.settings.setValue("Direction_CW",0)
        elif self.window.dirCW.isChecked():
            self.settings.setValue("Direction_CW",1)
            self.settings.setValue("Direction_CCW",0)
        
        if self.window.unitMm.isChecked():
            self.settings.setValue("Unit_mm",1)
            self.settings.setValue("Unit_inch",0)
        elif self.window.unitInch.isChecked():
            self.settings.setValue("Unit_inch",1)
            self.settings.setValue("Unit_mm",0)
        
        self.settings.setValue("Speed_XY",self.window.speedXY.text())
        self.settings.setValue("Speed_Z",self.window.speedZ.text())
        self.settings.setValue("ToolDiameter",self.window.toolDiameter.text())
        self.settings.setValue("StartZ",self.window.startZ.text())
        self.settings.setValue("SafeZ",self.window.zSafe.text())
        self.settings.setValue("Speed_G2G3",self.window.speedG2G3.text())
        self.settings.setValue("Speed_Zg1",self.window.speedZg1.text())
        self.settings.setValue("Center_X",self.window.centerX.text())
        self.settings.setValue("Center_Y",self.window.centerY.text())
        self.settings.setValue("DepthTotal",self.window.depthTotal.text())
        self.settings.setValue("DepthStep",self.window.depthStep.text())
    
    def init_settings(self):
        #print(self.settings.fileName())
        #print(len(self.settings.allKeys()))
        self.window.preamble.setText(self.settings.value("Preamble"))
        self.window.postGcode.setText(self.settings.value("PostGcode"))
        self.window.cbMaterial.setCurrentIndex(int(self.settings.value("Material")))
        self.window.cbMaterials.setCurrentIndex(int(self.settings.value("Materials")))
        self.window.toolId.setText(self.settings.value("ToolId"))
        self.window.spindleSpeed.setText(self.settings.value("SpindleSpeed"))
        self.window.dirCCW.setChecked(bool(self.settings.value("Direction_CCW")))
        self.window.dirCW.setChecked(bool(self.settings.value("Direction_CW")))
        self.window.unitMm.setChecked(bool(self.settings.value("Unit_mm")))
        self.window.unitInch.setChecked(bool(self.settings.value("Unit_inch")))
        self.window.speedXY.setText(self.settings.value("Speed_XY"))
        self.window.speedZ.setText(self.settings.value("Speed_Z"))
        self.window.toolDiameter.setText(self.settings.value("ToolDiameter"))
        self.window.startZ.setText(self.settings.value("StartZ"))
        self.window.zSafe.setText(self.settings.value("SafeZ"))
        self.window.speedG2G3.setText(self.settings.value("Speed_G2G3"))
        self.window.speedZg1.setText(self.settings.value("Speed_Zg1"))
        self.window.centerX.setText(self.settings.value("Center_X"))
        self.window.centerY.setText(self.settings.value("Center_Y"))
        self.window.depthTotal.setText(self.settings.value("DepthTotal"))
        self.window.depthStep.setText(self.settings.value("DepthStep"))
        
        

    def init_Material(self):
        with open(self.materialFile, "r") as read_file:
            self.dicMaterials = json.load(read_file)
        
        for (cat,v) in self.dicMaterials.items():
            self.window.cbMaterial.addItem(cat)
        
        self.window.cbMaterial.currentIndexChanged.connect(self.onMaterialChanged)
        self.window.cbMaterials.currentIndexChanged.connect(self.onMaterialsChanged)
        matIdx = self.window.cbMaterial.currentIndex()
        self.window.cbMaterial.currentIndexChanged.emit(matIdx)
    
    def onActionGCode_Pre_Post(self):
        if self.window.frame_Gcode.isVisible():
            self.window.frame_Gcode.hide()
        else:
            self.window.frame_Gcode.show()

    def onActionMaterial(self):
        if self.window.frame_Material.isVisible():
            self.window.frame_Material.hide()
        else:
            self.window.frame_Material.show()
    
    
    def onActionMachineParams(self):
        
        if self.window.groupBoxDirection.isVisible():
            self.window.groupBoxDirection.hide()
            print("machine")
        else:
            self.window.groupBoxDirection.show()
        
    #Slot int
    def onTabBarClicked(self,idx):
        if idx == 0:
            from ContourArc import ContourArc
            contourArc = ContourArc(self)
            self.toolBoxObj = contourArc
        elif idx == 1:
            from ContourRect import ContourRectangle
            contourRect = ContourRectangle(self)
            self.toolBoxObj = contourRect
        elif idx == 2:
            from ContourRoundRect import ContourRoundRectangle
            contourRRect = ContourRoundRectangle(self)
            self.toolBoxObj = contourRRect
    
    def onPocketToolChanged(self,idx):
        if idx == 0:
            from PocketCircle import PocketCircle
            pocketCircle = PocketCircle(self)
            self.toolBoxObj = pocketCircle
           
    
    def onMaterialChanged(self, idx):
        material = self.window.cbMaterial.currentText()
        #print(material)
        with open(self.materialFile, "r") as read_file:
            self.dicMaterials = json.load(read_file)
        
        self.window.cbMaterials.clear()
        
        for item in self.dicMaterials[material]:
            self.window.cbMaterials.addItem(item["Material"])
            #print(item["Material"])
        
    def onMaterialsChanged(self, idx):
        material = self.window.cbMaterial.currentText()
        materials = self.window.cbMaterials.currentText()
        #print(material, " ",materials)
        for item in self.dicMaterials[material]:
            
            if item["Material"] == materials:
                self.window.toolId.setText( str(item["ToolID"]))
                self.window.spindleSpeed.setText( str(item["Spindel-RPM"]))
        
    def onGCodeClicked(self):
        
        self.gcodeWidget.dialog.gcodeText.clear()  
        self.gcodeWidget.dialog.gcodeText.appendPlainText(self.commonGcode.getGCode(self))
        self.gcodeWidget.show()
    

if __name__ == "__main__":
    app = QApplication([])
    widget = GCodeGenerator()
    app.aboutToQuit.connect(widget.write_settings)
    widget.window.show()
    sys.exit(app.exec_())
