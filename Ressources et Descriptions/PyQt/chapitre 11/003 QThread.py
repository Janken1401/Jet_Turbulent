import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


class RechercheFichiers(qtc.QObject):

    correspondance_ok = qtc.pyqtSignal(str)
    changement_repertoire = qtc.pyqtSignal(str)
    fini = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.termeRecherche = None

    @qtc.pyqtSlot(str)
    def definir_termeRecherche(self, termeRecherche):
        self.termeRecherche = termeRecherche

    @qtc.pyqtSlot()
    def recherche(self):

        print(qtc.QThread.currentThreadId().__int__())

        cheminPath = qtc.QDir.rootPath()
        self.rechercher(self.termeRecherche, cheminPath)
        self.fini.emit()

    def rechercher(self, termeRecherche, cheminPath):
        self.changement_repertoire.emit(cheminPath)
        repertoire = qtc.QDir(cheminPath)
        repertoire.setFilter(
            repertoire.filter() |
            qtc.QDir.NoDotAndDotDot |
            qtc.QDir.NoSymLinks
        )
        for element in repertoire.entryInfoList():
            if termeRecherche in element.filePath():
                print(element.filePath())
                self.correspondance_ok.emit(element.filePath())
            if element.isDir():
                self.rechercher(termeRecherche, element.filePath())


class Formulaire(qtw.QWidget):

    changementTexte = qtc.pyqtSignal(str)
    appuiBouton = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())
        self.texteRecherche = qtw.QLineEdit(
            placeholderText='Chaîne recherchée',
            textChanged=self.changementTexte,
            returnPressed=self.appuiBouton)
        self.layout().addWidget(self.texteRecherche)
        self.resultat = qtw.QListWidget()
        self.layout().addWidget(self.resultat)
        self.appuiBouton.connect(self.resultat.clear)

    def ajoutResultat(self, resultat):
        self.resultat.addItem(resultat)


class Fenetre(qtw.QMainWindow):

    def __init__(self):


        super().__init__()


        formulaire = Formulaire()
        self.setCentralWidget(formulaire)
        self.rf = RechercheFichiers()

        self.threadRecherche = qtc.QThread()
        self.rf.moveToThread(self.threadRecherche)
        self.rf.fini.connect(self.threadRecherche.quit)
        self.threadRecherche.start()

        formulaire.changementTexte.connect(self.rf.definir_termeRecherche)
        formulaire.appuiBouton.connect(self.threadRecherche.start)
        formulaire.appuiBouton.connect(self.rf.recherche)

        self.rf.correspondance_ok.connect(formulaire.ajoutResultat)
        self.rf.fini.connect(self.on_rechercheTermine)
        self.rf.changement_repertoire.connect(self.on_changementRepertoire)
        self.show()

    def on_changementRepertoire(self, chemin):
        self.statusBar().showMessage(f'On cherche actuellement ici : {chemin}')

    def on_rechercheTermine(self):
        self.statusBar().showMessage('Recherche terminée')


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    print(qtc.QThread.currentThreadId().__int__())
    fenetre = Fenetre()
    sys.exit(app.exec())