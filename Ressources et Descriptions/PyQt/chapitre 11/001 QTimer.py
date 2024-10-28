import sys
from PyQt5.QtWidgets import QVBoxLayout, QPushButton,QApplication, QLabel, QWidget
from PyQt5.QtCore import QTimer,QDateTime

class Fenetre(QWidget):
    def __init__(self,parent=None):
        super(Fenetre, self).__init__(parent)
        self.setWindowTitle('Exemple de la classe QTimer')

        self.label=QLabel('')
        self.boutonDebut=QPushButton('Début')
        self.boutonFin=QPushButton('Fin')

        layout=QVBoxLayout()

        self.chrono=QTimer()
        self.chrono.timeout.connect(self.affichage)

        layout.addWidget(self.label)
        layout.addWidget(self.boutonDebut)
        layout.addWidget(self.boutonFin)

        self.boutonDebut.clicked.connect(self.debut)
        self.boutonFin.clicked.connect(self.fin)

        self.setLayout(layout)

    def affichage(self):
        dateHeure=QDateTime.currentDateTime()
        affich=dateHeure.toString('hh:mm:ss')
        self.label.setText(affich)

    def debut(self):
        self.chrono.start(1000)
        self.boutonDebut.setEnabled(False)
        self.boutonFin.setEnabled(True)

    def fin(self):
        self.chrono.stop()
        self.boutonDebut.setEnabled(True)
        self.boutonFin.setEnabled(False)


if __name__ == '__main__':
    app=QApplication(sys.argv)
    fenetre=Fenetre()
    fenetre.show()
    sys.exit(app.exec_())