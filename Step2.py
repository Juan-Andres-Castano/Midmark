import time
from PySide6.QtCore import Qt
from PySide6.QtCore import * #Qt
from PySide6.QtWidgets import QApplication, QMainWindow,QMessageBox,QDialog
import re

class Step2(QMainWindow):
    myInstructionSignal = Signal(str)
    
    def __init__(self, parent =None):
        super(Step2,self).__init__(parent)
        
    def trigger_test2(self,param):
      #  time.sleep(2)   
        print("triggered step ",param)
        self.myInstructionSignal.emit("text for test2")