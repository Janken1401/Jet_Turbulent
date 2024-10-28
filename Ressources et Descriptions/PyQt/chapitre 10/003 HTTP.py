from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import sys


def afficherResultat():
    resultatUTF8 = bytes(resultat.readAll()).decode("utf-8")
    print(resultatUTF8)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    url = QUrl("https://www.editions-eni.fr/")

    requete = QNetworkRequest()
    requete.setUrl(url)
    manager = QNetworkAccessManager()

    resultat = manager.get(requete)
    resultat.finished.connect(afficherResultat)

    sys.exit(app.exec_())