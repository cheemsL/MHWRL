from typing import List
from game import MonsterHunterWorld


def getJumpInstruction(fromAddress: hex, toAddress: hex):
    offset = toAddress - (fromAddress + 5)  # jmp rel32
    offset = offset & 0xFFFFFFFF  # 转为 32-bit 无符号表示（两补数）
    bytes = offset.to_bytes(4, 'little')
    instruction = [0xE9] + [int(byte) for byte in bytes]
    return instruction


class BaseModel:

    allocAddressRange = [
        0x130000000, 0x138000000,
        0x140000000, 0x148000000,
        0x150000000, 0x158000000,
        0x160000000
    ]

    def __init__(
            self,
            startAddress: hex,
            originInstructions: List[hex],
            targetInstruction: List[hex]
    ):
        self.startAddress = startAddress
        self.endAddress = self.startAddress + len(originInstructions)
        self.originInstructions = originInstructions
        self.targetInstruction = targetInstruction
        self.allocAddress = None
        self.targetInstructionSize = len(self.targetInstruction)
        self.allocMemorySize = (self.targetInstructionSize // 64 + 2) * 64

    def setEnable(self, enable: bool) -> None:
        if enable:
            # 分配内存
            self.allocAddress = MonsterHunterWorld.Memory.AllocMemory(
                self.allocMemorySize,
                self.allocAddressRange
            )
            if self.allocAddress is None:
                print(f"Debug.{self.__class__.__name__}.setEnable({enable}) 分配内存失败")
                return
            print(f"Debug.{self.__class__.__name__}.setEnable({enable}) 分配内存:{hex(self.allocAddress)}")
            # 生成跳转过去指令
            jumpBackInstruction = getJumpInstruction(
                fromAddress=self.allocAddress + self.targetInstructionSize,
                toAddress=self.endAddress
            )
            # 完整指令
            instruction = self.targetInstruction.copy() + jumpBackInstruction
            # 写入内存
            MonsterHunterWorld.Memory.WriteBytes(self.allocAddress, instruction)
            # 生成跳转回去指令
            jumpIntoInstruction = getJumpInstruction(
                fromAddress=self.startAddress,
                toAddress=self.allocAddress
            )
            # 写入游戏内存
            MonsterHunterWorld.Memory.WriteBytes(self.startAddress, jumpIntoInstruction)
        else:
            # 游戏内存数据归滚
            MonsterHunterWorld.Memory.WriteBytes(self.startAddress, self.originInstructions)
            # 释放分配内存
            if self.allocAddress is None:
                return
            MonsterHunterWorld.Memory.ReleaseMemory(self.allocAddress)
            self.allocAddress = None


# 保持最后一滴血
KeepLive = BaseModel(
    # MonsterHunterWorld.exe+1216979 - F3 0F11 41 64         - movss [rcx+64],xmm0
    startAddress=0x141216979,
    # MonsterHunterWorld.exe+1216979 - F3 0F11 41 64         - movss [rcx+64],xmm0
    originInstructions=[
        0xF3, 0x0F, 0x11, 0x41, 0x64
    ],
    # 50                    - push rax
    # F3 48 0F2D C0         - cvtss2si rax,xmm0
    # 48 83 F8 01           - cmp rax,01
    # 0F8D 0F000000         - jnl 13FFD001F
    # 48 B8 0100000000000000 - mov rax,0000000000000001
    # F3 48 0F2A C0         - cvtsi2ss xmm0,rax
    # 58                    - pop rax
    # F3 0F11 41 64         - movss [rcx+64],xmm0
    targetInstruction=[
        0x50,
        0xF3, 0x48, 0x0F, 0x2D, 0xC0,
        0x48, 0x83, 0xF8, 0x01,
        0x0F, 0x8D, 0x0F, 0x00, 0x00, 0x00,
        0x48, 0xB8, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0xF3, 0x48, 0x0F, 0x2A, 0xC0,
        0x58,
        0xF3, 0x0F, 0x11, 0x41, 0x64,
    ]
)


# 无碰撞检测
CollisionFree = BaseModel(
    # MonsterHunterWorld.exe+1F51810 - E8 3B662CFF           - call MonsterHunterWorld.exe+1217E50
    startAddress=0x141F51810,
    # MonsterHunterWorld.exe+1F51810 - E8 3B662CFF           - call MonsterHunterWorld.exe+1217E50
    originInstructions=[0xE8, 0x3B, 0x66, 0x2C, 0xFF],
    #
    targetInstruction=[]
)


# 动作帧暂停
ActionFreeze = BaseModel(
    # MonsterHunterWorld.exe+224DE89 - F3 0F11 46 5C
    startAddress=0x14224DE89,
    # MonsterHunterWorld.exe+224DE89 - F3 0F11 46 5C
    originInstructions=[0xF3, 0x0F, 0x11, 0x46, 0x5C],
    #
    targetInstruction=[]
)


if __name__ == '__main__':
    ActionFreeze.setEnable(True)
    input()
    ActionFreeze.setEnable(False)