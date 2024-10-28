from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QLineEdit, QMainWindow, QPushButton, QToolBar

import sys


class Fenetre(QMainWindow):

    def __init__(self):
        super(Fenetre, self).__init__()

        self.creation_interface_utilisateur()


    def creation_interface_utilisateur(self):

        self.barre_outils = QToolBar(self)
        self.addToolBar(self.barre_outils)

        self.bouton_retour = QPushButton(self)
        self.bouton_retour.setEnabled(False)

        self.bouton_retour.setIcon(QIcon(':/qt-project.org/styles/commonstyle/images/left-32.png'))
        self.bouton_retour.clicked.connect(self.methode_retour)
        self.barre_outils.addWidget(self.bouton_retour)

        self.bouton_suivant = QPushButton(self)
        self.bouton_suivant.setEnabled(False)
        self.bouton_suivant.setIcon(QIcon(':/qt-project.org/styles/commonstyle/images/right-32.png'))

        self.bouton_suivant.clicked.connect(self.methode_suivant)
        self.barre_outils.addWidget(self.bouton_suivant)

        self.addresse_url_web = QLineEdit(self)
        self.addresse_url_web.returnPressed.connect(self.chargement_url)
        self.barre_outils.addWidget(self.addresse_url_web)

        self.moteur_web = QWebEngineView(self)
        self.setCentralWidget(self.moteur_web)

        self.moteur_web.page().urlChanged.connect(self.onLoadFinished)

        self.moteur_web.page().titleChanged.connect(self.setWindowTitle)
        self.moteur_web.page().urlChanged.connect(self.methode_changement_adresse)

        self.setGeometry(500, 500, 500, 500)
        self.setWindowTitle('Mon navigateur web')
        self.show()

    def onLoadFinished(self):

        if self.moteur_web.history().canGoBack():
            self.bouton_retour.setEnabled(True)
        else:
            self.bouton_retour.setEnabled(False)

        if self.moteur_web.history().canGoForward():
            self.bouton_suivant.setEnabled(True)
        else:
            self.bouton_suivant.setEnabled(False)


    def chargement_url(self):

        adresse_url = QUrl.fromUserInput(self.addresse_url_web.text())

        if adresse_url.isValid():
            self.moteur_web.load(adresse_url)

    def methode_retour(self):
        self.moteur_web.page().triggerAction(QWebEnginePage.Back)

    def methode_suivant(self):
        self.moteur_web.page().triggerAction(QWebEnginePage.Forward)

    def methode_changement_adresse(self, adresse_url):
        self.addresse_url_web.setText(adresse_url.toString())


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    fenetre = Fenetre()
    sys.exit(app.exec_())