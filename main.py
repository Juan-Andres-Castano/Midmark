import sys
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow

app = QApplication(sys.argv)
w = MainWindow(app,0)
w.show()
app.exec()