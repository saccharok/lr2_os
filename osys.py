#операционная система
from packet import Packet, Task, TypeTask, StateTask
from cpu import CPU, StateCPU
from dataclasses import dataclass, field
from typing import List, Optional, Callable

@dataclass
class OS:
    ram: int                                                            #объем оперативной памяти в ГБ
    maxBlocksCount: int                                               #максимальное количество разделов памяти
    quantumSize: int = 1                                               #размер кванта времени для Round Robin
    packet: Optional[Packet] = None                                     #пакет задач для выполнения
    memoryBlocks: List[Optional[Task]] = field(default_factory=list)   #разделы памяти с задачами
    waitQueue: List[Task] = field(default_factory=list)                #очередь ожидающих задач
    readyQueue: List[Task] = field(default_factory=list)               #очередь завершенных задач
    runningTasks: List[Task] = field(default_factory=list)             #список выполняющихся задач
    ioWaitTasks: List[Task] = field(default_factory=list)             #список задач, ожидающих ввод/вывод
    cpu: CPU = field(default_factory=CPU)                               #процессор системы
    currentTact: int = 0                                               #текущий такт выполнения
    outputCallback: Optional[Callable[[str], None]] = None             #функция для вывода информации
    
    #статистика Round Robin
    rrStatistics: dict = field(default_factory=lambda: {
        'contextSwitches': 0,
        'quantumExhaustions': 0,
        'tasksCompletedInQuantum': 0,
        'rrQueueLengthHistory': [],
        'quantumEfficiency': []
    })
    
    #история выполнения для статистики
    history: dict = field(default_factory=lambda: {
        'tacts': [],
        'memoryBlocksUsed': [],
        'cpuStates': [],
        'taskStates': {'WAIT': [], 'RUN': [], 'READY': []},
        'memoryUsage': [],
        'taskTypes': {'MATH': 0, 'INOUT': 0},
        'rrQueueLength': []
    })
    
    #счетчики состояний процессора
    cpuStateCounts: dict = field(default_factory=lambda: {
        "ПРОСТОЙ": 0,
        "ВЫПОЛНЕНИЕ ВЫЧИСЛЕНИЙ": 0,
        "ОЖИДАНИЕ ЗАВЕРШЕНИЯ ВВОДА/ВЫВОДА": 0,
        "ПЕРЕГРУЗКА": 0
    })
    
    #инициализация системы
    def initialize(self, jsonFile: str):
        self.packet = Packet(jsonFile)
        self.waitQueue = self.packet.tasks.copy()
        self.memoryBlocks = [None] * self.maxBlocksCount
        self.currentTact = 0
        
        self.cpu.setQuantumSize(self.quantumSize)
        self.cpu.state = StateCPU.IDLE
        
        self.rrStatistics = {
            'contextSwitches': 0,
            'quantumExhaustions': 0,
            'tasksCompletedInQuantum': 0,
            'rrQueueLengthHistory': [],
            'quantumEfficiency': []
        }
        
        self.history = {
            'tacts': [],
            'memoryBlocksUsed': [],
            'cpuStates': [],
            'taskStates': {'WAIT': [], 'RUN': [], 'READY': []},
            'memoryUsage': [],
            'taskTypes': {
                'MATH': self.packet.getMathTasks(),
                'INOUT': self.packet.getInOutTasks()
            },
            'rrQueueLength': []
        }
        
        self.cpuStateCounts = {
            "ПРОСТОЙ": 0,
            "ВЫПОЛНЕНИЕ ВЫЧИСЛЕНИЙ": 0,
            "ОЖИДАНИЕ ЗАВЕРШЕНИЯ ВВОДА/ВЫВОДА": 0,
            "ПЕРЕГРУЗКА": 0
        }
    
    #планирование Round Robin
    def roundRobinSchedule(self):
        needSwitch = False
        
        if self.cpu.currentTask:
            if self.cpu.currentTask.state == StateTask.READY:
                needSwitch = True
                self.rrStatistics['tasksCompletedInQuantum'] += 1
            elif self.cpu.isQuantumExhausted():
                needSwitch = True
                self.rrStatistics['quantumExhaustions'] += 1
        elif self.cpu.state == StateCPU.IDLE:
            needSwitch = True
            
        if needSwitch and self.packet:
            currentTask = self.cpu.currentTask
            nextTask = self.packet.getNextTaskRr(currentTask)
            
            if nextTask:  
                self.cpu.allocateQuantumToTask(nextTask)
                self.rrStatistics['contextSwitches'] += 1
                
                if nextTask not in self.runningTasks:
                    self.runningTasks.append(nextTask)
                    
                if nextTask.type == TypeTask.INOUT and nextTask not in self.ioWaitTasks:
                    self.ioWaitTasks.append(nextTask)
                    
                self.output(f"Round Robin: переключение на задачу {nextTask.num} ({nextTask.type.value})")
            else:
                if currentTask and currentTask.state != StateTask.READY:
                    self.output(f"Round Robin: нет новых задач, продолжаем выполнение задачи {currentTask.num}")
                else:
                    self.output("Round Robin: нет доступных задач для выполнения")
                    self.cpu.currentTask = None
                    self.cpu.state = StateCPU.IDLE
    
    #выполнение одного такта с Round Robin
    def runTact(self):
        self.currentTact += 1
        
        self.freeCompletedTasks()
        
        self.loadTasksToMemory()
        
        self.roundRobinSchedule()
        if self.cpu.currentTask:
            self.executeCurrentTask()
            
        self.manageCpuStates()
        
        self.collectStatistics()
        
        if self.currentTact % 50 == 0 or self.currentTact <= 5:
            if self.outputCallback:
                usedBlocks = sum(1 for block in self.memoryBlocks if block is not None)
                completed = len(self.readyQueue)
                total = len(self.packet.tasks) if self.packet else 0
                
                info = f"Такт {self.currentTact}: завершено {completed}/{total}, " \
                    f"память {usedBlocks}/{self.maxBlocksCount}"
                
                if self.cpu.currentTask:
                    info += f", задача {self.cpu.currentTask.num}"
                
                self.outputCallback(info)
    
    #выполнение только текущей задачи (выбранной Round Robin) - ИСПРАВЛЕННЫЙ МЕТОД
    def executeCurrentTask(self):
        if not self.cpu.currentTask:
            self.output("Нет активной задачи для выполнения")
            return
            
        if self.cpu.currentTask.state == StateTask.RUN:
            task_num = self.cpu.currentTask.num
            task_type = self.cpu.currentTask.type.value
            current_task_ref = self.cpu.currentTask 
            
            completed = self.cpu.executeTick()
            
            if completed:
                self.output(f"Задача {task_num} ({task_type}) завершена!")

                if current_task_ref in self.runningTasks:
                    self.runningTasks.remove(current_task_ref)
                if current_task_ref in self.ioWaitTasks:
                    self.ioWaitTasks.remove(current_task_ref)
                    
                if self.packet:
                    self.packet.removeCompletedTask(current_task_ref)
                    
                for i, task in enumerate(self.memoryBlocks):
                    if task == current_task_ref:
                        self.memoryBlocks[i] = None
                        break
                
                self.readyQueue.append(current_task_ref)
                
            else:
                if self.cpu.currentTask:
                    self.output(f"Задача {self.cpu.currentTask.num} ({self.cpu.currentTask.type.value}) выполняется: "
                            f"{self.cpu.currentTask.executionTime}/{self.cpu.currentTask.requiredTime} тактов, "
                            f"квант: {self.cpu.remainingQuantum}")
                else:
                    self.output(f"Задача {task_num} ({task_type}) была вытеснена")
        elif self.cpu.currentTask:
            self.output(f"Задача {self.cpu.currentTask.num} в состоянии {self.cpu.currentTask.state.value}")
        else:
            self.output("Нет активной задачи для выполнения")
    
    #загрузка задачи в раздел с добавлением в очередь Round Robin
    def loadTasksToMemory(self) -> bool:
        loaded = False
    
        for i in range(len(self.memoryBlocks)):
            if self.memoryBlocks[i] is None and self.waitQueue:
                task = self.waitQueue.pop(0)
                self.memoryBlocks[i] = task
                self.output(f"Задача {task.num} ({task.type.value}) загружена в раздел {i+1}")
                loaded = True
                
                if self.packet and task not in self.packet.roundRobinQueue:
                    self.packet.roundRobinQueue.append(task)
                
                currentUsedBlocks = sum(1 for block in self.memoryBlocks if block is not None)
                if currentUsedBlocks > self.maxBlocksCount:
                    self.output(f"ПРЕДУПРЕЖДЕНИЕ: Превышено максимальное количество разделов! "
                               f"({currentUsedBlocks} > {self.maxBlocksCount})")                   
        return loaded
    
    #сбор статистики с учетом Round Robin
    def collectStatistics(self):
        usedBlocks = sum(1 for block in self.memoryBlocks if block is not None)
        self.history['memoryBlocksUsed'].append(usedBlocks)
        
        currentState = self.cpu.state.value
        self.history['cpuStates'].append(currentState)
        
        waitCount = len(self.waitQueue)
        runCount = len([task for task in self.runningTasks if task.state == StateTask.RUN])
        readyCount = len(self.readyQueue)
        
        self.history['taskStates']['WAIT'].append(waitCount)
        self.history['taskStates']['RUN'].append(runCount)
        self.history['taskStates']['READY'].append(readyCount)
        
        usedMemoryPercent = (usedBlocks / self.maxBlocksCount) * 100
        freeMemoryPercent = max(0, 100 - usedMemoryPercent)
        self.history['memoryUsage'].append(freeMemoryPercent)
        
        self.history['tacts'].append(self.currentTact)
        
        if self.packet:
            rrLength = self.packet.getRrQueueLength()
            self.history['rrQueueLength'].append(rrLength)
            
            if self.currentTact > 0:
                efficiency = (self.rrStatistics['tasksCompletedInQuantum'] / 
                            max(1, self.rrStatistics['contextSwitches'])) * 100
                self.rrStatistics['quantumEfficiency'].append(efficiency)
                
        currentState = self.cpu.state.value
        if currentState in self.cpuStateCounts:
            self.cpuStateCounts[currentState] += 1
    
    #получение статистики Round Robin
    def getRoundRobinStatistics(self):
        return self.rrStatistics.copy()
    
    #изменение количества разделов памяти
    def changeMemoryBlocksCount(self, newCount: int):
        if newCount <= 0:
            raise ValueError("Количество разделов памяти должно быть положительным")
        
        oldCount = self.maxBlocksCount
        self.maxBlocksCount = newCount
        
        currentTasks = [task for task in self.memoryBlocks if task is not None]
        
        newMemoryBlocks = [None] * newCount
        
        tasksToKeep = min(len(currentTasks), newCount)
        for i in range(tasksToKeep):
            newMemoryBlocks[i] = currentTasks[i]
            
        for i in range(tasksToKeep, len(currentTasks)):
            task = currentTasks[i]
            if task in self.runningTasks:
                self.runningTasks.remove(task)
            if task in self.ioWaitTasks:
                self.ioWaitTasks.remove(task)
            self.waitQueue.insert(0, task)  
        
        self.memoryBlocks = newMemoryBlocks
        
        self.updateCpuStateAfterMemoryChange()
        
        if self.outputCallback:
            self.output(f"Изменено количество разделов памяти: {oldCount} -> {newCount}")
            if len(currentTasks) > newCount:
                self.output(f"Возвращено в очередь: {len(currentTasks) - newCount} задач")
    
    #обновление состояния процессора после изменения настроек памяти
    def updateCpuStateAfterMemoryChange(self):
        usedBlocks = sum(1 for block in self.memoryBlocks if block is not None)
        
        if usedBlocks > self.maxBlocksCount:
            self.changeCpuState(StateCPU.OVERLOADED, "(перегрузка после изменения памяти)")
        elif self.cpu.state == StateCPU.OVERLOADED and usedBlocks <= self.maxBlocksCount:            
            self.changeToNormalState()
    
    #проверка и автоматическая настройка количества разделов памяти
    def checkAndAdjustMemoryBlocks(self):
        currentLoad = len(self.runningTasks)        
        if currentLoad < self.maxBlocksCount // 2 and self.maxBlocksCount > 2:
            newCount = max(self.maxBlocksCount - 1, 2)
            self.changeMemoryBlocksCount(newCount)
            return True
                
        return False
    
    #установка функции обратного вызова для вывода информации
    def setOutputCallback(self, callback: Callable[[str], None]):
        self.outputCallback = callback
    
    #вывод сообщения через установленный флаг
    def output(self, message: str):
        if self.outputCallback:
            try:
                self.outputCallback(message)
            except Exception as e:
                print(f"Ошибка вывода: {e}")
    
    #изменение состояние процессора с выводом информации о переходе из одного состояния в другое
    def changeCpuState(self, newState: StateCPU, reason: str = ""):
        oldState = self.cpu.state
        if oldState != newState:
            self.cpu.state = newState
            self.output(f"ПЕРЕКЛЮЧЕНИЕ CPU: {oldState.value} -> {newState.value} {reason}")
            
            currentUsedBlocks = sum(1 for block in self.memoryBlocks if block is not None)
            mathCount = len([task for task in self.runningTasks if task.type == TypeTask.MATH and task.state == StateTask.RUN])
            ioCount = len([task for task in self.runningTasks if task.type == TypeTask.INOUT and task.state == StateTask.RUN])
            self.output(f"Отладочная информация: Используется разделов={currentUsedBlocks}/{self.maxBlocksCount}, MATH={mathCount}, INOUT={ioCount}")
    
    #возвращение счетчика состояний процессора для графика
    def getCpuStateCounts(self):
        return self.cpuStateCounts.copy()
    
    #управление переключением состояний процессора на основе текущей ситуации
    def manageCpuStates(self):
        self.checkOverload()
        
        if self.cpu.state != StateCPU.OVERLOADED:
            if self.cpu.state == StateCPU.IDLE:
                self.handleIdleState()
            elif self.cpu.state == StateCPU.EXECUTING:
                self.handleExecutingState()
            elif self.cpu.state == StateCPU.IO_WAIT:
                self.handleIoWaitState()
                
        currentState = self.cpu.state.value
        if currentState in self.cpuStateCounts:
            self.cpuStateCounts[currentState] += 1

    #проверка перегрузки системы
    def checkOverload(self):
        currentUsedBlocks = sum(1 for block in self.memoryBlocks if block is not None)
    
        if currentUsedBlocks > self.maxBlocksCount:
            if self.cpu.state != StateCPU.OVERLOADED:
                self.changeCpuState(StateCPU.OVERLOADED, 
                                f"(перегрузка памяти: {currentUsedBlocks} > {self.maxBlocksCount} разделов)")
        else:
            if self.cpu.state == StateCPU.OVERLOADED:
                self.changeToNormalState()

    #возвращение процессора в нормальное состояние
    def changeToNormalState(self):
        mathTasks = [task for task in self.runningTasks if task.type == TypeTask.MATH and task.state == StateTask.RUN]
        ioTasks = [task for task in self.runningTasks if task.type == TypeTask.INOUT and task.state == StateTask.RUN]
        
        if mathTasks:
            self.changeCpuState(StateCPU.EXECUTING, "(система восстановилась, есть MATH задачи)")
        elif ioTasks:
            self.changeCpuState(StateCPU.IO_WAIT, "(система восстановилась, есть INOUT задачи)")
        else:
            self.changeCpuState(StateCPU.IDLE, "(система восстановилась, нет активных задач)")

    #обработка состояния простоя
    def handleIdleState(self):
        self.checkOverload()
        if self.cpu.state == StateCPU.OVERLOADED:
            return
        
        mathTasks = [task for task in self.runningTasks if task.type == TypeTask.MATH and task.state == StateTask.RUN]
        ioTasks = [task for task in self.runningTasks if task.type == TypeTask.INOUT and task.state == StateTask.RUN]
        
        if mathTasks:
            self.changeCpuState(StateCPU.EXECUTING, f"(найдены {len(mathTasks)} активных MATH задач)")
        elif ioTasks:
            self.changeCpuState(StateCPU.IO_WAIT, f"(найдены {len(ioTasks)} активных INOUT задач)")

    #обработка состояния выполнения вычислений
    def handleExecutingState(self):
        self.checkOverload()
        if self.cpu.state == StateCPU.OVERLOADED:
            return
        
        mathTasks = [task for task in self.runningTasks if task.type == TypeTask.MATH and task.state == StateTask.RUN]
        ioTasks = [task for task in self.runningTasks if task.type == TypeTask.INOUT and task.state == StateTask.RUN]
        
        if not mathTasks and ioTasks:
            self.changeCpuState(StateCPU.IO_WAIT, "(MATH задачи завершены, есть активные INOUT)")
        elif not mathTasks and not ioTasks:
            self.changeCpuState(StateCPU.IDLE, "(все активные задачи завершены)")

    #обработка состояния выполнения ввода/вывода
    def handleIoWaitState(self):
        self.checkOverload()
        if self.cpu.state == StateCPU.OVERLOADED:
            return
        
        ioTasks = [task for task in self.runningTasks if task.type == TypeTask.INOUT and task.state == StateTask.RUN]
        mathTasks = [task for task in self.runningTasks if task.type == TypeTask.MATH and task.state == StateTask.RUN]
        
        if not ioTasks and mathTasks:
            self.changeCpuState(StateCPU.EXECUTING, "(INOUT задачи завершены, есть активные MATH)")
        elif not ioTasks and not mathTasks:
            self.changeCpuState(StateCPU.IDLE, "(все активные задачи завершены)")
    
    #освобождение разделов памяти
    def freeCompletedTasks(self) -> bool:
        freed = False
        for i, task in enumerate(self.memoryBlocks):
            if task and task.state == StateTask.READY:
                self.output(f"Задача {task.num} завершена, освобождается раздел {i+1}")
                self.memoryBlocks[i] = None
                if task in self.runningTasks:
                    self.runningTasks.remove(task)
                if task in self.ioWaitTasks:
                    self.ioWaitTasks.remove(task)
                self.readyQueue.append(task)
                freed = True
        return freed
    
    #выполнение задачи в разделе памяти (старый метод, оставляем для совместимости)
    def executeTasks(self):
        for i, task in enumerate(self.memoryBlocks):
            if task and task.state == StateTask.WAIT:
                self.cpu.useToDoTask(task)
                self.output(f"Начато выполнение задачи {task.num} ({task.type.value}) в разделе {i+1}")
                
                if task.type == TypeTask.INOUT:
                    self.ioWaitTasks.append(task)
                
                self.runningTasks.append(task)
            
            elif task and task.state == StateTask.RUN:
                completed = task.execute()
                self.output(f"Задача {task.num} ({task.type.value}) выполняется: {task.executionTime}/{task.requiredTime} тактов")
                
                if completed:
                    self.output(f"Задача {task.num} ({task.type.value}) завершена!")
                    if task in self.ioWaitTasks:
                        self.ioWaitTasks.remove(task)
    
    #сброс состояния ОС к начальному (для перезапуска программы)
    def reset(self):
        if self.packet:
            self.waitQueue = self.packet.tasks.copy()
        else:
            self.waitQueue = []
        
        self.readyQueue = []
        self.runningTasks = []
        self.ioWaitTasks = []
        
        self.memoryBlocks = [None] * self.maxBlocksCount
        
        self.cpu.state = StateCPU.IDLE
        self.cpu.currentTask = None
        
        self.currentTact = 0
        
        self.history = {
            'tacts': [],
            'memoryBlocksUsed': [],
            'cpuStates': [],
            'taskStates': {'WAIT': [], 'RUN': [], 'READY': []},
            'memoryUsage': [],
            'taskTypes': {
                'MATH': self.packet.getMathTasks() if self.packet else 0,
                'INOUT': self.packet.getInOutTasks() if self.packet else 0
            },
            'rrQueueLength': []
        }
        
        self.cpuStateCounts = {
            "ПРОСТОЙ": 0,
            "ВЫПОЛНЕНИЕ ВЫЧИСЛЕНИЙ": 0,
            "ОЖИДАНИЕ ЗАВЕРШЕНИЯ ВВОДА/ВЫВОДА": 0,
            "ПЕРЕГРУЗКА": 0
        }
        
        self.rrStatistics = {
            'contextSwitches': 0,
            'quantumExhaustions': 0,
            'tasksCompletedInQuantum': 0,
            'rrQueueLengthHistory': [],
            'quantumEfficiency': []
        }
        
        if self.packet:
            for task in self.packet.tasks:
                task.state = StateTask.WAIT
                task.executionTime = 0
                task.remainingQuantum = 0
                task.contextSwitches = 0
        
        self.output("Система сброшена в начальное состояние")
    
    #проверка условий завершения симуляции
    def isSimulationComplete(self) -> bool:
        return (
            len(self.waitQueue) == 0 and 
            len(self.runningTasks) == 0 and 
            len(self.ioWaitTasks) == 0 and
            all(task is None or task.state.value == "ВЫПОЛНЕНА" for task in self.memoryBlocks)
        )