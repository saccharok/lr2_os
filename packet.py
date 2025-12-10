#пакет
from task import Task, TypeTask, StateTask
from enum import Enum
from dataclasses import dataclass, field
import json

#тип пакета
class TypePacket(Enum):
    MATH_PACK = "ВЫЧИСЛИТЕЛЬНЫЙ"
    INOUT_PACK = "ВВОД/ВЫВОД"
    EQUALS_PACK = "РАВНЫЙ ПО КОЛ-ВУ"
    BALANCED_PACK = "СБАЛАНСИРОВАННЫЙ"

@dataclass
class Packet:
    tasks: list = field(default_factory=list)  #список задач в пакете
    type: TypePacket = None  #тип пакета
    roundRobinQueue: list = field(default_factory=list)  #очередь Round Robin

    #инициализация пустого пакета или пакета из файла
    def __init__(self, filename: str = None):
        if filename:
            tasksList = self.createByJson(filename)
            self.tasks = tasksList if len(tasksList) > 0 else []
            if self.tasks:
                self.type = self.checkPacketType()
                self.roundRobinQueue = self.tasks.copy()
            else:
                self.type = None
                self.roundRobinQueue = []
        else:
            self.tasks = []
            self.type = None
            self.roundRobinQueue = []
    
    #автоматическое определение типа пакета   
    def checkPacketType(self):
        inout = 0
        math = 0
        totalMathTime = 0
        totalInoutTime = 0
        
        for task in self.tasks:  
            if task.type == TypeTask.MATH:
                math += 1
                totalMathTime += task.requiredTime
            else:
                inout += 1
                totalInoutTime += task.requiredTime
                
        if totalMathTime == totalInoutTime:
            return TypePacket.BALANCED_PACK
        
        elif math == inout:
            return TypePacket.EQUALS_PACK
        elif math > inout:
            return TypePacket.MATH_PACK
        else:
            return TypePacket.INOUT_PACK
    
    #получение следующей задачи Round Robin 
    def getNextTaskRr(self, currentTask: Task = None) -> Task:
        if not self.roundRobinQueue:
            return None
        
        #если текущая задача существует и не завершена
        if currentTask and currentTask.state != StateTask.READY:
            currentTask.contextSwitches += 1
            self.roundRobinQueue.append(currentTask)
            
        #удаляем все завершенные задачи из начала очереди
        while self.roundRobinQueue and self.roundRobinQueue[0]:
            task = self.roundRobinQueue[0]
            if task.state == StateTask.READY:
                self.roundRobinQueue.pop(0)
            else:
                break
                
        while self.roundRobinQueue:
            nextTask = self.roundRobinQueue.pop(0)
            
            #проверяем, что задача существует и не завершена
            if nextTask and nextTask.state != StateTask.READY:
                return nextTask
                
        return None
    
    #удаление завершенной задачи из очереди Round Robin
    def removeCompletedTask(self, task: Task):
        if task and task in self.roundRobinQueue:
            self.roundRobinQueue.remove(task)
    
    #получение длины очереди Round Robin
    def getRrQueueLength(self) -> int:
        return len([task for task in self.roundRobinQueue if task and task.state != StateTask.READY])
    
    #получить общее количество задач
    def getTasksCount(self):
        return len(self.tasks)
    
    #получить общую память пакета
    def getTasksMemory(self):
        memory = 0
        for task in self.tasks:
            memory += task.memory
        return memory
    
    #получить количество задача в состоянии ожидания выполнения
    def getWaitTasks(self):
        count = 0
        for task in self.tasks:
            if task.state == StateTask.WAIT:
                count += 1
        return count
    
    #получить количество задача в состоянии выполнения
    def getRunTasks(self):
        count = 0
        for task in self.tasks:
            if task.state == StateTask.RUN:
                count += 1
        return count
    
    #получить количество выполненых задач   
    def getReadyTasks(self):
        count = 0
        for task in self.tasks:
            if task.state == StateTask.READY:
                count += 1
        return count
    
    #получить количество математических задач
    def getMathTasks(self):
        count = 0
        for task in self.tasks:
            if task.type == TypeTask.MATH:
                count += 1
        return count    
    
    #получить количество задач ввода-вывода
    def getInOutTasks(self):
        count = 0
        for task in self.tasks:
            if task.type == TypeTask.INOUT:
                count += 1
        return count

    #создать пакет из json-файла
    @classmethod
    def createByJson(cls, filename: str):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)        
    
        tasksList = []
        for taskData in data['tasks']:
            task = Task(
                num=taskData['num'],
                type=TypeTask[taskData['type']],
                memory=taskData['memory']
            )
            tasksList.append(task)
        return tasksList
    
    #добавить задачу в пакет
    def addTask(self, task: Task):
        self.tasks.append(task)
        self.roundRobinQueue.append(task)
        self.type = self.checkPacketType()
    
    #удалить задачу по номеру
    def removeTask(self, taskNum: int):
        taskToRemove = None
        for task in self.tasks:
            if task.num == taskNum:
                taskToRemove = task
                break
        
        if taskToRemove:
            self.tasks.remove(taskToRemove)
            if taskToRemove in self.roundRobinQueue:
                self.roundRobinQueue.remove(taskToRemove)
            
            #переопределяем тип пакета после удаления задачи
            if self.tasks:
                self.type = self.checkPacketType()
            else:
                self.type = None
    
    #получить задачу по номеру
    def getTaskByNum(self, taskNum: int) -> Task:
        for task in self.tasks:
            if task.num == taskNum:
                return task
        return None
    
    #получить задачи по состоянию
    def getTasksByState(self, state: StateTask) -> list:
        return [task for task in self.tasks if task.state == state]
    
    #получить задачи по типу
    def getTasksByType(self, taskType: TypeTask) -> list:
        return [task for task in self.tasks if task.type == taskType]
    
    #получить общее время выполнения всех задач
    def getTotalExecutionTime(self) -> int:
        totalTime = 0
        for task in self.tasks:
            totalTime += task.requiredTime
        return totalTime
    
    #сбросить все задачи в состояние ожидания
    def resetAllTasks(self):
        for task in self.tasks:
            task.resetTask()
        self.roundRobinQueue = self.tasks.copy()
    
    #очистить пакет
    def clearPacket(self):
        self.tasks.clear()
        self.roundRobinQueue.clear()
        self.type = None