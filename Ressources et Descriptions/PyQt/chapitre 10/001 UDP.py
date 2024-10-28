import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtNetwork as qtn
from PyQt5 import QtCore as qtc


class UDP_messageInterface(qtc.QObject):

    port = 1234
    delimiteur = '||'
    recus = qtc.pyqtSignal(str, str)
    error = qtc.pyqtSignal(str)

    def __init__(self, nom_user):
        super().__init__()
        self.nom_user = nom_user

        self.socket = qtn.QUdpSocket()
        self.socket.bind(qtn.QHostAddress.Any, self.port)
        self.socket.readyRead.connect(self.gestion_paquets)
        self.socket.error.connect(self.on_error)

    def gestion_paquets(self):
        while self.socket.hasPendingDatagrams():
            datagram = self.socket.receiveDatagram()
            # Conversion
            raw_message = bytes(datagram.data()).decode('utf-8')

            if self.delimiteur not in raw_message:
                continue
            nom_user, message = raw_message.split(self.delimiteur, 1)
            self.recus.emit(nom_user, message)

    def on_error(self, socket_error):
        error_index = (qtn.QAbstractSocket
                       .staticMetaObject
                       .indexOfEnumerator('SocketError'))
        error = (qtn.QAbstractSocket
                 .staticMetaObject
                 .enumerator(error_index)
                 .valueToKey(socket_error))
        message = f"On a une erreur => {error}"
        self.error.emit(message)

    def envoi_message(self, message):
        msg_bytes = (
            f'{self.nom_user}{self.delimiteur}{message}'
            ).encode('utf-8')
        self.socket.writeDatagram(
            qtc.QByteArray(msg_bytes),
            qtn.QHostAddress.Broadcast,
            self.port
            )


class Fenetre_Messagerie(qtw.QWidget):

    envoyes = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setLayout(qtw.QGridLayout())
        self.message_contenu = qtw.QTextEdit(readOnly=True)
        self.layout().addWidget(self.message_contenu, 1, 1, 1, 2)
        self.nouveau_message = qtw.QLineEdit()
        self.layout().addWidget(self.nouveau_message, 2, 1)
        self.envoyer_btn = qtw.QPushButton('Envoyer', clicked=self.envoyer)
        self.layout().addWidget(self.envoyer_btn, 2, 2)

    def ecrire_message(self, nom_user, message):
        self.message_contenu.append(f'<b>{nom_user} : </b> {message}<br>')

    def envoyer(self):
        message = self.nouveau_message.text().strip()
        if message:
            self.envoyes.emit(message)
            self.nouveau_message.clear()


class Fenetre(qtw.QMainWindow):

    def __init__(self):
        super().__init__()

        self.cw = Fenetre_Messagerie()
        self.setCentralWidget(self.cw)

        nom_user = qtc.QDir.home().dirName()
        self.interface = UDP_messageInterface(nom_user)
        self.cw.envoyes.connect(self.interface.envoi_message)
        self.interface.recus.connect(self.cw.ecrire_message)

        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = Fenetre()
    sys.exit(app.exec())