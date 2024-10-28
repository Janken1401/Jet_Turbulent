from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time, sys


class Traitement(QRunnable):

    @pyqtSlot()
    def run(self):
        print("Tâche démarrée")
        time.sleep(10)
        print(QThread.currentThreadId().__int__())
        print("Tâche terminée")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    traitement = Traitement()

    threadpool = QThreadPool()
    threadpool.start(traitement)

    print(QThread.currentThreadId().__int__())

