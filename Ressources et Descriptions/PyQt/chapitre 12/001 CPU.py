from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtChart as qt_chart

from collections import deque
import psutil

import sys


class UsageCPU(qt_chart.QChartView):

    nombrePoints = 600
    titreDiagramme = "Utilisation CPU de la machine"

    def __init__(self):
        super().__init__()

        diagramme = qt_chart.QChart(title=self.titreDiagramme)
        self.setChart(diagramme)

        self.spline_series = qt_chart.QSplineSeries(name="Pourcentage (%)")
        diagramme.addSeries(self.spline_series)

        self.jeu_donnees = deque(
            [0] * self.nombrePoints, maxlen=self.nombrePoints)
        self.spline_series.append([
            QPoint(x, y)
            for x, y in enumerate(self.jeu_donnees)
        ])


        axe_des_x = qt_chart.QValueAxis()
        axe_des_x.setRange(0, self.nombrePoints)
        axe_des_x.setLabelsVisible(False)
        axe_des_y = qt_chart.QValueAxis()
        axe_des_y.setRange(0, 100)
        diagramme.setAxisX(axe_des_x, self.spline_series)
        diagramme.setAxisY(axe_des_y, self.spline_series)


        self.setRenderHint(QPainter.Antialiasing)


        self.timer = QTimer(
            interval=250, timeout=self.mise_a_jour_donnees)
        self.timer.start()

    def mise_a_jour_donnees(self):
        usage = psutil.cpu_percent()
        self.jeu_donnees.append(usage)
        new_jeu_donnees = [
            QPoint(x, y)
            for x, y in enumerate(self.jeu_donnees)]
        self.spline_series.replace(new_jeu_donnees)


class Fenetre(QMainWindow):

    def __init__(self):

        super().__init__()

        widget = QTabWidget()
        self.setCentralWidget(widget)
        usage_cpu = UsageCPU()
        widget.addTab(usage_cpu, "CPU (%)")

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    fenetre = Fenetre()
    sys.exit(app.exec())