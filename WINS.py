import win32gui
import win32con
import win32api
import win32process
import win32ui

from PIL import Image

class WINS:
    def __init__(self):
        self.wins = {}
        self.zorder_of_wins = {}

    def add_win(self, hwnd):
        win = self.WIN(hwnd)
        self.wins[hwnd] = win
        return win
        
    def _refresh_alttabwins_enumproc(self, hwnd, lp):
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        is_ws_ex_toolwindow = ex_style & win32con.WS_EX_TOOLWINDOW
        if win32gui.IsWindowVisible(hwnd) and not is_ws_ex_toolwindow:
            win = self.add_win(hwnd)
            self.wins_count += 1
            win.refresh_info()
            win.zorder = self.wins_count
        return 1

    def refresh_alttabwins(self, init=True):
        if init:
            self.wins_count = 0
            self.wins = {}
        win32gui.EnumWindows(self._refresh_alttabwins_enumproc, 0)

    class WIN:
        def __init__(self, hwnd):
            self.hwnd = hwnd
            self.exe_path = None

        def refresh_info(self):
            self.text = win32gui.GetWindowText(self.hwnd)
            self.pos = win32gui.GetWindowRect(self.hwnd)
            self.threadId, self.procId = win32process.GetWindowThreadProcessId(
                self.hwnd)
            hproc = win32api.OpenProcess(
                win32con.PROCESS_QUERY_LIMITED_INFORMATION, False, self.procId)
            self.exe_path = win32process.GetModuleFileNameEx(hproc, win32con.NULL)
            self.process_name = self.exe_path.split("\\")[-1].replace(".exe", "")
            win32api.CloseHandle(hproc)

        def get_text(self):
            self.text = win32gui.GetWindowText(self.hwnd)
            return self.text

        def get_icon_bitmap(self, saveAs=None):
            if self.exe_path is None:
                return None
            
            #http://melpystudio.blog82.fc2.com/blog-entry-119.html
            
            # Exeのパスからアイコンを取得する関数。
            # 大きいアイコンのサイズを取得。-------------------------------------------
            ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
            ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
            # -------------------------------------------------------------------------

            # アイコンを取得。
            large, small = win32gui.ExtractIconEx(self.exe_path, 0)
            # 小さいアイコンは今回は使用しないので破棄する。
            if small:
                win32gui.DestroyIcon(small[0])
            # 大きいアイコンを取得できなかった場合はNoneを返す。
            if not large:
                return None

            # アイコンのハンドルを取得。-----------------------------------------------
            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hbmp = win32ui.CreateBitmap()

            # Bitmapを作成。その際上で取得した大きいアイコンのサイズを指定する。
            # この値は直接int値を入力してもよい。
            hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)

            hdc = hdc.CreateCompatibleDC()
            hdc.SelectObject(hbmp)
            hdc.DrawIcon((0, 0), large[0])
            hdc.DeleteDC()
            # -------------------------------------------------------------------------

            bmpstr = hbmp.GetBitmapBits(True)

            #https://stackoverflow.com/questions/32341661/getting-a-windows-program-icon-and-saving-it-as-a-png-python
            self.img = Image.frombuffer('RGBA',(ico_x, ico_y),bmpstr, 'raw', 'BGRA', 0, 1)
            if saveAs:
                self.img.save(saveAs)
            return self.img


        def verbose(self):
            for key in self.__dict__:
                print(f"WIN.{key} = {self.__dict__[key]}")

        def serializable(self):
            out = {}
            for key in self.__dict__:
                item = self.__dict__[key]
                out[key] = str(item)
        
        def activate(self):
            #win32gui.BringWindowToTop(self.hwnd)
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                win32con.SWP_SHOWWINDOW | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                
