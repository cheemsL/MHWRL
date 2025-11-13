import vgamepad
import time
from threading import Thread
from public.tools import QuitEvent

class VX360Gamepad:
    # 创建一个虚拟XBOX 360手柄
    __controller = vgamepad.VX360Gamepad()

    #
    __click_intervel = 0.1 # 0.1秒

    class Button:
        UP = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP                      # 方向键上键 0x0001
        DOWN = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN                  # 方向键下键 0x0002
        LEFT = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT                  # 方向键左键 0x0004
        RIGHT = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT                # 方向键右键 0x0008

        START = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_START                     # 开始键（通常用于暂停/菜单 0x0010
        BACK = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_BACK                       # 返回键（通常用于返回/地图）0x0020
        GUIDE = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE                     # Xbox 中心键 0x0400

        LEFT_THUMB = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB           # 左摇杆按下（LS 按钮）0x0040
        RIGHT_THUMB = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB         # 右摇杆按下（RS 按钮）0x0080
        LEFT_SHOULDER = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER     # 左肩键（LB 键，通常用于次要操作）0x0100
        RIGHT_SHOULDER = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER   # 右肩键（RB 键，通常用于主要操作）0x0200

        A = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A                             # A 0x1000
        B = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B                             # B 0x2000
        X = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X                             # X 0x4000
        Y = vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_Y                             # Y 0x8000


    @classmethod
    def Press(cls, button:hex):
        """
        按下按钮: VX360Gamepad.Button
        """
        cls.__controller.press_button(button)
        cls.__controller.update()

    @classmethod
    def Release(cls, button:hex):
        """
        松开按钮: VX360Gamepad.Button
        """
        cls.__controller.release_button(button)
        cls.__controller.update()

    @classmethod
    def Click(cls, button):
        """
        点击按钮: VX360Gamepad.Button
        """
        def __click():
            cls.Press(button)
            time.sleep(cls.__click_intervel)
            cls.Release(button)
        threat = Thread(target=__click)
        threat.daemon = True
        threat.start()

    @classmethod
    def LeftJoystick(cls, x:float, y:float):
        """
        -1 <= x <= 1, -1 <= y <= 1
        移动方向:
            y > 0: 前
            y < 0: 后
            x > 0: 右
            x < 0: 左
        """
        cls.__controller.left_joystick_float(x, y)
        cls.__controller.update()

    @classmethod
    def RightJoystick(cls, x:float, y:float):
        """
        视角方向: -1 <= x <= 1, -1 <= y <= 1
        """
        cls.__controller.right_joystick_float(x, y)
        cls.__controller.update()

    @classmethod
    def LeftTrigger(cls, value:float):
        cls.__controller.left_trigger_float(value)
        cls.__controller.update()

    @classmethod
    def RightTrigger(cls, value:float):
        cls.__controller.right_trigger_float(value)
        cls.__controller.update()

    @classmethod
    def ClickLeftTrigger(cls):
        def __click():
            cls.LeftTrigger(1.)
            time.sleep(cls.__click_intervel)
            cls.LeftTrigger(0.)
        threat = Thread(target=__click)
        threat.daemon = True
        threat.start()

    @classmethod
    def ClickRightTrigger(cls):
        def __click():
            cls.RightTrigger(1.)
            time.sleep(cls.__click_intervel)
            cls.RightTrigger(0.)
        threat = Thread(target=__click)
        threat.daemon = True
        threat.start()

    @classmethod
    def Reset(cls):
        cls.__controller.reset()

    @classmethod
    def Delete(cls):
        cls.Reset()
        del cls.__controller


class MHWGamepad:

    @classmethod
    def ViewLock(cls):
        """视角锁定，点击RS"""
        VX360Gamepad.Click(VX360Gamepad.Button.RIGHT_THUMB)

    @classmethod
    def Move(cls):
        """快速移动，按下RB"""
        VX360Gamepad.Press(VX360Gamepad.Button.RIGHT_SHOULDER)

    @classmethod
    def Evada(self):
        """翻滚，点击A"""
        VX360Gamepad.Click(VX360Gamepad.Button.A)

    @classmethod
    def SlingerBurst(self):
        """强化射击，点击LT"""
        VX360Gamepad.ClickLeftTrigger()

    @classmethod
    def Charge(cls):
        """蓄力，按下Y"""
        VX360Gamepad.Press(VX360Gamepad.Button.Y)

    @classmethod
    def ChargeSlash(cls):
        """蓄力，斩松开Y"""
        VX360Gamepad.Release(VX360Gamepad.Button.Y)

    @classmethod
    def Tackle(cls):
        """冲撞攻击，同时点击Y+B"""
        VX360Gamepad.Click(VX360Gamepad.Button.B)
        VX360Gamepad.Click(VX360Gamepad.Button.Y)

    @classmethod
    def SideBlow(cls):
        """横击，同时点击RT+Y"""
        VX360Gamepad.Click(VX360Gamepad.Button.Y)
        VX360Gamepad.ClickRightTrigger()


QuitEvent.Append(VX360Gamepad.Delete)


if __name__ == '__main__':
    # 移动
    time.sleep(1)
    MHWGamepad.ViewLock()
    time.sleep(1)