import time
from PySide6.QtCore import Qt
from PySide6.QtCore import * #Qt
from PySide6.QtWidgets import QApplication, QMainWindow,QMessageBox,QDialog
import re

class Step1(QMainWindow):
    myInstructionSignal = Signal(str)
    
    def __init__(self, parent =None):
        super(Step1,self).__init__(parent)
        
    def trigger_test1(self,param):
      #  time.sleep(2)   
        print("triggered step ",param)
        self.myInstructionSignal.emit("text for test1")
    


