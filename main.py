import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget

def main():
    app = QApplication(sys.argv)
    #app.setWindowIcon(QIcon(resource_path('bar.ico')))
    w = QWidget()

    button = QtWidgets.QPushButton(w)
    button.setText("hoge!")
    button.move(100,200)
    button.setGeometry(20, 10, 30, 40)

    def unko():
        print("kue")

    button.clicked.connect(unko)

    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()