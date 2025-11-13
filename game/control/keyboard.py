import time
import ctypes
from threading import Thread
from typing import (
    List,
    Dict,
    Any
)


# 获取Windows user32.dll中的SendInput函数，用于模拟键盘鼠标输入
_SendInput = ctypes.windll.user32.SendInput
# 定义指向c_ulong类型的指针类型
_PUL = ctypes.POINTER(ctypes.c_ulong)


# 定义键盘输入结构体
class _KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),       # 虚拟键码
                ("wScan", ctypes.c_ushort),     # 硬件扫描码
                ("dwFlags", ctypes.c_ulong),    # 操作标志（按下/释放）
                ("time", ctypes.c_ulong),       # 时间戳
                ("dwExtraInfo", _PUL)]          # 额外信息


# 定义硬件输入结构体
class _HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),       # 消息代码
                ("wParamL", ctypes.c_short),    # 参数低位字
                ("wParamH", ctypes.c_ushort)]   # 参数高位字


# 定义鼠标输入结构体
class _MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),          # x轴位置或相对移动
                ("dy", ctypes.c_long),          # y轴位置或相对移动
                ("mouseData", ctypes.c_ulong),  # 鼠标数据（如滚轮）
                ("dwFlags", ctypes.c_ulong),    # 鼠标操作标志
                ("time", ctypes.c_ulong),       # 时间戳
                ("dwExtraInfo", _PUL)]          # 额外信息


# 定义输入联合体，可以包含键盘、鼠标或硬件输入
class _Input_I(ctypes.Union):
    _fields_ = [("ki", _KeyBdInput),            # 键盘输入
                ("mi", _MouseInput),            # 鼠标输入
                ("hi", _HardwareInput)]         # 硬件输入


# 定义输入结构体，包含输入类型和具体的输入数据
class _Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),       # 输入类型（1=键盘，2=鼠标，3=硬件
                ("ii", _Input_I)]               # 输入数据


class Key:
    Q = 0x10
    W = 0x11
    E = 0x12
    R = 0x13
    T = 0x14
    Y = 0x15
    U = 0x16
    I = 0x17
    O = 0x18
    P = 0x19
    A = 0x1E
    S = 0x1F
    D = 0x20
    F = 0x21
    G = 0x22
    H = 0x23
    J = 0x24
    K = 0x25
    L = 0x26
    # ; = 0x27
    Z = 0x2C
    X = 0x2D
    C = 0x2E
    V = 0x2F
    B = 0x30
    N = 0x31
    M = 0x32

    F1 = 0x3B
    F2 = 0x3C
    F3 = 0x3D
    F4 = 0x3E
    F5 = 0x3F
    F6 = 0x40
    F7 = 0x41
    F8 = 0x42
    F9 = 0x43
    F10 = 0x44
    F11 = 0x57
    F12 = 0x58

    # 功能键
    Esc = 0x01      # 退出键
    Tab = 0x0F      # 制表键
    Shift = 0x2A    # 上档键
    Ctrl = 0x1D     # 控制键
    Space = 0x39    # 空格键


class Keyboard:
    __activate_key: Dict = {}
    __pressed_keys: set = set()  # 存储当前被按下的按键

    @classmethod
    def Click(cls, key):
        def __click():
            cls.__Press(key)
            time.sleep(0.1)
            cls.__Release(key)
        threat = Thread(target=__click)
        threat.daemon = True
        threat.start()

    @classmethod
    def __Press(cls, key):
        extra = ctypes.c_ulong(0)
        ii_ = _Input_I()
        ii_.ki = _KeyBdInput(0, key, 0x0008, 0, ctypes.pointer(extra))
        x = _Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    @classmethod
    def __Release(cls, key):
        extra = ctypes.c_ulong(0)
        ii_ = _Input_I()
        ii_.ki = _KeyBdInput(0, key, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
        x = _Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    @classmethod
    def Press(cls, keys: List):
        """
        确保只有指定的按键列表处于按下状态

        参数:
            keys: 要处于按下状态的按键列表
        """
        # 释放不在新列表中的按键
        keys_to_release = cls.__pressed_keys - set(keys)
        for key in keys_to_release:
            cls.__Release(key)
            cls.__pressed_keys.remove(key)
        # 按下新列表中尚未按下的按键
        for key in keys:
            if key not in cls.__pressed_keys:
                cls.__Press(key)
                cls.__pressed_keys.add(key)

    @classmethod
    def Reset(cls):
        """释放所有按下的按键"""
        for key in list(cls.__pressed_keys):
            cls.__Release(key)
            cls.__pressed_keys.remove(key)

    @classmethod
    def GetPressedKeys(cls):
        """获取当前按下的按键列表"""
        return list(cls.__pressed_keys)




if __name__ == '__main__':
    import time
    from game import MonsterHunterWorld
    MonsterHunterWorld.Window.moveForeground()
    time.sleep(1)
    MonsterHunterWorld.Process.Suspend()
    time.sleep(1)
    MonsterHunterWorld.Process.Resume()
    Keyboard.Click(Key.F11)
    time.sleep(0.03)
    time.sleep(1)
    MonsterHunterWorld.Process.Suspend()
    time.sleep(1)
    MonsterHunterWorld.Process.Resume()
    time.sleep(2)
