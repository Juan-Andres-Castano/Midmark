from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

from ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.app = app
        
        #self.setWindowTitle("User data")
        #self.operatorNext.clicked.connect(self.do_something)
        
    

        

        self.actionQuit.triggered.connect(self.quit)
        #self.actionCopy.triggered.connect(self.copy)
        #self.actionCut.triggered.connect(self.cut)
        #self.actionPaste.triggered.connect(self.paste)
        #self.actionUndo.triggered.connect(self.undo)
        #self.actionRedo.triggered.connect(self.redo)
        #self.actionAbout.triggered.connect(self.about)
        #self.actionAboutQt.triggered.connect(self.aboutQt)

    def quit(self):
        self.app.quit()
    #def copy(self):
    #    self.textEdit.copy()
    #def cut(self):
    #    self.textEdit.cut()
    #def paste(self):
    #    self.textEdit.paste()
    #def undo(self):
    #    self.textEdit.undo()
    #def redo(self):
    #    self.textEdit.redo()
    #def about(self):
    #    QMessageBox.information(self,"Going pro!","QMainWindow,Qt Designer and Resources : Going pro!")
    #def aboutQt(self):
    #    QApplication.aboutQt()
    
#    def do_something(self):
 #       print(self.operatorName.text()," is a ",self.operatorCode.text())
