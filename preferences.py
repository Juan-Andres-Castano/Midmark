from PySide6.QtWidgets import QCheckBox, QPushButton, QVBoxLayout, QApplication, QMainWindow,QMessageBox,QTableWidgetItem, QWidget, QLabel, QFileDialog, QDialog
from PySide6.QtCore import *


class Preferences(QDialog):
    
    checkBoxSignal = Signal(bool)
    
    def __init__(self,parent=None):
        super(Preferences, self).__init__(parent)
        
        self.resize(200,100)
        self.setWindowTitle("Preferences")
        
        self.checkBox = QCheckBox("Show expert toolbar")
        #######self.checkBox.setChecked(showToolbar)
        closeBtn = QPushButton("close")
        
        layout = QVBoxLayout()
        layout.addWidget(self.checkBox)
        layout.addWidget(closeBtn)
        
        self.setLayout(layout)

        closeBtn.clicked.connect(self.close)
        self.checkBox.stateChanged.connect(self.checkBoxStateChanged)
        
        
    def checkBoxStateChanged(self):
        self.checkBoxSignal.emit(self.checkBox.isChecked())
        
        
        
    