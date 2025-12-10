#симуляция
import time
from osys import OS
from packet import Packet
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Simulation:
    maxBlocksCount: int  #начальное количество разделов памяти
    ram: int  #объем оперативной памяти в ГБ
    jsonFile: str  #файл с задачами в формате JSON
    maxTacts: int  #максимальное количество тактов выполнения
    quantumSize: int = 1  #размер кванта времени для Round Robin
    os: Optional[OS] = None  #экземпляр операционной системы
    startTime: float = 0  #время начала симуляции
    endTime: float = 0  #время окончания симуляции
    totalTacts: int = 0  #фактическое количество выполненных тактов
    memoryChanges: list = field(default_factory=list)  #история изменений памяти
    
    #пост-инициализации
    def __post_init__(self):
        self.os = OS(ram=self.ram, maxBlocksCount=self.maxBlocksCount, quantumSize=self.quantumSize)
        self.os.initialize(self.jsonFile)
        self.startTime = time.time()
        self.memoryChanges = [f"Начальное количество: {self.maxBlocksCount} разделов, "
                              f"Квант: {self.quantumSize} тактов"]
    
    #изменения количества разделов в памяти во время выполнения
    def changeMemoryBlocks(self, newCount: int):
        if self.os:
            oldCount = self.maxBlocksCount
            self.os.changeMemoryBlocksCount(newCount)
            self.maxBlocksCount = newCount
            
            changeInfo = f"Такт {self.totalTacts}: {oldCount} → {newCount} разделов"
            self.memoryChanges.append(changeInfo)
    
    #запуск симуляции
    def runSimulation(self):
        self.totalTacts = 0
        
        if self.os.outputCallback:
            self.os.outputCallback("СТАРТ СИМУЛЯЦИИ Round Robin")
            totalMemoryMb = self.os.packet.getTasksMemory()
            totalMemoryGb = totalMemoryMb / 1024
            self.os.outputCallback(f"Суммарно RAM пакета: {totalMemoryGb:.1f} ГБ")
            self.os.outputCallback(f"Всего задач: {self.os.packet.getTasksCount()}")
            self.os.outputCallback(f"MATH задач: {self.os.packet.getMathTasks()}")
            self.os.outputCallback(f"INOUT задач: {self.os.packet.getInOutTasks()}")
            self.os.outputCallback(f"Начальное количество разделов памяти: {self.maxBlocksCount}")
            self.os.outputCallback(f"Размер кванта времени: {self.quantumSize} тактов")
            self.os.outputCallback(f"Тип пакета: {self.os.packet.type.value if self.os.packet.type else 'Не определен'}")
        
        for tact in range(self.maxTacts):
            self.totalTacts = tact + 1
            self.os.runTact()

            if self.isSimOver():
                break

        self.endTime = time.time()
        
        if self.os.outputCallback:
            self.os.outputCallback("\nФИНИШ СИМУЛЯЦИИ")
            self.os.outputCallback(f"Всего выполнено тактов: {self.totalTacts}")
            self.os.outputCallback(f"Финальное количество разделов памяти: {self.maxBlocksCount}")
            
            rrStats = self.os.getRoundRobinStatistics()
            self.os.outputCallback(f"\nСТАТИСТИКА ROUND ROBIN:")
            self.os.outputCallback(f"  Всего переключений контекста: {rrStats['contextSwitches']}")
            self.os.outputCallback(f"  Исчерпаний кванта: {rrStats['quantumExhaustions']}")
            self.os.outputCallback(f"  Задач завершено в пределах кванта: {rrStats['tasksCompletedInQuantum']}")
            
            if rrStats['contextSwitches'] > 0:
                efficiency = (rrStats['tasksCompletedInQuantum'] / rrStats['contextSwitches']) * 100
                self.os.outputCallback(f"  Эффективность использования квантов: {efficiency:.1f}%")
            
            if len(self.memoryChanges) > 1:
                self.os.outputCallback("\nИстория изменений разделов памяти:")
                for change in self.memoryChanges:
                    self.os.outputCallback(f"  {change}")
    
    #проверка условий завершения симуляции
    def isSimOver(self) -> bool:
        return (
            len(self.os.waitQueue) == 0 and 
            len(self.os.runningTasks) == 0 and 
            len(self.os.ioWaitTasks) == 0 and
            all(task is None or task.state.value == "ВЫПОЛНЕНА" for task in self.os.memoryBlocks)
        )
    
    #получить время выполнения симуляции
    def getRunTime(self) -> float:
        return self.endTime - self.startTime
    
    #история изменения разделов памяти
    def getMemoryChanges(self) -> list:
        return self.memoryChanges.copy()
    
    #сброс симуляции к начальному состоянию
    def reset(self):
        if self.os:
            self.os.reset() 
    
        self.startTime = time.time()
        self.endTime = 0
        self.totalTacts = 0
        self.memoryChanges = [f"Начальное количество: {self.maxBlocksCount} разделов, "
                              f"Квант: {self.quantumSize} тактов"]
    
    #запуск симуляции
    def start(self):
        self.runSimulation()