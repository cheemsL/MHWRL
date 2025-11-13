# 游戏控制

### 模拟XBox手柄操作

代码路径：`game/control/gamepad.py`

| 操作     | 对应函数                  | 描述         |
| -------- | ------------------------- | ------------ |
| 锁定视角 | MHWGamepad.ViewLock()     | 点击RS       |
| 快速移动 | MHWGamepad.Move()         | 按下RB       |
| 翻滚     | MHWGamepad.Evada()        | 点击A        |
| 强化射击 | MHWGamepad.SlingerBurst() | 点击LT       |
| 蓄力     | MHWGamepad.Charge()       | 按下Y        |
| 蓄力斩   | MHWGamepad.ChargeSlash()  | 松开Y        |
| 冲撞攻击 | MHWGamepad.Tackle()       | 同时点击Y+B  |
| 横击     | MHWGamepad.SideBlow()     | 同时点击RT+Y |

