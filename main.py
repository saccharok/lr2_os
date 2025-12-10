#главное окно
import sys
import random
import json
import os

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QSpinBox, QMessageBox,
                             QLineEdit, QPushButton, QPlainTextEdit, QFileDialog, 
                             QDialog, QVBoxLayout, QHBoxLayout, QWidget, QComboBox, QGridLayout)
from PyQt6.QtGui import QKeyEvent, QPainter, QColor, QPen

from simulation import Simulation, Packet
from statisticsInfo import Statistics

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LR1 Zemskaya")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        headertext = "color: #3333FF; " \
                    "font-size: 25px; " \
                    "font-family: 'Century Gothic'; "
        maintext = "color: #000000; " \
                    "font-size: 15px; " \
                    "font-family: 'Century Gothic'; "
        btntext = "color: #3333FF; " \
                    "font-size: 15px; " \
                    "font-family: 'Century Gothic'; " \
                    "background-color: #FFFFFF; "
        text = "color: #3333FF; " \
                    "font-size: 15px; " \
                    "font-family: 'Century Gothic'; "
        
        self.mainlabel = QLabel('МОДЕЛИРОВАНИЕ РАБОТЫ\n' \
        'ОПЕРАЦИОННОЙ СИСТЕМЫ\n' \
        'РАБОТАЮЩЕЙ В ПАКЕТНОМ РЕЖИМЕ\n' \
        'С ИСПОЛЬЗОВАНИЕМ TIMESHARING\n' \
        'И АЛГОРИТМА ROUND ROBIN', self)
        self.mainlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainlabel.setStyleSheet(headertext+"font-weight: bold;")


        self.propertylabel = QLabel('Параметры системы', self)
        self.propertylabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.propertylabel.setStyleSheet(headertext)

        self.blocksvalue = QSpinBox(self)
        self.blocksvalue.setValue(1)
        self.blocksvalue.setMinimum(1)
        self.blocksvalue.setMaximum(64)
        self.blocksvalue.setStyleSheet(maintext)
        self.blockslabel = QLabel('Максимальное количество разделов', self)
        self.blockslabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.blockslabel.setStyleSheet(maintext)

        self.tactsvalue = QSpinBox(self)
        self.tactsvalue.setValue(1)
        self.tactsvalue.setMinimum(1)
        self.tactsvalue.setMaximum(1000)
        self.tactsvalue.setStyleSheet(maintext)
        self.tactslabel = QLabel('Максимальное количество тактов (циклов)', self)
        self.tactslabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tactslabel.setStyleSheet(maintext)

        self.ramvalue = QSpinBox(self)
        self.ramvalue.setValue(1)
        self.ramvalue.setMinimum(1)
        self.ramvalue.setMaximum(128)
        self.ramvalue.setStyleSheet(maintext)
        self.ramlabel = QLabel('RAM (ОП) в ГБ', self)
        self.ramlabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.ramlabel.setStyleSheet(maintext)

        self.packlabel = QLabel('Текущий пакет:', self)
        self.packlabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.packlabel.setStyleSheet(maintext)
        self.filename = 'equals_little_pack.json'
        self.packname = QLineEdit(self.filename, self)
        self.packname.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.packname.setReadOnly(True)
        self.packname.setStyleSheet(maintext)
        
        self.typepacklabel = QLabel('Тип текущего пакетa:', self)
        self.typepacklabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.typepacklabel.setStyleSheet(maintext)
        
        self.typelabel = QLabel('', self)
        self.typelabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.typelabel.setStyleSheet(text)
        
        self.mathtasklabel = QLabel('Количество математических задач:', self)
        self.mathtasklabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.mathtasklabel.setStyleSheet(maintext)
        
        self.mathcountlabel = QLabel('', self)
        self.mathcountlabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.mathcountlabel.setStyleSheet(text)
        
        self.inouttasklabel = QLabel('Количество задач ввода/вывода:', self)
        self.inouttasklabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.inouttasklabel.setStyleSheet(maintext)
        
        self.intoutcountlabel = QLabel('', self)
        self.intoutcountlabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.intoutcountlabel.setStyleSheet(text)

        self.changepackbutton = QPushButton("Выбрать другой пакет",self)
        self.changepackbutton.setStyleSheet(btntext)
        self.changepackbutton.clicked.connect(self.changePacket)

        self.newpackbutton = QPushButton("Создать новый пакет",self)
        self.newpackbutton.setStyleSheet(btntext)
        self.newpackbutton.clicked.connect(self.createPacket)

        self.startbutton = QPushButton("СТАРТ СИМУЛЯЦИИ",self)
        self.startbutton.setStyleSheet(btntext)
        self.startbutton.clicked.connect(self.startSimulation)

        self.infolabel = QLabel('Для выхода из программы нажмите клавижу ESC', self)
        self.infolabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.infolabel.setStyleSheet(maintext)
        
        self.datatext = QPlainTextEdit('', self)
        self.datatext.setStyleSheet(maintext + "background-color: #D9D9D9; ")
        self.datatext.setReadOnly(True)

        self.quantumlabel = QLabel('Размер кванта времени (тактов)', self)
        self.quantumlabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.quantumlabel.setStyleSheet(maintext)
        
        self.quantumvalue = QSpinBox(self)
        self.quantumvalue.setValue(1)
        self.quantumvalue.setMinimum(1)
        self.quantumvalue.setMaximum(10)

        self.topGraphsContainer = QWidget(self)
        self.topGraphsContainer.setStyleSheet("background-color: #FFFFFF; border: 1px solid #3333FF;")
        self.topGraphsLayout = QGridLayout(self.topGraphsContainer)
        self.topGraphsLayout.setSpacing(5)
        self.topGraphsLayout.setContentsMargins(5, 5, 5, 5)
        
        self.bottomGraphsContainer = QWidget(self)
        self.bottomGraphsContainer.setStyleSheet("background-color: #FFFFFF; border: 1px solid #3333FF;")
        self.bottomGraphsLayout = QGridLayout(self.bottomGraphsContainer)
        self.bottomGraphsLayout.setSpacing(5)
        self.bottomGraphsLayout.setContentsMargins(5, 5, 5, 5)
        
        self.topGraphWidgets = []
        self.bottomGraphWidgets = []
        
        for i in range(3):
            topWidget = QLabel(f"График {i+1}\n(запустите симуляцию)")
            topWidget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            topWidget.setStyleSheet("background-color: #F0F0F0; border: 1px solid #CCCCCC; color: #666666; font-size: 12px;")
            topWidget.setMinimumSize(200, 150)
            self.topGraphWidgets.append(topWidget)
            self.topGraphsLayout.addWidget(topWidget, 0, i)
            
            bottomWidget = QLabel(f"График {i+4}\n(запустите симуляцию)")
            bottomWidget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bottomWidget.setStyleSheet("background-color: #F0F0F0; border: 1px solid #CCCCCC; color: #666666; font-size: 12px;")
            bottomWidget.setMinimumSize(200, 150)
            self.bottomGraphWidgets.append(bottomWidget)
            self.bottomGraphsLayout.addWidget(bottomWidget, 0, i)

        self.getPackInfo()
        
        self.statisticsWidget = None
        self.simulation = None
        self.statisticsInitialized = False

        self.showFullScreen()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        width = self.width()
        height = self.height()
        cellWidth = width // 3
        cellHeight = height // 3
        
        leftColumnWidth = 2 * cellWidth
        leftSectionHeight = height // 3
        
        self.datatext.setGeometry(0, 0, leftColumnWidth, leftSectionHeight)
        
        self.topGraphsContainer.setGeometry(0, leftSectionHeight, leftColumnWidth, leftSectionHeight)
        
        self.bottomGraphsContainer.setGeometry(0, 2 * leftSectionHeight, leftColumnWidth, leftSectionHeight)
        
        padding = 50
        
        self.mainlabel.setGeometry(2 * cellWidth, 0, cellWidth, cellHeight)
        
        self.propertylabel.setGeometry(2 * cellWidth, cellHeight - padding, cellWidth, cellHeight)
        
        
        self.quantumlabel.setGeometry(2 * cellWidth + padding * 2, cellHeight, cellWidth, cellHeight - padding)
        self.quantumvalue.setGeometry(2 * cellWidth + 10, cellHeight, 80, 35)
        
        self.blockslabel.setGeometry(2 * cellWidth + padding * 2, cellHeight + padding, cellWidth, cellHeight - padding)
        self.tactslabel.setGeometry(2 * cellWidth + padding * 2, cellHeight + padding * 2, cellWidth, cellHeight - padding * 2)
        self.ramlabel.setGeometry(2 * cellWidth + padding * 2, cellHeight + padding * 3, cellWidth, cellHeight - padding * 3)
        self.packlabel.setGeometry(2 * cellWidth + 10, cellHeight + padding * 4, cellWidth, cellHeight - padding * 4)

        self.blocksvalue.setGeometry(2 * cellWidth + 10, cellHeight + padding - 7, 80, 35)
        self.tactsvalue.setGeometry(2 * cellWidth + 10, cellHeight + padding * 2 - 7, 80, 35)
        self.ramvalue.setGeometry(2 * cellWidth + 10, cellHeight + padding * 3 - 7, 80, 35)
        self.packname.setGeometry(2 * cellWidth + padding * 3, cellHeight + padding * 4 - 7, 325, 35)

        self.changepackbutton.setGeometry(2 * cellWidth + 10, cellHeight + padding * 5 - 7, 195, 35)
        self.newpackbutton.setGeometry(2 * cellWidth + 280, cellHeight + padding * 5 - 7, 195, 35)

        self.typepacklabel.setGeometry(2 * cellWidth + 10, cellHeight + padding * 6 - 7, cellWidth - 20, 30)
        self.typelabel.setGeometry(2 * cellWidth + 300, cellHeight + padding * 6 - 7, cellWidth - 20, 30)

        self.mathtasklabel.setGeometry(2 * cellWidth + 10, cellHeight + padding * 7 - 7, cellWidth - 20, 30)
        self.mathcountlabel.setGeometry(2 * cellWidth + 300, cellHeight + padding * 7 - 7, cellWidth - 20, 30)

        self.inouttasklabel.setGeometry(2 * cellWidth + 10, cellHeight + padding * 8 - 7, cellWidth - 20, 30)
        self.intoutcountlabel.setGeometry(2 * cellWidth + 300, cellHeight + padding * 8 - 13, cellWidth - 20, 30)
        
        self.startbutton.setGeometry(2 * cellWidth + 150, cellHeight + padding * 9 - 7, 195, 45)

        self.infolabel.setGeometry(2*cellWidth, 2*cellHeight + padding * 5, cellWidth, cellHeight)
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        painter.fillRect(self.rect(), QColor("#D9D9D9"))

        pen = QPen(QColor("white"))
        pen.setWidth(3)
        painter.setPen(pen)
        
        height = self.height()
        width = self.width()
        thirdHeight = height // 3
        thirdWidth = width // 3
        
        painter.drawLine(2 * thirdWidth, 0, 2 * thirdWidth, height)
        painter.drawLine(0, thirdHeight, 2 * thirdWidth, thirdHeight)

    def getPackInfo(self):
        file = 'ready_packets/'+ str(self.packname.text())
        self.packet = Packet(file)
        self.typelabel.setText(self.packet.type.value)
        self.mathcountlabel.setText(str(self.packet.getMathTasks()))
        self.intoutcountlabel.setText(str(self.packet.getInOutTasks()))

    def changePacket(self):
        filename, ok = QFileDialog.getOpenFileName(
        self,
        "Выбрать пакет", 
        "ready_packets/", 
        "Packet (*.json)"
        )
        if ok and filename:
            self.packname.setText(filename.split('/')[-1])  
            self.getPackInfo()

    def startSimulation(self):
        try:
            self.datatext.clear()
            
            packetFile = 'ready_packets/' + self.packname.text()
            if not os.path.exists(packetFile):
                QMessageBox.critical(self, "Ошибка", f"Файл пакета не найден: {packetFile}")
                return
            
            try:
                test_packet = Packet(packetFile)
                if not test_packet.tasks:
                    QMessageBox.critical(self, "Ошибка", "Пакет не содержит задач!")
                    return
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки пакета: {str(e)}")
                return
            
            self.simulation = Simulation(
                maxBlocksCount=self.blocksvalue.value(),
                ram=self.ramvalue.value(),
                jsonFile=packetFile,
                maxTacts=self.tactsvalue.value(),
                quantumSize=self.quantumvalue.value()
            )
            
            if self.simulation and self.simulation.os:
                self.simulation.os.setOutputCallback(self.outputCallback)
                self.simulation.start()
                
                QTimer.singleShot(100, self.setupStatisticsAfterSimulation)
                
                self.datatext.appendPlainText(f"Время выполнения симуляции: {self.simulation.getRunTime():.2f} секунд")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось создать симуляцию")
                
        except Exception as e:
            errorMsg = f"Не удалось запустить симуляцию: {str(e)}"
            QMessageBox.critical(self, "Ошибка", errorMsg)
            self.datatext.appendPlainText(f"ОШИБКА: {errorMsg}")
            import traceback
            self.datatext.appendPlainText(f"Трассировка:\n{traceback.format_exc()}")

    def setupStatisticsAfterSimulation(self):
        try:
            if self.simulation:
                self.statisticsWidget = Statistics(self.simulation)
                self.replaceGraphPlaceholders()

                if hasattr(self.statisticsWidget, 'updateCharts'):
                    self.statisticsWidget.updateCharts()
                
                self.statisticsInitialized = True
                
        except Exception as e:
            print(f"Ошибка при создании статистики: {e}")
            import traceback
            traceback.print_exc()
            
            errorLabel = QLabel(f"Ошибка создания графиков: {str(e)}")
            errorLabel.setStyleSheet("color: red;")
            self.datatext.appendPlainText(f"\nОШИБКА: Не удалось создать графики: {e}")

    def outputCallback(self, tactInfo: str):
        self.datatext.appendPlainText(tactInfo)
        cursor = self.datatext.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.datatext.setTextCursor(cursor)
        QApplication.processEvents()

    def replaceGraphPlaceholders(self):
        if not self.statisticsWidget:
            return
        
        for i in reversed(range(self.topGraphsLayout.count())):
            widget = self.topGraphsLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        for i in reversed(range(self.bottomGraphsLayout.count())):
            widget = self.bottomGraphsLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        try:
            graphs = [
                self.statisticsWidget.memoryPlot,
                self.statisticsWidget.cpuPlot,
                self.statisticsWidget.tasksPlot,
                self.statisticsWidget.rrQueuePlot,
                self.statisticsWidget.freeMemPlot,
                self.statisticsWidget.efficiencyPlot
            ]
            
            titles = [
                "Использование памяти",
                "Состояния CPU", 
                "Статусы задач",
                "Очередь Round Robin",
                "Свободная память",
                "Эффективность"
            ]
            
            for i, graph in enumerate(graphs):
                if graph is None:
                    print(f"График {i} не создан!")
                    return
            
            for i, (graph, title) in enumerate(zip(graphs, titles)):
                if i < 3:  
                    container = self.topGraphsContainer
                    layout = self.topGraphsLayout
                else:  
                    container = self.bottomGraphsContainer
                    layout = self.bottomGraphsLayout
                    i = i - 3  
                
                graphContainer = QWidget()
                graphContainer.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px;")
                graphLayout = QVBoxLayout(graphContainer)
                graphLayout.setContentsMargins(5, 5, 5, 5)
                graphLayout.setSpacing(5)
                
                titleLabel = QLabel(title)
                titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                titleLabel.setStyleSheet("font-size: 10pt; font-weight: bold; color: #3333FF; padding: 5px;")
                graphLayout.addWidget(titleLabel)
                
                if graph:
                    graph.setMinimumSize(250, 180)
                    graph.setMaximumSize(250, 180)
                    graph.setParent(graphContainer)
                    graphLayout.addWidget(graph)
                else:
                    errorLabel = QLabel(f"График '{title}' не доступен")
                    errorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    errorLabel.setStyleSheet("color: red;")
                    graphLayout.addWidget(errorLabel)
                
                layout.addWidget(graphContainer, 0, i)
                
            self.topGraphsContainer.update()
            self.bottomGraphsContainer.update()
            
        except Exception as e:
            print(f"Ошибка при создании графиков: {e}")
            import traceback
            traceback.print_exc()    

    def createPacket(self):
        maintext = "color: #000000; " \
                    "font-size: 15px; " \
                    "font-family: 'Century Gothic'; "
        btntext = "color: #3333FF; " \
                    "font-size: 10px; " \
                    "font-family: 'Century Gothic'; " \
                    "background-color: #FFFFFF; "
        dialog = QDialog(self)
        dialog.setWindowTitle("Создание нового пакета")
        dialog.setFixedSize(500, 600)
        screenGeometry = QApplication.primaryScreen().availableGeometry()
        x = (screenGeometry.width() - 500) // 2
        y = (screenGeometry.height() - 600) // 2
        dialog.move(x, y)

        dialog.setStyleSheet("background-color: #D9D9D9;")

        tasksList = []  
        taskCounter = 1  
        
        centralWidget = QWidget()
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(centralWidget)
        
        mainLayout = QVBoxLayout(centralWidget)
        mainLayout.setSpacing(12)
        mainLayout.setContentsMargins(20, 20, 20, 20)
        
        packNameLayout = QHBoxLayout()
        packNameLayout.setContentsMargins(0, 0, 0, 0)
        
        packNameLabel = QLabel('Имя пакета:')
        packNameLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        packNameLabel.setStyleSheet(maintext)
        packNameLabel.setFixedWidth(100)
        
        packNameEdit = QLineEdit()
        packNameEdit.setPlaceholderText("Введите имя пакета")
        packNameEdit.setStyleSheet(maintext)
        packNameEdit.setFixedWidth(200)
        
        packNameLayout.addWidget(packNameLabel)
        packNameLayout.addWidget(packNameEdit)
        packNameLayout.addStretch()
        
        mainLayout.addLayout(packNameLayout)
        
        blocksvalue = QSpinBox()
        blocksvalue.setValue(1)
        blocksvalue.setMinimum(1)
        blocksvalue.setMaximum(1000)
        blocksvalue.setStyleSheet(maintext)
        blocksvalue.setFixedWidth(60)
        
        blockslabel = QLabel('Количество задач:')
        blockslabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        blockslabel.setStyleSheet(maintext)
        
        spinboxLayout = QHBoxLayout()
        spinboxLayout.setContentsMargins(0, 0, 0, 0)
        spinboxLayout.addWidget(blockslabel)
        spinboxLayout.addWidget(blocksvalue)
        spinboxLayout.addStretch()
        
        mainLayout.addLayout(spinboxLayout)
        
        randomLabel = QLabel('Создать пакет рандомно')
        randomLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        randomLabel.setStyleSheet(maintext)
        mainLayout.addWidget(randomLabel)
        
        buttonsRowLayout = QHBoxLayout()
        buttonsRowLayout.setSpacing(8)
        buttonsRowLayout.setContentsMargins(0, 0, 0, 0)
        
        computeButton = QPushButton("ВЫЧИСЛИТЕЛЬНЫЙ")
        computeButton.setStyleSheet(btntext)
        computeButton.setFixedSize(140, 35)
        
        ioButton = QPushButton("ВВОД/ВЫВОД")
        ioButton.setStyleSheet(btntext)
        ioButton.setFixedSize(140, 35)
        
        balancedButton = QPushButton("СБАЛАНСИРОВАННЫЙ")
        balancedButton.setStyleSheet(btntext)
        balancedButton.setFixedSize(140, 35)
        
        equalsButton = QPushButton("РАВНЫЙ ПО КОЛ-ВУ")
        equalsButton.setStyleSheet(btntext)
        equalsButton.setFixedSize(140, 35)
        
        buttonsRowLayout.addWidget(computeButton)
        buttonsRowLayout.addWidget(ioButton)
        buttonsRowLayout.addWidget(balancedButton)
        buttonsRowLayout.addWidget(equalsButton)
        
        mainLayout.addLayout(buttonsRowLayout)
        
        manualLabel = QLabel('Добавить позадачно:')
        manualLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        manualLabel.setStyleSheet(maintext)
        mainLayout.addWidget(manualLabel)
        
        inputContainerLayout = QHBoxLayout()
        inputContainerLayout.setSpacing(15)
        
        leftInputLayout = QVBoxLayout()
        leftInputLayout.setSpacing(12)
        
        taskTypeLayout = QHBoxLayout()
        taskTypeLayout.setContentsMargins(0, 0, 0, 0)
        
        taskTypeLabel = QLabel('Тип задачи:')
        taskTypeLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        taskTypeLabel.setStyleSheet(maintext)
        taskTypeLabel.setFixedWidth(100)
        
        taskTypeCombo = QComboBox()
        taskTypeCombo.addItems(["MATH", "INOUT"])
        taskTypeCombo.setStyleSheet(maintext)
        taskTypeCombo.setFixedWidth(200)
        
        taskTypeLayout.addWidget(taskTypeLabel)
        taskTypeLayout.addWidget(taskTypeCombo)
        taskTypeLayout.addStretch()
        
        leftInputLayout.addLayout(taskTypeLayout)
        
        memoryLayout = QHBoxLayout()
        memoryLayout.setContentsMargins(0, 0, 0, 0)
        
        memoryLabel = QLabel('Память в МБ:')
        memoryLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        memoryLabel.setStyleSheet(maintext)
        memoryLabel.setFixedWidth(100)
        
        memorySpinbox = QSpinBox()
        memorySpinbox.setValue(1)
        memorySpinbox.setMinimum(1)
        memorySpinbox.setMaximum(128 * 1024)
        memorySpinbox.setStyleSheet(maintext)
        memorySpinbox.setFixedWidth(200)
        
        memoryLayout.addWidget(memoryLabel)
        memoryLayout.addWidget(memorySpinbox)
        memoryLayout.addStretch()
        
        leftInputLayout.addLayout(memoryLayout)
        
        addTaskButton = QPushButton("Добавить\nзадачу")
        addTaskButton.setStyleSheet(btntext + "font-size: 12px;")
        addTaskButton.setFixedSize(100, 70)
        
        inputContainerLayout.addLayout(leftInputLayout)
        inputContainerLayout.addWidget(addTaskButton)
        
        mainLayout.addLayout(inputContainerLayout)
        
        tasksText = QPlainTextEdit()
        tasksText.setStyleSheet(maintext + "background-color: #FFFFFF; border: 1px solid #3333FF;")
        tasksText.setFixedHeight(150)
        tasksText.setReadOnly(True)
        
        header = f"{'НОМЕР':<30} {'ТИП':<30} {'ПАМЯТЬ':<30}"
        separator = "-" * 80
        
        tasksText.appendPlainText(header)
        tasksText.appendPlainText(separator)
        
        mainLayout.addWidget(tasksText)

        mainLayout.addStretch()
        
        buttonsLayout = QHBoxLayout()
        buttonsLayout.setSpacing(15)
        buttonsLayout.setContentsMargins(0, 0, 0, 0)
        
        saveButton = QPushButton("Сохранить")
        saveButton.setStyleSheet(btntext)
        saveButton.setFixedSize(100, 35)
        
        cancelButton = QPushButton("Отмена")
        cancelButton.setStyleSheet(btntext)
        cancelButton.setFixedSize(100, 35)
        cancelButton.clicked.connect(dialog.close)
        
        buttonsLayout.addWidget(saveButton)
        buttonsLayout.addWidget(cancelButton)
        
        mainLayout.addLayout(buttonsLayout)
        
        def generateMathPacket():
            nonlocal tasksList, taskCounter
            tasksList.clear()
            tasksText.clear()
            tasksText.appendPlainText(header)
            tasksText.appendPlainText(separator)
            
            numTasks = blocksvalue.value()
            
            mathRatio = random.uniform(0.7, 0.9)
            mathTasks = max(1, int(numTasks * mathRatio))
            ioTasks = numTasks - mathTasks
            
            for i in range(mathTasks):
                taskNum = taskCounter
                taskType = "MATH"
                memory = random.randint(100, 1000)
                
                tasksList.append({
                    "num": taskNum,
                    "type": taskType,
                    "memory": memory
                })
                
                taskLine = f"{taskNum:<30} {taskType:<30} {memory:<30}"
                tasksText.appendPlainText(taskLine)
                taskCounter += 1
                
            for i in range(ioTasks):
                taskNum = taskCounter
                taskType = "INOUT"
                memory = random.randint(50, 500)
                
                tasksList.append({
                    "num": taskNum,
                    "type": taskType,
                    "memory": memory
                })
                
                taskLine = f"{taskNum:<30} {taskType:<30} {memory:<30}"
                tasksText.appendPlainText(taskLine)
                taskCounter += 1

        def generateIOPacket():
            nonlocal tasksList, taskCounter
            tasksList.clear()
            tasksText.clear()
            tasksText.appendPlainText(header)
            tasksText.appendPlainText(separator)
            
            numTasks = blocksvalue.value()
            
            ioRatio = random.uniform(0.7, 0.9)
            ioTasks = max(1, int(numTasks * ioRatio))
            mathTasks = numTasks - ioTasks
            
            for i in range(ioTasks):
                taskNum = taskCounter
                taskType = "INOUT"
                memory = random.randint(50, 500)
                
                tasksList.append({
                    "num": taskNum,
                    "type": taskType,
                    "memory": memory
                })
                
                taskLine = f"{taskNum:<30} {taskType:<30} {memory:<30}"
                tasksText.appendPlainText(taskLine)
                taskCounter += 1
                
            for i in range(mathTasks):
                taskNum = taskCounter
                taskType = "MATH"
                memory = random.randint(100, 1000)
                
                tasksList.append({
                    "num": taskNum,
                    "type": taskType,
                    "memory": memory
                })
                
                taskLine = f"{taskNum:<30} {taskType:<30} {memory:<30}"
                tasksText.appendPlainText(taskLine)
                taskCounter += 1

        def generateBalancedPacket():
            nonlocal tasksList, taskCounter
            tasksList.clear()
            tasksText.clear()
            tasksText.appendPlainText(header)
            tasksText.appendPlainText(separator)
            
            numTasks = blocksvalue.value()

            mathRatio = 2/5  #40% MATH задач
            ioRatio = 3/5    #60% INOUT задач
            
            mathTasks = max(1, int(numTasks * mathRatio))
            ioTasks = max(1, int(numTasks * ioRatio))
            
            totalTasks = mathTasks + ioTasks
            while totalTasks > numTasks:
                if mathTasks > 1:
                    mathTasks -= 1
                    totalTasks -= 1
                elif ioTasks > 1:
                    ioTasks -= 1
                    totalTasks -= 1
                    
            while totalTasks < numTasks:
                ioTasks += 1
                totalTasks += 1
            
            for i in range(mathTasks):
                taskNum = taskCounter
                taskType = "MATH"
                memory = random.randint(100, 1000)
                
                tasksList.append({
                    "num": taskNum,
                    "type": taskType,
                    "memory": memory
                })
                
                taskLine = f"{taskNum:<30} {taskType:<30} {memory:<30}"
                tasksText.appendPlainText(taskLine)
                taskCounter += 1
                
            for i in range(ioTasks):
                taskNum = taskCounter
                taskType = "INOUT"
                memory = random.randint(50, 500)
                
                tasksList.append({
                    "num": taskNum,
                    "type": taskType,
                    "memory": memory
                })
                
                taskLine = f"{taskNum:<30} {taskType:<30} {memory:<30}"
                tasksText.appendPlainText(taskLine)
                taskCounter += 1

        def generateEqualsPacket():
            nonlocal tasksList, taskCounter
            tasksList.clear()
            tasksText.clear()
            tasksText.appendPlainText(header)
            tasksText.appendPlainText(separator)
            
            numTasks = blocksvalue.value()
            
            if numTasks % 2 != 0:
                numTasks = numTasks + 1
                blocksvalue.setValue(numTasks)
            
            mathTasks = numTasks // 2
            ioTasks = numTasks // 2
            
            for i in range(mathTasks):
                taskNum = taskCounter
                taskType = "MATH"
                memory = random.randint(100, 1000)
                
                tasksList.append({
                    "num": taskNum,
                    "type": taskType,
                    "memory": memory
                })
                
                taskLine = f"{taskNum:<30} {taskType:<30} {memory:<30}"
                tasksText.appendPlainText(taskLine)
                taskCounter += 1
                
            for i in range(ioTasks):
                taskNum = taskCounter
                taskType = "INOUT"
                memory = random.randint(50, 500)
                
                tasksList.append({
                    "num": taskNum,
                    "type": taskType,
                    "memory": memory
                })
                
                taskLine = f"{taskNum:<30} {taskType:<30} {memory:<30}"
                tasksText.appendPlainText(taskLine)
                taskCounter += 1

        def addManualTask():
            nonlocal tasksList, taskCounter
            taskType = taskTypeCombo.currentText()
            memory = memorySpinbox.value()
            taskNum = taskCounter
            
            tasksList.append({
                "num": taskNum,
                "type": taskType,
                "memory": memory
            })
            
            taskLine = f"{taskNum:<30} {taskType:<30} {memory:<30}"
            tasksText.appendPlainText(taskLine)
            taskCounter += 1

        def savePacket():
            if not tasksList:
                QMessageBox.warning(dialog, "Ошибка", "Пакет не содержит задач!")
                return
            
            packName = packNameEdit.text().strip()
            if not packName:
                QMessageBox.warning(dialog, "Ошибка", "Введите имя пакета!")
                return
            
            packetData = {
                "tasks": tasksList
            }
            
            filename = f"ready_packets/{packName}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(packetData, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(dialog, "Успех", f"Пакет сохранен в файл: {filename}")
                dialog.close()
                
                self.packname.setText(f"{packName}.json")
                self.getPackInfo()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Ошибка", f"Не удалось сохранить файл: {str(e)}")
                
        computeButton.clicked.connect(generateMathPacket)
        ioButton.clicked.connect(generateIOPacket)
        balancedButton.clicked.connect(generateBalancedPacket)
        equalsButton.clicked.connect(generateEqualsPacket)
        addTaskButton.clicked.connect(addManualTask)
        saveButton.clicked.connect(savePacket)
        
        dialog.exec()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()