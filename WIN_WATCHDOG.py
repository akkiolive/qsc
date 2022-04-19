import threading
import win32gui
from WINS import WINS

import copy


from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

class QWatcher(QObject):
    signal = pyqtSignal()
    def __init__(self):
        QObject.__init__(self)

        self.w = Watcher("watcher", self.signal)
        self.w.start()
        self.que_last = []




    

class Watcher(threading.Thread):
    def __init__(self, thread_name, signal):
        self.thread_name = thread_name
        threading.Thread.__init__(self)
        self.hwnd_active = win32gui.GetForegroundWindow()
        self.hwnd_active_last = self.hwnd_active
        self.count = 0
        self.wins = WINS()
        self.wins2 = WINS()
        self.wins2.refresh_alttabwins()
        self.wins3 = WINS()
        self.wins3.wins = copy.deepcopy(self.wins2.wins)
        self.wins.refresh_alttabwins()
        self.q = False
        self.p = False
        self.f = False
        self.que = []
        self.signal = signal
        self.wins_last = self.wins.wins

    def run(self):
        while True:
            if self.q:
                break
            if self.p:
                continue
            if self.f:
                self.que = []
                self.f = False
            if self.hwnd_active != win32gui.GetForegroundWindow():
                self.hwnd_active  = win32gui.GetForegroundWindow()
                self.count += 1
                print("active changed", self.count, self.hwnd_active_last, "->", self.hwnd_active)
                self.signal.emit()
                self.que.append(self.hwnd_active)
                #if self.count > 20:
                #    break
                self.hwnd_active_last = self.hwnd_active
            text_changed = False
            self.wins2.refresh_alttabwins()
            for hwnd in self.wins2.wins:
                win = self.wins2.wins[hwnd]
                if hwnd in self.wins3.wins:
                    win_last = self.wins3.wins[hwnd]
                    if win_last.text != win.text:
                        print("text was changed!", hwnd, win_last.text, "->", win.text)
                        text_changed = True
                else:
                    print("added new window!", hwnd, win.text)
                    self.wins3.wins = copy.deepcopy(self.wins2.wins)
                    self.signal.emit()


            if text_changed:
                self.signal.emit()
                self.wins3.wins = copy.deepcopy(self.wins2.wins)

    def get_wins(self):
        return self.wins
    def kill(self):
        self.q = True
    def pause(self):
        self.p = True
    def unpause(self):
        self.p = False
    def flush(self):
        self.f = True



