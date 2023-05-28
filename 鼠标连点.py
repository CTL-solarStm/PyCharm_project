import tkinter as tk
import threading
import win32api
import win32con
import time
from pynput import keyboard as pynput_kb


class MouseClicker:
    def __init__(self, interval=0.02):
        self.interval = interval
        self.continue_clicking = False
        self.click_thread = None

    def start_clicking(self):
        self.continue_clicking = True
        self.click_thread = threading.Thread(target=self.click_loop)
        self.click_thread.start()

    def stop_clicking(self):
        self.continue_clicking = False
        if self.click_thread:
            self.click_thread.join()

    def click_loop(self):
        time.sleep(0.5)
        while self.continue_clicking:
            x, y = win32api.GetCursorPos()
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            time.sleep(self.interval)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master.title("肖宫连点器")
        self.clicker = MouseClicker()
        self.start_key = "2"
        self.stop_keys = ["f8","1","3","4"]
        self.end_key = "e"
        self.active_key = None

        self.master = master
        self.master.geometry("412x112")
        self.pack()
        self.create_widgets()

        # 启动 pynput 监听器线程
        self.listener = pynput_kb.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        # 处理窗口关闭请求
        self.master.protocol("WM_DELETE_WINDOW", self.stop_listener_thread)

    def create_widgets(self):
        self.instructions = tk.Label(self, text=f"把肖宫放在2号位置上，\n\n按 {self.start_key} 开始连点，按 {' 或 '.join(self.stop_keys)} 切换角色来停止连点")
        #self.config(bg="#FFFFFF")  # 设置窗口为白色
        self.instructions.pack(side="bottom", fill="both", expand=True)

        # 自定义背景色，用于检查父容器位置和大小是否正常
        #self.instructions.config(bg="#FF0000")

        self.quit_btn = tk.Button(self, text="退出程序", command=self.stop_listener_thread)
        self.quit_btn.pack(side="top", anchor="n", padx=10)

        # 将父控件填充整个窗口
        self.pack(fill="both", expand=True)

    def start_clicker(self):
        self.clicker.start_clicking()
        self.instructions.configure(text=f"正在连点中...按 {' 或 '.join(self.stop_keys)}  切换角色来停止连点")

    def stop_clicker(self):
        self.clicker.stop_clicking()
        self.active_key = None
        self.instructions.configure(text=f"按 {self.start_key} 开始连点，按 {' 或 '.join(self.stop_keys)} 切换角色来停止连点")

    def on_press(self, key):
        if key == pynput_kb.Key.esc:
            # 如果按下了 Esc 键，停止监听
            return False

        try:
            key_name = key.char
        except AttributeError:
            # 如果是特殊按键如 Ctrl，转换为字符串表示形式
            key_name = key.name

        if not self.active_key:
            # 如果没有按下2，忽略所有按键
            if key_name == self.start_key:
                self.active_key = key_name
                self.instructions.configure(text=f"按 {self.end_key} 开始连点，按 {' 或 '.join(self.stop_keys)} 切换角色来停止连点")
        elif self.active_key == self.start_key:
            # 2按键已经按下，等待下一个按键
            if key_name == self.end_key:
                self.start_clicker()
                self.active_key = self.end_key
        elif self.active_key == self.end_key:
            # 正在连点，按下指定按键停止连点
            if key_name in self.stop_keys:
                self.stop_clicker()

    def on_release(self, key):
        pass

    def stop_listener_thread(self):
        # 停止 pynput 监听线程
        if self.listener.is_alive():
            self.listener.stop()

        # 定时器检查监听线程是否已停止
        timeout = 5  # 超时时间为5秒
        start_time = time.time()
        while self.listener.is_alive():
            if time.time() - start_time > timeout:
                # 如果线程仍在运行，强制停止
                self.listener._thread.stop()  # 使用 _thread 属性强制停止线程
                break
        # 关闭主窗口
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    #root.protocol("WM_DELETE_WINDOW", app.stop_listener_thread)
    root.mainloop()