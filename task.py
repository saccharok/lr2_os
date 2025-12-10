#задача
from enum import Enum
from dataclasses import dataclass

#типы задач
class TypeTask(Enum):
    MATH = "MATH"
    INOUT = "INOUT"

#состояние задачи
class StateTask(Enum):
    WAIT = "ОЖИДАНИЕ ВЫПОЛНЕНИЯ"
    RUN = "В ПРОЦЕССЕ ВЫПОЛНЕНИЯ"
    READY = "ВЫПОЛНЕНА"

@dataclass
class Task:
    num: int  #номер задачи
    type: TypeTask  #тип задачи
    memory: int  #объем памяти для задачи
    state: StateTask = StateTask.WAIT  #текущее состояние задачи
    executionTime: int = 0  #время, затраченное на выполнение
    requiredTime: int = 0  #общее требуемое время для выполнения
    remainingQuantum: int = 0  #оставшееся время в текущем кванте
    contextSwitches: int = 0  #количество переключений контекста для этой задачи

    #устанавливает требуемое время в зависимости от типа задачи
    def __post_init__(self):
        if self.type == TypeTask.MATH:
            self.requiredTime = 3  #MATH задачи выполняются 3 такта
        else:
            self.requiredTime = 2  #INOUT задачи выполняются 2 такта
    
    #изменение состояния задачи
    def changeState(self, stateTask: StateTask):
        self.state = stateTask
    
    #выполнение одного такта задачи
    def execute(self) -> bool:
        if self.state == StateTask.RUN:
            
            if self.remainingQuantum > 0:
                self.remainingQuantum -= 1
            
            self.executionTime += 1
            
            if self.executionTime >= self.requiredTime:
                self.changeState(StateTask.READY)
                return True
            
            if self.remainingQuantum <= 0:
                return False  
            
        return False  
    
    #выделение нового кванта задаче
    def allocateQuantum(self, quantumSize: int):
        self.remainingQuantum = quantumSize
        if self.state == StateTask.WAIT:
            self.changeState(StateTask.RUN)
    
    #проверка, выполняется ли задача
    def isRunning(self) -> bool:
        return self.state == StateTask.RUN
    
    #проверка, завершена ли задача
    def isCompleted(self) -> bool:
        return self.state == StateTask.READY
    
    #проверка, ожидает ли задача выполнения
    def isWaiting(self) -> bool:
        return self.state == StateTask.WAIT
    
    #получение оставшегося времени выполнения
    def getRemainingTime(self) -> int:
        return max(0, self.requiredTime - self.executionTime)
    
    #получение прогресса выполнения в процентах
    def getProgressPercent(self) -> float:
        if self.requiredTime > 0:
            return (self.executionTime / self.requiredTime) * 100
        return 0.0
    
    #сброс задачи в начальное состояние
    def resetTask(self):
        self.state = StateTask.WAIT
        self.executionTime = 0
        self.remainingQuantum = 0
        self.contextSwitches = 0