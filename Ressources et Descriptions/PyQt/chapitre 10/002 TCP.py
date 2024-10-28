import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtNetwork as qtn
from PyQt5 import QtCore as qtc


class ClasseTCP(qtc.QObject):

    port = 1234
    delimiteur = '||'
    recus = qtc.pyqtSignal(str, str)
    error = qtc.pyqtSignal(str)

    def __init__(self, nom_user, cible):
        super().__init__()
        self.nom_user = nom_user
        self.cible = cible

        self.ecouteur = qtn.QTcpServer()
        self.ecouteur.listen(qtn.QHostAddress.Any, self.port)
        self.ecouteur.newConnection.connect(self.on_connection)
        self.ecouteur.acceptError.connect(self.on_error)
        self.connections = []

        self.client_socket = qtn.QTcpSocket()
        self.client_socket.error.connect(self.on_error)

    def on_connection(self):
        connection = self.ecouteur.nextPendingConnection()
        self.connections.append(connection)
        connection.readyRead.connect(self.gestion_paquets_donnees)

    def gestion_paquets_donnees(self):
        for socket in self.connections:
            self.flux_donnees = qtc.QDataStream(socket)
            if not socket.bytesAvailable():
                continue
                
            message_brut = self.flux_donnees.readQString()
            if message_brut and self.delimiteur in message_brut:
                nom_user, message = message_brut.split(self.delimiteur, 1)
                self.recus.emit(nom_user, message)

    def envoyer_message(self, message):

        message_brut = f'{self.nom_user}{self.delimiteur}{message}'
        if self.client_socket.state() != qtn.QAbstractSocket.ConnectedState:
            self.client_socket.connectToHost(self.cible, self.port)
        self.flux_donnees = qtc.QDataStream(self.client_socket)

        self.flux_donnees.writeQString(message_brut)

        self.recus.emit(self.nom_user, message)

    def on_error(self, socket_error):

        erreur_id = (qtn.QAbstractSocket
                       .staticMetaObject
                       .indexOfEnumerator('SocketError'))
        error = (qtn.QAbstractSocket
                 .staticMetaObject
                 .enumerator(erreur_id)
                 .valueToKey(socket_error))
        message = f"Il y a un problème : {error}"
        self.error.emit(message)


class FenetreMessagerie(qtw.QWidget):

    envoi_soumis = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())
        self.widget_message = qtw.QTextEdit(readOnly=True)
        self.layout().addWidget(self.widget_message)
        self.widget_message_entrant = qtw.QLineEdit(returnPressed=self.envoyer)
        self.layout().addWidget(self.widget_message_entrant)
        self.widget_bouton_envoi = qtw.QPushButton('Envoyer', clicked=self.envoyer)
        self.layout().addWidget(self.widget_bouton_envoi)

    def ecrire_message(self, nom_user, message):
        self.widget_message.append(f'<b>{nom_user} : </b> {message}<br />')

    def envoyer(self):
        message = self.widget_message_entrant.text().strip()
        if message:
            self.envoi_soumis.emit(message)
            self.widget_message_entrant.clear()


class Fenetre(qtw.QMainWindow):

    def __init__(self):

        super().__init__()

        nom_user = qtc.QDir.home().dirName()
        self.cw = FenetreMessagerie()
        self.setCentralWidget(self.cw)
        cible, _ = qtw.QInputDialog.getText(
            None, 'Cible',
            "Spécifier l'IP de l'hôte distant (cible)")
        if not cible:
            sys.exit()

        self.interface = ClasseTCP(nom_user, cible)
        self.cw.envoi_soumis.connect(self.interface.envoyer_message)
        self.interface.recus.connect(self.cw.ecrire_message)
        self.interface.error.connect(
            lambda x: qtw.QMessageBox.critical(None, 'Erreur', x))

        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = Fenetre()
    sys.exit(app.exec())