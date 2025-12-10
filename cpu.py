#процессор
from packet import Task, StateTask, TypeTask
from dataclasses import dataclass, field
from enum import Enum

#состояние процессора
class StateCPU(Enum):
    IDLE = "ПРОСТОЙ"
    EXECUTING = "ВЫПОЛНЕНИЕ ВЫЧИСЛЕНИЙ"
    IO_WAIT = "ОЖИДАНИЕ ЗАВЕРШЕНИЯ ВВОДА/ВЫВОДА"
    OVERLOADED = "ПЕРЕГРУЗКА"

@dataclass
class CPU:
    state: StateCPU = StateCPU.IDLE  #текущее состояние процессора
    currentTask: Task = None  #задача выполняемая в данный момент
    quantumSize: int = 1  #размер кванта времени
    remainingQuantum: int = 0  #оставшееся время в текущем кванте
    contextSwitchCount: int = 0  #счетчик переключений контекста
    clockCounter: int = 0  #счетчик тактов
    
    #установка размера кванта
    def setQuantumSize(self, quantum: int):
        if quantum > 0:
            self.quantumSize = quantum
            self.remainingQuantum = quantum
    
    #проверка исчерпан ли квант
    def isQuantumExhausted(self) -> bool:
        return self.remainingQuantum <= 0
    
    #выделение кванта задаче
    def allocateQuantumToTask(self, task: Task):
        if task:
            task.allocateQuantum(self.quantumSize)
            self.remainingQuantum = self.quantumSize
            self.currentTask = task
            
            if task.type == TypeTask.MATH:
                self.state = StateCPU.EXECUTING
            else:
                self.state = StateCPU.IO_WAIT
    
    #выполнение одного такта текущей задачи
    def executeTick(self) -> bool:
        if self.currentTask is None:
            self.state = StateCPU.IDLE
            return False
        
        self.clockCounter += 1
        
        taskCompleted = self.currentTask.execute()
        
        if self.remainingQuantum > 0:
            self.remainingQuantum -= 1
            
        if taskCompleted:
            self.completeTask()
            return True
        
        return False
    
    #завершение текущей задачи
    def completeTask(self):
        if self.currentTask:
            self.currentTask.changeState(StateTask.READY)
            self.currentTask = None
            self.state = StateCPU.IDLE
            self.remainingQuantum = 0
    
    #принудительное вытеснение задачи (исчерпан квант)
    def preemptTask(self) -> Task:
        if self.currentTask and self.currentTask.state != StateTask.READY:
            task = self.currentTask
            self.contextSwitchCount += 1
            self.currentTask = None
            self.state = StateCPU.IDLE
            self.remainingQuantum = 0
            return task
        return None
    
    #проверка занят ли процессор
    def isBusy(self) -> bool:
        return self.currentTask is not None and self.currentTask.state == StateTask.RUN
    
    #проверка простаивает ли процессор
    def isIdle(self) -> bool:
        return self.currentTask is None or self.state == StateCPU.IDLE
    
    #получение оставшегося времени выполнения текущей задачи
    def getRemainingTime(self) -> int:
        if self.currentTask is None:
            return 0
        return max(0, self.currentTask.requiredTime - self.currentTask.executionTime)
    
    #назначить задачу на выполнение
    def useToDoTask(self, task: Task):
        task.changeState(StateTask.RUN)
        self.currentTask = task
        
        if task.type == TypeTask.MATH:
            self.state = StateCPU.EXECUTING
        else:
            self.state = StateCPU.IO_WAIT
    
    #выполнение задачи
    def doTask(self, task: Task):
        task.changeState(StateTask.READY)
        self.currentTask = None
    
    #сброс процессора в начальное состояние
    def resetCPU(self):
        self.state = StateCPU.IDLE
        self.currentTask = None
        self.remainingQuantum = 0
        self.contextSwitchCount = 0
        self.clockCounter = 0
    
    #получение текущего прогресса выполнения задачи в процентах
    def getTaskProgressPercent(self) -> float:
        if self.currentTask:
            return self.currentTask.getProgressPercent()
        return 0.0
    
    #получение информации о текущей задаче
    def getCurrentTaskInfo(self) -> str:
        if self.currentTask:
            return f"Задача {self.currentTask.num} ({self.currentTask.type.value}): " \
                   f"{self.currentTask.executionTime}/{self.currentTask.requiredTime}"
        return "Нет активной задачи"
    
    #получение количества выполненных переключений контекста
    def getContextSwitchCount(self) -> int:
        return self.contextSwitchCount
    
    #увеличение счетчика переключений контекста
    def incrementContextSwitchCount(self):
        self.contextSwitchCount += 1
    
    #получение общего количества тактов
    def getClockCounter(self) -> int:
        return self.clockCounter
    
    #проверка, выполняется ли MATH задача
    def isExecutingMath(self) -> bool:
        return self.state == StateCPU.EXECUTING
    
    #проверка, ожидает ли INOUT задача
    def isWaitingIO(self) -> bool:
        return self.state == StateCPU.IO_WAIT
    
    #проверка, перегружен ли процессор
    def isOverloaded(self) -> bool:
        return self.state == StateCPU.OVERLOADED
    
    #установка состояния перегрузки
    def setOverloadedState(self):
        self.state = StateCPU.OVERLOADED
    
    #снятие состояния перегрузки
    def clearOverloadedState(self):
        if self.currentTask:
            if self.currentTask.type == TypeTask.MATH:
                self.state = StateCPU.EXECUTING
            else:
                self.state = StateCPU.IO_WAIT
        else:
            self.state = StateCPU.IDLE