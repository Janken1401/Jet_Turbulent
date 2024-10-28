from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
import time
import sys

def affichageThreadId(texte):
    print(texte + ' ----> Thread Id : ' + str(QtCore.QThread.currentThreadId().__int__()))


class TraitementSecondaire(QtCore.QObject):
    signal = pyqtSignal()

    def __init__(self, parent=None):
        affichageThreadId('class Traitement secondaire : __init__')
        super().__init__(parent)

    def lancerTraitement(self, coef=8):
        affichageThreadId('Traitement secondaire : début')
        for x in range(coef):
            y = x + 1
            time.sleep(0.001)
        affichageThreadId('Traitement secondaire : fin')

        self.signal.emit()


class Fenetre(QtWidgets.QWidget):
    def __init__(self, parent=None):
        affichageThreadId('Fenêtre principale : __init__')
        super().__init__(parent)

        self.traitementSecondaire = TraitementSecondaire()
        self.threadTraitementSecondaire = None

        self.bouton1 = QtWidgets.QPushButton('Démarrer la tâche secondaire dans un thread dédié')
        self.bouton2 = QtWidgets.QPushButton('Démarrer la tâche secondaire dans le thread courant')
        disposition = QtWidgets.QVBoxLayout(self)
        disposition.addWidget(self.bouton1)
        disposition.addWidget(self.bouton2)

        self.traitement()

    def traitement(self):
        affichageThreadId('Fenêtre principale : traitement')

        self.threadTraitementSecondaire = QtCore.QThread()
        self.traitementSecondaire.moveToThread(self.threadTraitementSecondaire)

        self.traitementSecondaire.signal.connect(self.traitementSecondaireFini)
        self.bouton1.clicked.connect(self.traitementSecondaire.lancerTraitement)
        self.bouton2.clicked.connect(self.traitementSecondaireLancement)

        self.threadTraitementSecondaire.start()
        self.show()

    def traitementSecondaireFini(self):
        affichageThreadId('Fenêtre principale : traitement secondaire terminé')

    def traitementSecondaireLancement(self):
        affichageThreadId('Fenêtre principale : lancement traitement secondaire')
        self.traitementSecondaire.lancerTraitement()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    affichageThreadId('Thread principal')

    fenetre = Fenetre()
    sys.exit(app.exec_())