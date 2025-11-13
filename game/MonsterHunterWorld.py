import os
import sys
import cv2
import time
import psutil
import ctypes
import win32ui
import win32api
import win32con
import win32gui
import win32process
import numpy as np
from enum import (
    Enum
)
from typing import (
    Union,
    Tuple,
    Optional,
    List
)


class Process:
    __WindowHandle: int = 0     # 窗口句柄 (HWND)
    __ProcessId: int = 0        # 进程ID (PID)
    __ProcessHandle: int = 0    # 进程句柄 (Windows内核对象)
    __Process: Optional[psutil.Process] = None

    __Suspended: bool = False

    @classmethod
    def WindowHandle(cls) -> int:
        """ 窗口句柄 (HWND) """
        return cls.__WindowHandle

    @classmethod
    def ProcessHandle(cls) -> int:
        """ 进程句柄 (Windows内核对象) """
        return cls.__ProcessHandle

    @classmethod
    def ProcessId(cls) -> int:
        """ 进程ID (PID) """
        return cls.__ProcessId

    @classmethod
    def Suspend(cls) -> None:
        """ 挂起游戏进程 """
        # 如果游戏没有启动，直接返回
        if cls.__WindowHandle == 0:
            return
        # 如果已经被挂起，直接返回
        if cls.__Suspended:
            return
        # 挂起进程
        cls.__Process.suspend()
        cls.__Suspended = True

    @classmethod
    def Resume(cls) -> None:
        """ 恢复游戏进程 """
        # 如果游戏没有启动，直接返回
        if cls.__WindowHandle == 0:
            return
        # 如果游戏没有被挂起，不需要挂起，直接返回
        if not cls.__Suspended:
            return
        # 恢复进程
        cls.__Process.resume()

    @classmethod
    def Initialize(cls, WindowHandle: Optional[int] = None) -> None:
        """ 初始化进程ID、 进程句柄"""
        if WindowHandle is None:
            WindowHandle = cls.FindWindow()
        cls.__WindowHandle = WindowHandle
        if cls.__WindowHandle == 0:
            return
        cls.__ProcessId = win32process.GetWindowThreadProcessId(
            cls.__WindowHandle
        )[1]
        cls.__ProcessHandle = win32api.OpenProcess(
            0x1F0FFF, True, cls.__ProcessId
        )
        cls.__Process = psutil.Process(cls.ProcessId())

    @classmethod
    def FindWindow(cls) -> int:
        """
        寻找游戏窗口，如果返回值为0，则没有找到窗口
        """
        WindowHandle = win32gui.FindWindow(
            "MT FRAMEWORK", "MONSTER HUNTER: WORLD(421810)"
        )
        return WindowHandle


class Window:
    __DeviceContext = None        # 窗口的设备上下文句柄
    __TempDeviceContext = None
    __CompatibleDeviceContext = None    # 用来接收截图
    __Bitmap = None
    Width = 0
    Height = 0

    @classmethod
    def Initialize(cls) -> None:
        """初始化"""
        WindowHandle = Process.WindowHandle()
        cls.__DeviceContext = win32gui.GetWindowDC(WindowHandle)
        cls.__TempDeviceContext = win32ui.CreateDCFromHandle(cls.__DeviceContext)
        cls.Width, cls.Height = cls.WindowSize()
        cls.__CompatibleDeviceContext = cls.__TempDeviceContext.CreateCompatibleDC()
        cls.__Bitmap = win32ui.CreateBitmap()
        cls.__Bitmap.CreateCompatibleBitmap(
            cls.__TempDeviceContext, cls.Width, cls.Height
        )
        cls.__CompatibleDeviceContext.SelectObject(cls.__Bitmap)
        
    @classmethod
    def Screenshot(cls, resize: Optional[Tuple[int, int]] = None) -> Union[None, np.ndarray]:
        WindowHandle = Process.WindowHandle()
        if WindowHandle == 0:
            return None
        Width, Height = cls.WindowSize()
        if Width != cls.Width:
            cls.Initialize()
        
        WindowRect = win32gui.GetWindowRect(WindowHandle)
        ClientLeft, ClientTop = win32gui.ClientToScreen(
            WindowHandle, (0, 0)
        )
        OffsetX = round(ClientLeft - WindowRect[0])
        OffsetY = round(ClientTop - WindowRect[1])
        cls.__CompatibleDeviceContext.BitBlt(
            (0, 0),
            (Width, Height),
            cls.__TempDeviceContext,
            (OffsetX, OffsetY),
            win32con.SRCCOPY
        )
        SignedIntArray = cls.__Bitmap.GetBitmapBits(True)
        Image = np.frombuffer(SignedIntArray, dtype=np.uint8)
        Image.shape = (Height, Width, 4)
        Image = cv2.cvtColor(Image, cv2.COLOR_BGRA2RGB)
        if resize is not None:
            Image = cv2.resize(Image, resize, interpolation=cv2.INTER_AREA)
        return Image

    @classmethod
    def DevicePixelRatio(cls) -> float:
        dpi = cls.__TempDeviceContext.GetDeviceCaps(win32con.LOGPIXELSX)
        return dpi / 96.0

    @classmethod
    def WindowSize(cls) -> Tuple[int, int]:
        Left, Top, Right, Bottom = win32gui.GetClientRect(
            Process.WindowHandle()
        )
        Width = Right - Left
        Height = Bottom - Top
        return int(Width), int(Height)

    @classmethod
    def moveForeground(cls):
        win32gui.SetForegroundWindow(Process.WindowHandle())


class Memory:
    __Kernal32 = ctypes.windll.LoadLibrary(r"C:\Windows\System32\kernel32.dll")
    __Kernal32.VirtualAllocEx.argtypes = [
        ctypes.c_void_p,    # HANDLE hProcess
        ctypes.c_void_p,    # LPVOID lpAddress
        ctypes.c_size_t,    # SIZE_T dwSize
        ctypes.c_ulong,     # DWORD  flAllocationType
        ctypes.c_ulong      # DWORD  flProtect
    ]
    __Kernal32.VirtualAllocEx.restype = ctypes.c_void_p  # 返回地址指针

    __Kernal32.VirtualFreeEx.argtypes = [
        ctypes.c_void_p,  # HANDLE hProcess
        ctypes.c_void_p,  # LPVOID lpAddress
        ctypes.c_size_t,  # SIZE_T dwSize
        ctypes.c_ulong  # DWORD dwFreeType
    ]
    __Kernal32.VirtualFreeEx.restype = ctypes.c_int  # BOOL

    @classmethod
    def __ReadFromMemory(cls, address: hex, data, length: int):
        cls.__Kernal32.ReadProcessMemory(
            int(Process.ProcessHandle()),
            ctypes.c_void_p(address),
            ctypes.byref(data),
            length,
            None
        )
        return data.value

    @classmethod
    def __WriteIntoMemory(cls, address: hex, data, length: int):
        cls.__Kernal32.WriteProcessMemory(
            int(Process.ProcessHandle()),
            ctypes.c_void_p(address),
            ctypes.byref(data),
            length,
            None
        )

    @classmethod
    def ReadAddress(cls, *addresses: hex):
        address = addresses[0]
        for bias in addresses[1:]:
            address = cls.ReadLong(address)
            address += bias
        return address

    @classmethod
    def ReadByte(cls, address: hex):
        byte_data = ctypes.c_byte()
        return cls.__ReadFromMemory(address, byte_data, length=1)

    @classmethod
    def ReadShort(cls, address: hex):
        short_data = ctypes.c_short()
        return cls.__ReadFromMemory(address, short_data, length=2)

    @classmethod
    def ReadUnsignedShort(cls, address: hex):
        short_data = ctypes.c_ushort()
        return cls.__ReadFromMemory(address, short_data, length=2)

    @classmethod
    def ReadInt(cls, address: hex):
        int_data = ctypes.c_int()
        return cls.__ReadFromMemory(address, int_data, length=4)

    @classmethod
    def ReadLong(cls, address: hex):
        long_data = ctypes.c_int64()
        return cls.__ReadFromMemory(address, long_data, length=8)

    @classmethod
    def ReadFloat(cls, address: hex):
        float_data = ctypes.c_float()
        return cls.__ReadFromMemory(address, float_data, length=4)

    @classmethod
    def ReadString(cls, address: hex, length: int):
        data = ctypes.create_string_buffer(length)
        cls.__Kernal32.ReadProcessMemory(
            int(Process.ProcessHandle()),
            ctypes.c_void_p(address),
            data,
            length,
            None
        )
        return data.value.decode("utf-8", errors="ignore")

    @classmethod
    def WriteByte(cls, address: hex, data: hex):
        byte_data = ctypes.c_byte()
        byte_data.value = data
        cls.__WriteIntoMemory(address, byte_data, length=1)

    @classmethod
    def WriteInt(cls, address: hex, data: int):
        int_data = ctypes.c_int()
        int_data.value = data
        cls.__WriteIntoMemory(address, int_data, length=4)

    @classmethod
    def WriteFloat(cls, address: hex, data: float):
        float_data = ctypes.c_float()
        float_data.value = data
        cls.__WriteIntoMemory(address, float_data, length=4)

    @classmethod
    def WriteString(cls, address: hex, data: str):
        data = data.encode('utf-8')
        length = len(data) + 1
        string_data = ctypes.create_string_buffer(data, length)
        cls.__Kernal32.WriteProcessMemory(
            int(Process.ProcessHandle()),
            ctypes.c_void_p(address),
            string_data,
            length,
            None
        )

    @classmethod
    def WriteBytes(cls, address: hex, data: List[hex]):
        size = len(data)
        bytes_data = bytes([byte & 0xFF for byte in data])
        bytes_data = (ctypes.c_ubyte * size).from_buffer_copy(bytes_data)
        cls.__WriteIntoMemory(address, bytes_data, length=size)

    @classmethod
    def AllocMemory(cls, size: int = 2048, allocAddressRange: List = None):
        """在游戏进程里申请一片大小为size的内存"""
        address = None
        if allocAddressRange is None:
            allocAddressRange = [0x0]
        for nearAddress in allocAddressRange:
            address = cls.__Kernal32.VirtualAllocEx(
                int(Process.ProcessHandle()),
                ctypes.c_void_p(nearAddress),        # 在游戏内存附近申请内存
                size,
                0x1000 | 0x2000,    # MEM_COMMIT | MEM_RESERVE
                0x40,               # PAGE_EXECUTE_READWRITE
            )
            if address is not None:
                break
        return address

    @classmethod
    def ReleaseMemory(cls, address: hex):
        """释放申请的内存"""
        cls.__Kernal32.VirtualFreeEx(
            int(Process.ProcessHandle()),
            ctypes.c_void_p(address),
            0,
            0x8000
        )


class Chat:
    """向游戏中发送聊天信息"""

    # 文本颜色
    class TextColor(Enum):
        RED = "MOJI_RED_DEFAULT"  # FF0000 RGB(255, 0, 0)
        GREEN = "MOJI_GREEN_DEFAULT"  # 008000	RGB(0, 128, 0)
        BLUE = "MOJI_BLUE_DEFAULT"  # 0000FF RGB(0, 0, 255)
        PURPLE = "MOJI_PURPLE_DEFAULT"  # 9370DB	RGB(147, 112, 219)
        YELLOW = "MOJI_YELLOW_DEFAULT"  # FFFF00 RGB(255, 255, 0)
        ORANGE = "MOJI_ORANGE_DEFAULT"  # FFA500 RGB(255, 165, 0)
        LIGHTBLUE = "MOJI_LIGHTBLUE_DEFAULT"  # ADD8E6 RGB(173, 216, 230)
        LIGHTGREEN = "MOJI_LIGHTGREEN_DEFAULT"  # 90EE90	RGB(144, 238, 144)
        LIGHTYELLOW = "MOJI_LIGHTYELLOW_DEFAULT"  # FFFFE0 RGB(255, 255, 224)
        SLGREEN = "MOJI_SLGREEN_DEFAULT"  # D0F0C0 RGB(208, 240, 192)
        BROWN = "MOJI_BROWN_DEFAULT"  # 2B1700 or darker
        WHITE = "MOJI_WHITE_DEFAULT"  # FFFFFF	RGB(255, 255, 255)
        PALE = "MOJI_WHITE_DEFAULT2"  #DCDCDC RGB(220, 220, 220)
        WHITE_SELECTED = "MOJI_WHITE_SELECTED2"  # C0C0C0 RGB(192, 192, 192)
        BLACK = "MOJI_BLACK_DEFAULT"  # 000000 RGB(0, 0, 0)

    # 发送聊天信息
    @classmethod
    def SendMessage(
            cls,
            message: str,
            color: Optional[TextColor] = None,
            size: Optional[int] = None
    ):
        if size is not None:
            size = min(max(size, 20), 30)
            message = f"<SIZE {size}>{message}</SIZE>"
        if color is not None:
            message = f"<STYL {color}>{message}</STYL>"
        message = ((message.encode("utf-8"))[:127]).decode("utf-8")
        message_address = Memory.ReadAddress(0x1451C4640, 0x13FD0, 0x28F8 + 0x165)
        send_address = Memory.ReadAddress(0x1451C4640, 0x13FD0, 0x325E)
        Memory.WriteString(message_address, message)
        Memory.WriteByte(send_address, 1)


Process.Initialize()
Window.Initialize()