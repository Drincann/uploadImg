from ctypes import *
from ctypes import wintypes
import win32con
import threading
import inspect
import ctypes

class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [
        ('vkCode', c_int),
        ('scanCode', c_int),
        ('flags', c_int),
        ('time', c_int),
        ('dwExtraInfo', c_uint),
        ('', c_void_p)
    ]


class POINT(Structure):
    _fields_ = [
        ('x', c_long),
        ('y', c_long)
    ]


class MSLLHOOKSTRUCT(Structure):
    _fields_ = [
        ('pt', POINT),
        ('hwnd', c_int),
        ('wHitTestCode', c_uint),
        ('dwExtraInfo', c_uint),
    ]

class hook:

    def __init__(self, mou_callback=None, keyb_callback=None):
        self._SetWindowsHookEx = windll.user32.SetWindowsHookExA
        self._UnhookWindowsHookEx = windll.user32.UnhookWindowsHookEx
        self._CallNextHookEx = windll.user32.CallNextHookEx
        self._GetMessage = windll.user32.GetMessageA
        self._GetModuleHandle = windll.kernel32.GetModuleHandleW
        # 保存键盘钩子函数句柄
        self._keyboard_hd = None
        # 保存鼠标钩子函数句柄
        self._mouse_hd = None
        self.mou_callback = mou_callback
        self.keyb_callback = keyb_callback

        self.mouThread = None
        self.keybThread = None

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)

    def _wait_for_msg(self):
        msg = wintypes.MSG()
        self._GetMessage(msg, 0, 0, 0)



    def _keyboard_pro(self, nCode, wParam, lParam):
        """
        函数功能：键盘钩子函数，当有按键按下时此函数被回调
        """
        if nCode == win32con.HC_ACTION:
            KBDLLHOOKSTRUCT_p = POINTER(KBDLLHOOKSTRUCT)
            param=cast(lParam,KBDLLHOOKSTRUCT_p)
            self.keyb_callback(param.contents.vkCode, param.contents.flags)
        return self._CallNextHookEx(self._keyboard_hd, nCode, wParam, lParam)


    def start_keyboard_hook(self, callback_fun=None):
        callback_fun = self.keyb_callback if callback_fun == None else callback_fun
        self.keybThread = threading.Thread(target=self._keboard_hook, args=[callback_fun])
        self.keybThread.start()



    def _keboard_hook(self, callback_fun):
        HOOKPROTYPE = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
        pointer = HOOKPROTYPE(self._keyboard_pro)
        self.keyb_callback = callback_fun
        keyboard_hd = self._SetWindowsHookEx(
            win32con.WH_KEYBOARD_LL,
            pointer,
            self._GetModuleHandle(None),
            0)
        self._wait_for_msg()


    def stop_keyboard_hook(self):
        self._UnhookWindowsHookEx(self._keyboard_hd)
        self.stop_thread(self.keybThread)




    def _mouse_pro(self, nCode, wParam, lParam):
        if nCode == win32con.HC_ACTION:
            MSLLHOOKSTRUCT_p = POINTER(MSLLHOOKSTRUCT)
            param=cast(lParam,MSLLHOOKSTRUCT_p)

            state = 0
            x = param.contents.pt.x
            y = param.contents.pt.y
            if wParam == win32con.WM_LBUTTONDOWN:#左键点击
                state = 1
            elif wParam == win32con.WM_LBUTTONUP:#左键抬起
                state = 2
            elif wParam == win32con.WM_RBUTTONDOWN:#右键点击
                state = 3
            elif wParam == win32con.WM_RBUTTONUP:#右键抬起
                state = 4
            elif wParam == win32con.WM_MOUSEMOVE:#鼠标移动
                state = 5
            self.mou_callback(state, [x, y])
        return self._CallNextHookEx(self._mouse_hd, nCode, wParam, lParam)


    def start_mouse_hook(self, callback_fun):
        callback_fun = self.mou_callback if callback_fun == None else callback_fun
        self.mouThread = threading.Thread(target=self._mouse_hook, args=[callback_fun])
        self.mouThread.start()



    def _mouse_hook(self, callback_fun):
        HOOKPROTYPE = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
        pointer = HOOKPROTYPE(self._mouse_pro)
        self.mou_callback = callback_fun
        mouse_hd = self._SetWindowsHookEx(
            win32con.WH_MOUSE_LL,
            pointer,
            self._GetModuleHandle(None),
            0)
        self._wait_for_msg()
    def stop_mouse_hook(self):
        """
        函数功能：停止鼠标监听
        """
        self._UnhookWindowsHookEx(self._mouse_hd)
        self.stop_thread(self.mouThread)

