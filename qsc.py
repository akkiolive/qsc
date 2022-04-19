import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QGridLayout, QLabel, QScrollArea, QTextEdit, QTabWidget,QListWidget, QLineEdit, QMenuBar, qApp, QTableWidget, QTableWidgetItem
from PyQt5 import QtGui, QtCore
import threading
from PIL.ImageQt import ImageQt

import re

from everything import Everything
from WINS import WINS
from WIN_WATCHDOG import QWatcher

class FileSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.searchbox = QLineEdit()
        self.searchbutton = QPushButton()
        self.listbox = QListWidget()

        self.grid = QGridLayout()
        self.grid.addWidget(self.searchbox)
        self.grid.addWidget(self.searchbutton)
        self.grid.addWidget(self.listbox)
        self.setLayout(self.grid)



        self.start_everything()

        self.searchbox.textChanged.connect(self.search)

    def start_everything(self):
        self.everything = Everything()
    
    def search(self, text):
        if text:
            print("searching:", text)
            filenames = self.everything.search(text)
            print(len(filenames))
            self.listbox.clear()
            if len(filenames) < 100:
                for filename in filenames:
                    self.listbox.addItem(filename)
    
class WinSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.searchbox = QLineEdit()
        self.searchbutton = QPushButton()
        self.table = QTableWidget(100, 6)
        #self.table.setSortingEnabled(True)
        self.table.itemClicked.connect(self.tableClicked)

        self.grid = QGridLayout()
        self.grid.addWidget(self.searchbox)
        #self.grid.addWidget(self.searchbutton)
        self.grid.addWidget(self.table)
        self.setLayout(self.grid)

        self.parent = parent

        
        self.wins = self.parent.qw.w.wins
        self.table_data = {}
        self.table_arrange = [
                "zorder",
                "text",
                "exe_path",
                "hwnd",
        ]
        self.ignore = [
            #{"text": "qsc", "exe_path": "python.exe"},
            {"text": "Microsoft Text Input Application", "exe_path": "TextInputHost.exe"},
            {"text": "設定", "exe_path": "ApplicationFrameHost.exe"},
            {"text": "設定", "exe_path": "SystemSettings.exe"},
        ]
        self.init()
        
        self.searchbox.textChanged.connect(self.search)

    def tableClicked(self, item):
        import win32gui, win32con
        try:
            hwnd = int(self.table.item(item.row(), 3).text())
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            self.parent.setFocus(QtCore.Qt.PopupFocusReason)
        except:
            print("failed to activate window")
                


    def init(self):
        print("init")
        self.wins.refresh_alttabwins()
        self.table.clear()
        nt = 0
        for n, hwnd in enumerate(self.wins.wins):
            win = self.wins.wins[hwnd]
            if self.searchbox.text() == "" or \
                re.search(self.searchbox.text().lower(), win.text.lower()) or re.search(self.searchbox.text().lower(),win.exe_path.split("\\")[-1].lower()):
                nt += 1
                for ignore in self.ignore:
                    ignore_matched = True
                    for key in ignore:
                        if key == "exe_path":
                            val = str(ignore[key].split("\\")[-1])
                            val_win = str(win.__dict__[key].split("\\")[-1])
                        else:
                            val = str(ignore[key])
                            val_win = str(win.__dict__[key])
                        if val != val_win:
                            ignore_matched = False
                            break
                    if ignore_matched:
                        nt += -1
                        break
                if not ignore_matched:        
                    for m, key in enumerate(self.table_arrange):
                        if key == "exe_path":
                            val = str(win.__dict__[key].split("\\")[-1])
                        else:
                            val = str(win.__dict__[key])
                        item = QTableWidgetItem(val)
                        if key == "text":
                            pilimage = win.get_icon_bitmap()
                            qimage = ImageQt(pilimage)
                            pixmap = QtGui.QPixmap.fromImage(qimage)
                            icon = QtGui.QIcon(pixmap)
                            item.setIcon(icon)
                        self.table.setItem(nt-1, m, item)
        self.table.resizeColumnsToContents()
        
    def search(self, text):
        self.init()
                    
    
    def refresh(self):
        self.search(self.searchbox.text())
        
            
class ExampleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(600, 600)
        self.move(300, 100)
        self.setWindowTitle("qsc")
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        # hash
        self.hash = "2398hsadkjnfaskljf9pa82098dyufasdfnjasd8"

        # QWatcher
        self.qw = QWatcher()

        # statusbar
        self.statusBar().show()

        # meubar
        self.createMenu()

        #tab
        self.tab = QTabWidget()

        # widget
        self.fileselectors = []
        ws = WinSelector(self)
        self.qw.signal.connect(self.qw.w.wins.refresh_alttabwins)
        self.qw.signal.connect(ws.refresh)
        self.tab.addTab(ws, "Win")


        self.button_add_tab = QPushButton("add")
        self.button_remove_tab = QPushButton("remove")
        def add_tab():
            ws = WinSelector(self)
            self.tab.addTab(ws, "new")
            self.qw.signal.connect(ws.refresh)
        self.button_add_tab.clicked.connect(add_tab)
            
        # grid
        self.central = QWidget()
        self.grid = QGridLayout(self.central)
        self.grid.addWidget(self.tab)
        self.grid.addWidget(self.button_add_tab)
        self.grid.addWidget(self.button_remove_tab)

        self.setCentralWidget(self.central)


        
    @property
    def wins(self):
        return self.w.get_wins()

    def createMenu(self):
        file = self.menuBar().addMenu("File")
        exit = file.addAction("Exit")
        exit.setStatusTip("Exit application")
        exit.triggered.connect(qApp.exit)      
        self.show()
    



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ExampleApp()
    ret = app.exec()
    win.qw.w.kill()
    sys.exit(ret)
