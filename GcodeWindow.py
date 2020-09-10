import os

#from PySide2.QtWidgets import QDialog
#from PySide2.QtUiTools import QUiLoader
#from PySide2.QtCore import QFile

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QFile
from PyQt5 import uic

from CommonGcode import CommonGcode

class GcodeWindow(QDialog):
    def __init__(self, parent=None):
        super(GcodeWindow, self).__init__(parent)
        
        self.load_ui()
    
    def load_ui(self):
        #loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "dialog.ui")
        ui_file = QFile(path)
        if ui_file.open(QFile.ReadOnly):
            #self.dialog = loader.load(ui_file, self)
            self.dialog = uic.loadUi(ui_file)
            ui_file.close()
            self.dialog.pbClose.clicked.connect(self.close)
        else:
            print("Error: could not open dialog.ui")
    
    def show(self):
        self.dialog.show()
    
    def exec_(self):
        self.dialog.exec_()
    
    def close(self):
        self.dialog.gcodeText.clear()
        self.dialog.hide()
    #def copy(self):
    #    self.dialog.gcodeText.
    
   
