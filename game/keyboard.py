import time
import ctypes
from threading import Thread


_SendInput = ctypes.windll.user32.SendInput
_PUL = ctypes.POINTER(ctypes.c_ulong)


class _KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", _PUL)]
class _HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]
class _MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", _PUL)]
class _Input_I(ctypes.Union):
    _fields_ = [("ki", _KeyBdInput),
                ("mi", _MouseInput),
                ("hi", _HardwareInput)]
class _Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", _Input_I)]


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
    Esc = 0x01
    Tab = 0x0F
    Shift = 0x2A
    Ctrl = 0x1D
    Space = 0x39


class Keyboard:

    @classmethod
    def Click(cls, key):
        def __click():
            cls.PressDown(key)
            time.sleep(0.1)
            cls.Release(key)
        threat = Thread(target=__click)
        threat.daemon = True
        threat.start()

    @classmethod
    def PressDown(cls, key):
        extra = ctypes.c_ulong(0)
        ii_ = _Input_I()
        ii_.ki = _KeyBdInput(0, key, 0x0008, 0, ctypes.pointer(extra))
        x = _Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    @classmethod
    def Release(cls, key):
        extra = ctypes.c_ulong(0)
        ii_ = _Input_I()
        ii_.ki = _KeyBdInput(0, key, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
        x = _Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


if __name__ == '__main__':
    Keyboard.Click(Key.Space)