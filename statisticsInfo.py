#статистика
import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel)
from PyQt6.QtCore import Qt

class Statistics(QWidget):    
    #конструктор
    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation
        self.initUI()
    
    #сбор данных из истории выполнения ОС
    def collectRealData(self):
        history = self.simulation.os.history.copy()
        
        history['cpuStateCounts'] = self.simulation.os.getCpuStateCounts()
        
        history['rrStatistics'] = self.simulation.os.getRoundRobinStatistics()
        return history
    
    #инициализация визуализации
    def initUI(self):
        mainLayout = QVBoxLayout()
        
        title = QLabel("СТАТИСТИКА РАБОТЫ ОПЕРАЦИОННОЙ СИСТЕМЫ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; margin: 10px; color: #2c3e50;")
        mainLayout.addWidget(title)
        
        self.infoContainer = QWidget()
        self.infoLayout = QVBoxLayout(self.infoContainer)
        mainLayout.addWidget(self.infoContainer)
        
        self.setupGraphs()
        
        graphsContainer = QWidget()
        self.graphsLayout = QGridLayout(graphsContainer)
        self.graphsLayout.setSpacing(10)
        self.graphsLayout.setContentsMargins(10, 10, 10, 10)
        
        graphsInfo = [
            (self.memoryPlot, "Использование разделов памяти", ["Используемые разделы"]),
            (self.cpuPlot, "Распределение состояний процессора", [
                "Красный - ПРОСТОЙ", 
                "Зеленый - ВЫПОЛНЕНИЕ", 
                "Синий - ОЖИДАНИЕ В/В", 
                "Оранжевый - ПЕРЕГРУЗКА"
            ]),
            (self.tasksPlot, "Статусы задач", [
                "ОЖИДАНИЕ", 
                "ВЫПОЛНЕНИЕ", 
                "ВЫПОЛНЕНО"
            ]),
            (self.rrQueuePlot, "Очередь Round Robin", ["Длина очереди"]), 
            (self.freeMemPlot, "Свободная память", ["Свободная память %"]),
            (self.efficiencyPlot, "Эффективность выполнения", ["% завершенных задач"])
        ]
        
        for i, (graph, titleText, legends) in enumerate(graphsInfo):
            row = i // 3
            col = i % 3
            
            graphContainer = QWidget()
            graphContainer.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px;")
            graphLayout = QVBoxLayout(graphContainer)
            graphLayout.setContentsMargins(5, 5, 5, 5)
            graphLayout.setSpacing(5)
            
            titleLabel = QLabel(titleText)
            titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            titleLabel.setStyleSheet("font-size: 10pt; font-weight: bold; color: #3333FF; padding: 5px;")
            graphLayout.addWidget(titleLabel)
            
            if legends:
                legendContainer = QWidget()
                legendLayout = QVBoxLayout(legendContainer)
                legendLayout.setContentsMargins(5, 0, 5, 0)
                legendLayout.setSpacing(2)
                
                for legendText in legends:
                    legendLabel = QLabel(legendText)
                    legendLabel.setStyleSheet("font-size: 8pt; color: #666;")
                    legendLayout.addWidget(legendLabel)
                
                graphLayout.addWidget(legendContainer)
                
            graph.setMinimumSize(300, 180)
            graph.setMaximumSize(300, 180)
            graphLayout.addWidget(graph)
            
            self.graphsLayout.addWidget(graphContainer, row, col)
        
        mainLayout.addWidget(graphsContainer)
        self.setLayout(mainLayout)
        
        self.updateCharts()
    
    #обновление информации о симуляции
    def updateSimulationInfo(self):
        for i in reversed(range(self.infoLayout.count())):
            widget = self.infoLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        history = self.collectRealData()
        
        infoText = f"Всего тактов: {self.simulation.totalTacts} | " \
                   f"Размер кванта: {self.simulation.quantumSize} | " \
                   f"MATH задач: {history['taskTypes']['MATH']} | " \
                   f"INOUT задач: {history['taskTypes']['INOUT']} | " \
                   f"Разделов памяти: {self.simulation.maxBlocksCount}"
        infoLabel = QLabel(infoText)
        infoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        infoLabel.setStyleSheet("font-size: 12pt; color: #666; margin: 5px;")
        self.infoLayout.addWidget(infoLabel)
        
        memoryChanges = self.simulation.getMemoryChanges()
        if len(memoryChanges) > 1:
            changesText = "Изменения памяти: " + " → ".join([change.split(": ")[1].split(" ")[0] for change in memoryChanges])
            changesLabel = QLabel(changesText)
            changesLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            changesLabel.setStyleSheet("font-size: 11pt; color: #2c3e50; margin: 3px; font-style: italic;")
            self.infoLayout.addWidget(changesLabel)
            
        if 'rrStatistics' in history:
            rrStats = history['rrStatistics']
            rrText = f"Round Robin: Переключений: {rrStats['contextSwitches']} | " \
                     f"Исчерпаний кванта: {rrStats['quantumExhaustions']} | " \
                     f"Завершено в кванте: {rrStats['tasksCompletedInQuantum']}"
            rrLabel = QLabel(rrText)
            rrLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            rrLabel.setStyleSheet("font-size: 11pt; color: #ff6b00; margin: 3px;")
            self.infoLayout.addWidget(rrLabel)
    
    #настройка графиков
    def setupGraphs(self):
        self.memoryPlot = pg.PlotWidget()
        self.memoryPlot.setBackground('w')
        self.memoryPlot.setLabel('left', 'Количество разделов')
        self.memoryPlot.setLabel('bottom', 'Такты')
        self.memoryPlot.showGrid(x=True, y=True, alpha=0.3)
        self.memoryPlot.setYRange(0, self.simulation.maxBlocksCount)
        self.memoryCurve = self.memoryPlot.plot(pen=pg.mkPen('b', width=3))
        
        self.cpuPlot = pg.PlotWidget()
        self.cpuPlot.setBackground('w')
        self.cpuPlot.setLabel('left', 'Количество тактов')
        self.cpuPlot.setLabel('bottom', 'Состояния процессора')
        self.cpuPlot.showGrid(x=True, y=True, alpha=0.3)
        
        self.cpuBars = None
            
        self.tasksPlot = pg.PlotWidget()
        self.tasksPlot.setBackground('w')
        self.tasksPlot.setLabel('left', 'Количество задач')
        self.tasksPlot.setLabel('bottom', 'Такты')
        self.tasksPlot.showGrid(x=True, y=True, alpha=0.3)
        
        taskColors = {
            'WAIT': '#ff6b6b',
            'RUN': '#4ecdc4',  
            'READY': '#45b7d1'
        }
        
        self.taskCurves = {}
        for state, color in taskColors.items():
            self.taskCurves[state] = self.tasksPlot.plot(pen=pg.mkPen(color, width=3))
            
        self.rrQueuePlot = pg.PlotWidget()
        self.rrQueuePlot.setBackground('w')
        self.rrQueuePlot.setLabel('left', 'Длина очереди')
        self.rrQueuePlot.setLabel('bottom', 'Такты')
        self.rrQueuePlot.showGrid(x=True, y=True, alpha=0.3)
        self.rrQueueCurve = self.rrQueuePlot.plot(pen=pg.mkPen('orange', width=3))
        
        self.freeMemPlot = pg.PlotWidget()
        self.freeMemPlot.setBackground('w')
        self.freeMemPlot.setLabel('left', 'Проценты')
        self.freeMemPlot.setLabel('bottom', 'Такты')
        self.freeMemPlot.showGrid(x=True, y=True, alpha=0.3)
        self.freeMemPlot.setYRange(0, 100)
        self.freeMemCurve = self.freeMemPlot.plot(pen=pg.mkPen('g', width=3))
        
        self.efficiencyPlot = pg.PlotWidget()
        self.efficiencyPlot.setBackground('w')
        self.efficiencyPlot.setLabel('left', 'Проценты')
        self.efficiencyPlot.setLabel('bottom', 'Такты')
        self.efficiencyPlot.showGrid(x=True, y=True, alpha=0.3)
        self.efficiencyPlot.setYRange(0, 100)
        self.efficiencyCurve = self.efficiencyPlot.plot(pen=pg.mkPen('purple', width=3))
    
    #обновление графиков реальными данными
    def updateCharts(self):
        self.updateSimulationInfo()
        
        history = self.collectRealData()
        
        if not history['tacts']:
            self.showNoDataMessage()
            return
            
        tacts = history['tacts']
        
        try:
            #график 1: использование памяти
            if history['memoryBlocksUsed'] and len(history['memoryBlocksUsed']) == len(tacts):
                self.memoryCurve.setData(tacts, history['memoryBlocksUsed'])
                self.memoryPlot.setYRange(0, self.simulation.maxBlocksCount)
            
            #график 2: состояния CPU
            if 'cpuStateCounts' in history:
                stateCounts = history['cpuStateCounts']
                
                allStates = ["ПРОСТОЙ", "ВЫПОЛНЕНИЕ ВЫЧИСЛЕНИЙ", 
                            "ОЖИДАНИЕ ЗАВЕРШЕНИЯ ВВОДА/ВЫВОДА", "ПЕРЕГРУЗКА"]
                for state in allStates:
                    if state not in stateCounts:
                        stateCounts[state] = 0
                
                states = list(stateCounts.keys())
                counts = list(stateCounts.values())
                
                colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#ffa726']
                
                if self.cpuBars:
                    self.cpuPlot.removeItem(self.cpuBars)
                
                bg = pg.BarGraphItem(x=range(len(states)), height=counts, width=0.6, brushes=colors)
                self.cpuPlot.addItem(bg)
                self.cpuBars = bg
                
                self.cpuPlot.getAxis('bottom').setTicks([[(i, self.getShortStateName(state)) 
                                                        for i, state in enumerate(states)]])
                self.cpuPlot.setXRange(-0.5, len(states) - 0.5)
                
                maxCount = max(counts) if counts else 1
                self.cpuPlot.setYRange(0, maxCount * 1.1)
            
            #график 3: статусы задач 
            for state, curve in self.taskCurves.items():
                if (state in history['taskStates'] and 
                    history['taskStates'][state] and 
                    len(history['taskStates'][state]) == len(tacts)):
                    curve.setData(tacts, history['taskStates'][state])
            
            #график 4: очередь Round Robin
            if ('rrQueueLength' in history and 
                history['rrQueueLength'] and 
                len(history['rrQueueLength']) == len(tacts)):
                self.rrQueueCurve.setData(tacts, history['rrQueueLength'])
                maxQueueLength = max(history['rrQueueLength']) if history['rrQueueLength'] else 1
                self.rrQueuePlot.setYRange(0, maxQueueLength * 1.1)
            elif 'rrQueueLength' in history:
                minLen = min(len(tacts), len(history['rrQueueLength']))
                if minLen > 0:
                    self.rrQueueCurve.setData(tacts[:minLen], history['rrQueueLength'][:minLen])
            
            #график 5: свободная память
            if history['memoryUsage'] and len(history['memoryUsage']) == len(tacts):
                self.freeMemCurve.setData(tacts, history['memoryUsage'])
            
            #график 6: эффективность
            if (history['taskStates']['READY'] and 
                len(history['taskStates']['READY']) == len(tacts)):
                totalTasks = sum(history['taskTypes'].values())
                completedTasks = history['taskStates']['READY']
                if totalTasks > 0:
                    completionRate = [(tasks / totalTasks) * 100 for tasks in completedTasks]
                    self.efficiencyCurve.setData(tacts, completionRate)
            
        except Exception as e:
            print(f"Ошибка при обновлении графиков: {e}")
            print(f"Длины массивов: tacts={len(tacts) if tacts else 0}")
            print(f"memoryBlocksUsed={len(history['memoryBlocksUsed']) if 'memoryBlocksUsed' in history else 'нет'}")
            print(f"rrQueueLength={len(history['rrQueueLength']) if 'rrQueueLength' in history else 'нет'}")
            import traceback
            traceback.print_exc()

    #получение сокращенного названия состояния процессора
    def getShortStateName(self, fullName: str) -> str:
        shortNames = {
            "ПРОСТОЙ": "ПРОСТОЙ",
            "ВЫПОЛНЕНИЕ ВЫЧИСЛЕНИЙ": "ВЫЧИСЛЕНИЯ", 
            "ОЖИДАНИЕ ЗАВЕРШЕНИЯ ВВОДА/ВЫВОДА": "ОЖИДАНИЕ В/В",
            "ПЕРЕГРУЗКА": "ПЕРЕГРУЗКА"
        }
        return shortNames.get(fullName, fullName)
    
    #вывод сообщения об отсутствии данных
    def showNoDataMessage(self):
        for graph in [self.memoryPlot, self.cpuPlot, self.tasksPlot, 
                     self.rrQueuePlot, self.freeMemPlot, self.efficiencyPlot]:
            graph.clear()
            text = pg.TextItem("Нет данных для отображения", color='red', anchor=(0.5, 0.5))
            text.setPos(5, 0)
            graph.addItem(text)
    
    #метод для полного обновления статистики после новой симуляции
    def refreshStatistics(self):
        self.updateCharts()