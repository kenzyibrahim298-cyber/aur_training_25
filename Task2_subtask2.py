from time import time 
from rich.console import Console

console = Console()

def send_Msg(msg):
    if isinstance(msg, BaseMsg): 
        console.print(msg, style=msg.style)
    else:
        print(msg)



class BaseMsg:
    def __init__(self, data: str):
        self._data = data

    @property
    def style(self)->str:
        return''
   
    @property 
    def data(self):
        return self._data
    
    def __str__(self):
        return self._data
    
    def __len__(self):
        return len(str(self))
    
    def __eq__(self, other):
        if isinstance(other, BaseMsg):
            return str(self) == str(other)
        elif isinstance(other, str):
            return str(self) == other
        else:
            return NotImplemented


    def __add__(self, other):
        if isinstance(other, BaseMsg):
            other_raw = other.data
        elif isinstance(other, str):
            other_raw = other
        else:
            return NotImplemented
            return self.__class__(self.data + other_raw)


class LogMsg(BaseMsg):
    def __init__(self, data):
        super().__init__(data)
        self._timestamp: int = int(time())

    @property
    def style(self)->str:
        return 'black on yellow'
    
    def __str__(self):
        return f"[{self._timestamp}] {self.data}"


class WarnMsg(LogMsg):

     @property
     def style(self)->str:
        return 'white on red'
    
     def __str__(self):
        return f"[Warning][{self._timestamp}] {self.data}"


if __name__ == 'main':
        m1 = BaseMsg('Normal message')
        m2 = LogMsg('log')
        m3 = WarnMsg ('Warning')
        send_Msg(m1)
        send_Msg(m2)
        send_Msg(m3)
    



    
    