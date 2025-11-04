import atexit
from typing import (
    List,
    Tuple,
    Dict,
    Callable,
    Any,
    Optional
)


class QuitEvent:
    """
    退出事件
    当整个Python程序退出时，执行__CallList里的函数
    """
    __CallList: List[Tuple[Callable, Tuple[Any, ...], Dict[str, Any]]] = []

    @classmethod
    def Append(cls, func: Callable, *args: Any, **kwargs: Any) -> None:
        cls.__CallList.append((func, args, kwargs))

    @classmethod
    def Execute(cls):
        for func, args, kwargs in cls.__CallList:
            func(*args, **kwargs)


atexit.register(QuitEvent.Execute)

