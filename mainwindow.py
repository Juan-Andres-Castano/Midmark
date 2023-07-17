__appname__ = "Midmark"
__module__ = "main"
import numpy as np
import time
from PySide6.QtCore import Qt, QTimer
from random import randint
from PySide6.QtCore import * #Qt
from PySide6.QtWidgets import QApplication, QMainWindow,QMessageBox,QTableWidgetItem, QWidget, QLabel, QFileDialog , QVBoxLayout, QSlider, QHBoxLayout
from PySide6.QtGui import QPixmap
import re
import sqlite3
import os
import logging
from ui_mainwindow import Ui_MainWindow
import Step1
import Step2
import csv
import preferences
import utilities
from datetime import datetime
#from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
from pyqtgraph import ImageView
from models import Camera
import cv2

appDataPath = os.environ["APPDATA"] + "\\MidMark\\"

if not os.path.exists(appDataPath):
    try:
        os.makedirs(appDataPath)
    except Exception as e:
        appDataPath = os.getcwd()
        

logging.basicConfig(filename=appDataPath + "midmark.log",
                    format="%(asctime)-15s: %(name)-18s - %(levelname)-8s - %(module)-15s - %(funcname)-20s - %(lineno)-6d - %(message)s",
                    level=logging.DEBUG)

#logger = logging.getLogger(name="main-gui")



class MainWindow(QMainWindow, Ui_MainWindow):
    triggerStep = Signal(int)
    
    dbPath = appDataPath + "midmark.db"
    dbConn = sqlite3.connect(dbPath)
    
    
    def __init__(self,app, indexNumber):
        super().__init__()
        self.setupUi(self)
        self.cameraflag = 0
        self.camera = Camera(0)
        self.camera.initialize()
      #  logger.debug("Application initialized")
        #self.camera = camera
        self.app = app
        self.indexNumber = 0 #indexNumber
        self.workerThread = WorkerThread()
        self.movie_thread = MovieThread(self.camera)
        #self.test1 = Step1()
        #self.test1 = Step1.Step1(self)
        self.x1 = 0
        self.y1 = 0
        self.img_counter = 0
        self.blue_done = 0
        self.green_done = 0
        self.red_done = 0
        self.blueDetected  = 0
        self.redDetected  = 0
        self.greenDetected  = 0
        self.lcdTest = ""
        self.dbCursor = self.dbConn.cursor()
        self.dbCursor.execute("""CREATE TABLE IF NOT EXISTS MidmarkTable(id INTEGER PRIMARY KEY,
                              operatorName TEXT, operatorCode TEXT, serialNumber TEXT, workOrder TEXT, time TEXT, Date TEXT, photoR BLOB, photoG BLOB, photoB BLOB, step2 TEXT, step3 TEXT, step4 TEXT, comments TEXT)""")
        #, , testcanbus TEXT, testtouch TEXT, testrgb TEXT 
        
        
        self.dbConn.commit()
        
        self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "MidMark", "MidMarkData")
        
        self.actionQuit.triggered.connect(self.quit)
        #self.actionQuit.triggered.connect(self.closeEvent)
        self.actionCopy.triggered.connect(self.copy)
        self.actionCut.triggered.connect(self.cut)
        self.actionPaste.triggered.connect(self.paste)
        self.actionUndo.triggered.connect(self.undo)
        self.actionRedo.triggered.connect(self.redo)
        self.actionAbout.triggered.connect(self.about)
        self.actionAboutQt.triggered.connect(self.aboutQt)
        self.ButtonNext.clicked.connect(self.manageTabs)
        self.ButtonQuit.clicked.connect(self.quit)
        self.repeatButton.clicked.connect(self.repeat_test_clicked)
        
        self.actionImport.triggered.connect(self.import_action_triggered)
        self.actionExport.triggered.connect(self.export_action_triggered)
        self.actionView.triggered.connect(self.view_action_triggered)
        self.actionOperator.triggered.connect(self.preferences_action_triggered)
        
        
        
        self.showToolbar = utilities.str2bool(self.settings.value("showToolbar",True))
        self.toolBar.setVisible(self.showToolbar) 
        self.load_initial_settings()
        
        #self.graphWidget = pg.PlotWidget()
        
       # self.plot([1,2,3,4,5,6,7,8,9,10], [30,32,34,32,33,31,29,32,35,45])
        
        self.x = list(range(100)) #100 points
        self.y = [randint(0,100) for _ in range(100)]  # 100 data points

        
        self.graphWidget.setBackground('b')

        
       # self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setTitle("Touch Screen", color="b", size="30pt")
       
        self.graphWidget.setLabel('left', "<span style=\"color:red;font-size:20px\">X</span>")
        self.graphWidget.setLabel('bottom', "<span style=\"color:red;font-size:20px\">Y</span>")
        
        self.ImgWidget = ImageView()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0,10)
        self.layout = QVBoxLayout(self.InstructionStep5)
        self.layout.addWidget(self.ImgWidget)
        self.layout.addWidget(self.startButton)
        #self.layouth  = QHBoxLayout(self.InstructionStep5)

        #self.layouth.addWidget(self.colorBText)
        #self.layouth.addWidget(self.colorRText)
        #3self.layouth.addWidget(self.colorGText)
        #self.layout.addLayout(self.layouth)
        
        
        
        
        self.startButton.clicked.connect(self.start_movie)
        
        #hour = [1,2,3,4,5,6,7,8,9,10]
        #temperature = [30,32,34,32,33,31,29,32,35,45]
        #self.graphWidget.setBackground('w')
        #self.graphWidget.plot(hour, temperature)
      #  self.triggerStep.connect(self.test1.trigger_test1)
       # self.ButtonNext.clicked.connect(self.test1.trigger_test1)
       # self.connect(self.workerThread, SIGNAL("threadDone()"), self.threadDone, Qt.DirectConnection)
        self.connect(self.movie_thread, SIGNAL("threadDone()"), self.threadDone, Qt.DirectConnection)
        #self.workerThread.myNextSignal.connect(self.threadDone)
        self.slider.valueChanged.connect(self.update_brightness)

        self.timer = QTimer(self)
        
        #self.timer = QtCore.QTimer()
        #self.connect(timer, SIGNAL("timeout()"), self.update_plot_data)
        self.connect(self.timer, SIGNAL("timeout()"), self.update_movie)
        
        #timer.start(1)
        #timer.stop
        
        
    def update_movie(self):
        
        #frame =[]
        path = 'C:/MidmarkProject/camera'
        if self.cameraflag ==1:
            print("flag camera update movie  timer : %2d" % self.cameraflag)
            self.ImgWidget.setImage(self.camera.last_frame.T)
            frame = self.camera.get_myframe()

            cv2.imshow("test", frame)
        
            b = frame[:, :, :1]
            g = frame[:, :, 1:2]
            r = frame[:, :, 2:]
  
            # computing the mean
            b_mean = np.mean(b)
            g_mean = np.mean(g)
            r_mean = np.mean(r)
    
       # print(b_mean)
       # print(g_mean)
       # print(r_mean)
            #self.colorRText.setText("FAIL")
            #3self.colorGText.setText("FAIL")
            #self.colorBText.setText("FAIL")
    
    # displaying the most prominent color
            if (b_mean > g_mean and b_mean > r_mean):
                if self.blue_done == 0:
                    self.blue_done = 1
                    
                    print(b_mean)
                    print(g_mean)
                    print(r_mean)
                    
                    print("Blue")
                    self.blueDetected  = 1
                    
                    
                    img_name = "lcd_frame_blue_{}.jpg".format( (self.serialNumber.text()) )
                    self.colorBText.setText(img_name)
                    
                    cv2.imwrite(os.path.join(path , img_name), frame)
                    cv2.imwrite(img_name, frame)
                    #print("{} written!".format(img_name))
            elif (g_mean > r_mean and g_mean > b_mean):
                if self.green_done == 0:
                    self.green_done = 1
                    print(b_mean)
                    print(g_mean)
                    print(r_mean)
                    #self.colorText.setText("green")
                    print("Green")
                    self.greenDetected  = 1
                    img_name = "lcd_frame_green_{}.jpg".format( (self.serialNumber.text()) )
                    cv2.imwrite(os.path.join(path , img_name), frame)
                    self.colorGText.setText(img_name)
                    
                    cv2.imwrite(img_name, frame)
                    print("{} written!".format(img_name))
            else:
                if self.red_done == 0:
                    self.red_done = 1
                    print(b_mean)
                    print(g_mean)
                    print(r_mean)
                
                    #self.colorText.setText("red")
                    print("Red")
                    self.redDetected  = 1
                    #img_name = "C:\Midmark\camera\lcd_frame_frame_red_{}.png".format(self.serialNumber )
                    #img_name = "C:\Midmark\camera\lcd_frame_frame_red_{}.png"#.format((self.serialNumber.text()) )
                    
                    img_name = "lcd_frame_red_{}.jpg".format( (self.serialNumber.text()) )
                    cv2.imwrite(img_name, frame)
                    cv2.imwrite(os.path.join(path , img_name), frame)
                    self.colorRText.setText(img_name)
                    
                    #print("{} written!".format(img_name))

        
    def update_brightness(self, value):
        value /= 10
        self.camera.set_brightness(value)

    def start_movie(self):
        self.blue_done = 0
        self.green_done = 0
        self.red_done = 0
        self.blueDetected  = 0
        self.redDetected  = 0
        self.greenDetected  = 0
        self.colorRText.setText("")
        self.colorBText.setText("")
        self.colorGText.setText("")
        self.failButton.setStyleSheet("background-color: gray")
        self.passButton.setStyleSheet("background-color: gray")

        print("flag camera at buton start movie: %2d" % self.cameraflag)
        self.timer.start(1)
        
        if self.cameraflag ==0:
            self.cameraflag = 1
           # self.movie_thread = MovieThread(self.camera)
            self.movie_thread.start()

         
        else:
            pass
        #self.cameraflag = 0
    #        self.camera.close_camera()
      #      cv2.destroyAllWindows()
       #     self.camera.close_camera()
             
            
        #timer.start(5)
        #self.update_timer.start(30)       
        
    def quit(self):
        self.camera.close_camera()
       # self.camera.close_camera()
       # cv2.destroyAllWindows()
        self.app.quit()
    def copy(self):
        self.textEdit.copy()
    def cut(self):
        self.textEdit.cut()
    def paste(self):
        self.textEdit.paste()
    def undo(self):
        self.textEdit.undo()
    def redo(self):
        self.textEdit.redo()
    def about(self):
        QMessageBox.information(self,"Going pro!","QMainWindow,Qt Designer and Resources : Going pro!")
    def aboutQt(self):
        QApplication.aboutQt()
    def import_action_triggered(self):
        pass
    def preferences_action_triggered(self):
        dlg = preferences.Preferences(self)
        sig = dlg.checkBoxSignal
        sig.connect(self.showHideToolBar)
        dlg.exec_()
    
    def action_exit_triggered(self):
        #pass #self.closeEvent()
        self.camera.close_camera()
        
        #cv2.destroyAllWindows()
        self.quit()
    
    def update_plot_data(self):

        #self.x = self.x[1:]  # Remove the first y element.
        #self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
        

        #self.y = self.y[1:]  # Remove the first
        #self.y.append( randint(0,100))  # Add a new random value.

        #self.data_line.setData(self.x, self.y)  # Update the data.    
        
        self.x1 = 10 * np.random.normal(size=1)
        self.y1 = 10 * np.random.normal(size=1)
        
        if self.x1 <0:
            self.x1 = self.x1 * -1
        if self.y1 < 0:
            self.y1 = self.y1 * -1
        
        if self.x1 > 20:
            self.x1 = 20 
        if self.y1 > 20:
            self.y1 = 20    
            
        pen = pg.mkPen(color=(255, 0, 0), width = 4)
        self.graphWidget.plot(self.x1, self.y1, pen=pen, symbol='o')
        
    def closeEvent(self, event, *args, **kwargs):
         result = QMessageBox.question(self, __appname__,"Are you sure you want ot exit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
         if result == QMessageBox.Yes:
             event.accept()
         else:
             event.ignore()
     
    def showHideToolBar(self,param):
        self.toolBar.setVisible(param)
        self.technicianView.setVisible(param)
        self.technicianControls.setVisible(param)    
        self.settings.setValue("showToolbar",utilities.bool2str(param)) 
        #self.settings.setValue()
        
    def plot(self, hour, temperature):
        #self.graphWidget.plot(hour, temperature)
        self.graphWidget.setTitle("Your Title Here", color="b", size="30pt")
        styles = {'color':'r', 'font-size':'20px'}
        self.graphWidget.setLabel('left', "<span style=\"color:red;font-size:20px\">Temperature (°C)</span>")
        self.graphWidget.setLabel('bottom', "<span style=\"color:red;font-size:20px\">Hour (H)</span>")
        self.graphWidget.plot(hour, temperature)
        self.graphWidget.showGrid(x=True, y=True)
        
        
    def export_action_triggered(self):
        self.dbCursor.execute("SELECT * FROM MidmarkTable")
        dbFile = QFileDialog.getSaveFileName(parent=None,caption="Export database to a file",dir=".",filter="Midmark CSV (*.csv)")
        
        if dbFile[0]:
            try:
                with open(dbFile[0], "w", newline='') as csvFile: #with open(dbFile[0], "wb") as csvFile:  
                    csvWriter = csv.writer(csvFile, delimiter=',', quotechar="\"",quoting=csv.QUOTE_MINIMAL )

                    rows = self.dbCursor.fetchall()
                    rowCount = len(rows)

                    for row in rows:
                        csvWriter.writerow(row)
                            
                    QMessageBox.information(self,__appname__,"Succesfully exported" + str(rowCount) + "rows to a file\r\n" + str(QDir.toNativeSeparators(dbFile[0])) )
            except Exception as e:
                QMessageBox.critical(self,__appname__,"Error exporting file, error is\r\n" + str(e))                    
                return         
        
    def view_action_triggered(self):
        self.tabWidget.setCurrentIndex(1)
    def load_initial_settings(self):
        pass
    
    def validate_fields(self):
        self.dbCursor.execute("""SELECT operatorName FROM MidmarkTable""")
        usernames = self.dbCursor.fetchall()
        for operatorNames in usernames:
            if self.operatorName.text() in operatorNames[0]:
                QMessageBox.warning(self,"Warning!", "such serial number exsits!")
                return False
        #612-444-3333
        if not re.match('^[2-9]\d{2}-\d{3}-\d{4}',self.serialNumber.tet()):
                QMessageBox.warning(self,"Warning!", "such serial format!")
                return False
        return True    
        
    def threadDone(self):  #,param
      #  pass
        self.cameraflag = 0
        self.timer.stop()
        
        if ( (self.blueDetected  == 1) & (self.redDetected  == 1)& (self.greenDetected  == 1)):
            self.lcdTest = "PASS"
            
            self.passButton.setStyleSheet("background-color: green")
            self.failButton.setStyleSheet("background-color: gray")
        else:
            self.lcdTest = "FAIL"
            self.passButton.setStyleSheet("background-color: gray")
            self.failButton.setStyleSheet("background-color: red")
            
            
        print(self.lcdTest)    
        print("flag camera at end of thread: %2d" % self.cameraflag)
        #self.camera.close_camera()
        #cv2.destroyAllWindows()
      #  self.InstructionsText.setText("Instructions : " + str(param) )
        #QMessageBox.information(self,"Warning!", "worker thread execution completed")
        
  
    def load_initial_settings(self):
        self.dbCursor.execute("""SELECT * FROM MidmarkTable""")
        allRows = self.dbCursor.fetchall()
        
        for row in allRows:
            index = allRows.index(row)
            self.tableTests.insertRow(index)
            self.tableTests.setItem(index, 0, QTableWidgetItem(row[1]))
            self.tableTests.setItem(index, 1, QTableWidgetItem(row[2]))
            self.tableTests.setItem(index, 2, QTableWidgetItem(row[3]))
            self.tableTests.setItem(index, 3, QTableWidgetItem(row[4]))
            

            
            self.tableTests.setItem(index, 4, QTableWidgetItem(row[5]))            
            self.tableTests.setItem(index, 5, QTableWidgetItem(row[6]))
            
            itemImageI = self.getImageLabel(row[7])
            self.tableTests.setCellWidget(index,6, itemImageI  )
            
            itemImageI1 = self.getImageLabel(row[8])
            self.tableTests.setCellWidget(index,7, itemImageI1  )
            
            itemImageI2 = self.getImageLabel(row[9])
            self.tableTests.setCellWidget(index,8, itemImageI2  )
            
            self.tableTests.setItem(index, 9, QTableWidgetItem(row[10]))            
            self.tableTests.setItem(index, 10, QTableWidgetItem(row[11]))
            self.tableTests.setItem(index, 11, QTableWidgetItem(row[12]))            
            self.tableTests.setItem(index, 12, QTableWidgetItem(row[13]))
            
        
    def repeat_test_clicked(self):
        currentRow = self.tableTests.currentRow()
        print("repeat test", currentRow)
        if currentRow > -1:
            currentusername = (self.tableTests.item(currentRow,0).text(), )
            self.dbCursor.execute("""DELETE FROM MidmarkTable WHERE operatorName=?""", currentusername )
            self.dbConn.commit()
            self.tableTests.removeRow(currentRow)

    
    def convertToBinaryData(self, filename):
        # Convert digital data to binary format
        with open(filename, 'rb') as file:
            blobData = file.read()
        return blobData
    
    def getImageLabel(self,image):
        imageLabel = QLabel(self.centralwidget)
        imageLabel.setText("")
        imageLabel.setScaledContents(True)
        pixmap = QPixmap()
        
        pixmap.loadFromData(image, 'jpg')
        
        pixmap.scaledToHeight(20)
        pixmap.scaledToWidth(10)
        imageLabel.setPixmap(pixmap)
        return imageLabel
            
        #if not pixmap.loadFromData(image, 'jpg'):
         #   print("Error loading image format")
        #    return False
        #else:
        #    print("success loading image format")
        #    pixmap.scaledToHeight(10)
        #    pixmap.scaledToWidth(10)
        #    imageLabel.setPixmap(pixmap)
        #    return imageLabel
        
    
    def manageTabs(self):
        print("entrando")
        self.indexNumber = 4 #self.indexNumber + 1
        if self.indexNumber > 4:
            self.indexNumber = 0
            
        self.tabInputs.setCurrentIndex(self.indexNumber)    
        self.tabOutputs.setCurrentIndex(self.indexNumber)   
        self.tabInstructions.setCurrentIndex(self.indexNumber)   
        
        #if not self.validate_fields():
        #    return False
        
        if self.indexNumber == 1:
            print(self.indexNumber)   
            test1 = Step1.Step1(self)

           # sig1 = test2.myInstructionSignal
            self.triggerStep.connect(test1.trigger_test1)     


            sig = test1.myInstructionSignal
            sig.connect(self.displayInstructionText)
            
            self.triggerStep.emit(5)           
            print("preparing trigger step 1")
            

            

            
            
            
            
        elif self.indexNumber == 2:
            print(self.indexNumber)   
            test2 = Step2.Step2(self)

           # sig1 = test2.myInstructionSignal
            self.triggerStep.connect(test2.trigger_test2)     


            sig = test2.myInstructionSignal
            sig.connect(self.displayInstructionText)
            
            self.triggerStep.emit(5)           
            print("preparing trigger step 1")    
        elif self.indexNumber == 4:
            print("starting")  
            print(self.indexNumber)   
            operatorName = self.operatorName.text()
            operatorCode = self.operatorCode.text()
            serialNumber = self.serialNumber.text()
            workOrder = self.workOrder.text()
            
            
            
            
            currentRowcount = self.tableTests.rowCount()
            
            self.tableTests.insertRow(currentRowcount)
            
            self.tableTests.setItem(currentRowcount,0, QTableWidgetItem(operatorName))
            self.tableTests.setItem(currentRowcount,1, QTableWidgetItem(operatorCode))
            self.tableTests.setItem(currentRowcount,3, QTableWidgetItem(workOrder))
            self.tableTests.setItem(currentRowcount,2, QTableWidgetItem(serialNumber))
            
            
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = datetime.today().strftime('%Y-%m-%d')
            
            self.tableTests.setItem(currentRowcount,4, QTableWidgetItem(current_time))
            self.tableTests.setItem(currentRowcount,5, QTableWidgetItem(current_date))
            
            #str(bool)
            #photoTest =  "C:\Midmark\camera\photo1.jpg"
            
            #mage = "lcd_frame_green_{}.png".format( (self.serialNumber.text()) )
            image = self.colorRText.toPlainText()
            if image == "":
                imageR = None
            else:
                        
                photoTest = os.path.join('C:/MidmarkProject/camera/', image)
            
                #photoTest  =   "C:\Midmark\camera\".format(image)  
            
                imageR =   self.convertToBinaryData(photoTest)
                itemImage = self.getImageLabel(imageR)
                self.tableTests.setCellWidget(currentRowcount,6,  itemImage )
                
            
            image = self.colorGText.toPlainText()
            
            if image == "":
                imageG = None
            else:
                        
                photoTest = os.path.join('C:/MidmarkProject/camera/', image)
            
                #photoTest  =   "C:\Midmark\camera\".format(image)  
            
                imageG =   self.convertToBinaryData(photoTest)
                itemImage = self.getImageLabel(imageG)
                self.tableTests.setCellWidget(currentRowcount,7,  itemImage )
                
                
            image = self.colorBText.toPlainText()
            
            if image == "":
                imageB = None
            else:
                        
                photoTest = os.path.join('C:/MidmarkProject/camera/', image)
            
                #photoTest  =   "C:\Midmark\camera\".format(image)  
            
                imageB =   self.convertToBinaryData(photoTest)
                itemImage = self.getImageLabel(imageB)
                self.tableTests.setCellWidget(currentRowcount,8,  itemImage )
            
            
            
            
            
            

            
            
            
            comments = self.commentsText.toPlainText()
            
            test4Result = self.lcdTest
            
            test3Result = "PASS"
            print(test3Result)
            test2Result = "PASS"
            print(test2Result)
            
            self.tableTests.setItem(currentRowcount,9, QTableWidgetItem(test2Result))
            self.tableTests.setItem(currentRowcount,10, QTableWidgetItem(test3Result))
            
            self.tableTests.setItem(currentRowcount,11, QTableWidgetItem(test4Result))
            self.tableTests.setItem(currentRowcount,12, QTableWidgetItem(comments))
            
            parameters = (None, operatorName, operatorCode, serialNumber, workOrder, current_time, current_date, imageR, imageG, imageB, test2Result, test3Result, test4Result, comments )   
            self.dbCursor.execute('''INSERT INTO MidmarkTable VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? ,?)''', parameters)
            self.dbConn.commit()
            print("finishing")   
            
        else:
            pass
            #self.workerThread.start()
        #QMessageBox.information(self,"Done!", "Done")
       # self.InstructionsText.setText("done")
        
        
    def displayInstructionText(self, param):
        print("feedback")
        self.InstructionsText.setText("Instructions : " + str(param) )  

class WorkerThread(QThread):
    myNextSignal = Signal(int)
    def __init__(self, parent=None):
        super(WorkerThread,self).__init__(parent)
    def run(self):
       # time.sleep(5)    
        print( "done with the thread")
        self.myNextSignal.emit(10)
       # self.InstructionsText.setText("done")
        #self.emit(SIGNAL("threadDone()"))
              
class MovieThread(QThread):
    def __init__(self, camera):
        super().__init__()
        self.camera = camera

    def run(self):
        print( "run thread")
        self.camera.acquire_movie(100)  
        #self.cameraflag =0 
        
        self.emit(SIGNAL("threadDone()"))
        #self.camera.close_camera()
        #cv2.destroyAllWindows()          